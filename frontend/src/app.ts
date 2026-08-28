import type {
  Concept,
  Dossier,
  EdgeType,
  EvidenceEdgeKind,
  EvidenceNode,
  EvidenceNodeKind,
  FrontendData,
  LearningConcept,
  Resume,
} from "./contracts.js";
import { edgeTypes } from "./contracts.js";
import {
  button,
  element,
  pretty,
  repositoryLink,
  safeHttps,
  sourceLink,
} from "./dom.js";
import { renderEvidenceGraph } from "./evidence/view.js";
import { renderGraph } from "./graph/view.js";
import { readUrl, writeUrl, type UrlState } from "./url.js";

const SEARCH_RESULT_LIMIT = 24;
const GRAPH_NODE_LIMIT = 300;
type Scope = "global" | "track" | "case" | "focal";
interface State extends UrlState {
  scope: Scope;
  scopeValue: string;
  query: string;
  edgeType: EdgeType | "all";
  capability: string;
  evidenceKind: EvidenceNodeKind | "all";
  evidenceEdge: EvidenceEdgeKind | "all";
}

export function mountKnowledgeExplorer(
  root: HTMLElement,
  data: FrontendData,
): void {
  const byId = new Map(data.graph.nodes.map((node) => [node.id, node]));
  const learningById = new Map(
    data.learningState.concepts.map((item) => [item.id, item]),
  );
  const historyIds = new Set(data.history.dossiers.map((item) => item.id));
  const evidenceById = new Map(
    data.evidenceGraph.nodes.map((node) => [node.id, node]),
  );
  const route = readUrl();
  const concept =
    route.concept && byId.has(route.concept) ? route.concept : null;
  const history =
    route.history && historyIds.has(route.history) ? route.history : null;
  const evidence =
    route.evidence && evidenceById.has(route.evidence) ? route.evidence : null;
  const routeWasSanitized =
    concept !== route.concept ||
    history !== route.history ||
    evidence !== route.evidence;
  const state: State = {
    ...route,
    concept,
    history,
    evidence,
    scope: "global",
    scopeValue: "",
    query: "",
    edgeType: "all",
    capability: "all",
    evidenceKind: "all",
    evidenceEdge: "all",
  };
  root.replaceChildren();
  root.className = "learning-lab";
  const header = element("header", "topbar"),
    brand = element("strong", "brand");
  brand.textContent = "LEARNING LAB · KNOWLEDGE SPACE";
  const search = element("input", "search");
  search.id = "search";
  search.type = "search";
  search.placeholder = "搜索概念 /";
  search.setAttribute("aria-label", "搜索概念");
  const today = button("Today", "control"),
    resume = button("Continue", "control"),
    recall = button(state.recall ? "Reveal" : "Recall", "control");
  recall.id = "recall-toggle";
  recall.setAttribute("aria-pressed", String(state.recall));
  const learningCard = element("div", "learning-card");
  learningCard.append(today, resume, recall);
  header.append(brand, search, learningCard);
  root.append(header);
  const controls = element("nav", "filters");
  controls.setAttribute("aria-label", "知识空间筛选");
  const scope = element("select");
  scope.setAttribute("aria-label", "范围");
  for (const [value, label] of [
    ["global", "全部知识空间"],
    ["focal", "焦点概念"],
    ["track", "按学习轨道"],
    ["case", "按案例实验"],
  ] as const) {
    const option = element("option");
    option.value = value;
    option.textContent = label;
    scope.append(option);
  }
  const scopeValue = element("select");
  scopeValue.setAttribute("aria-label", "范围值");
  const edge = element("select");
  edge.setAttribute("aria-label", "关系类型");
  for (const value of ["all", ...edgeTypes]) {
    const option = element("option");
    option.value = value;
    option.textContent = value === "all" ? "所有关系" : pretty(value);
    edge.append(option);
  }
  const capability = element("select");
  capability.setAttribute("aria-label", "已审阅能力");
  for (const value of [
    "all",
    "unassessed",
    "encountered",
    "familiar",
    "usable",
    "retained",
  ]) {
    const option = element("option");
    option.value = value;
    option.textContent = value === "all" ? "所有已审阅能力" : pretty(value);
    capability.append(option);
  }
  const evidenceKind = element("select"),
    evidenceEdge = element("select");
  evidenceKind.id = "evidence-kind";
  evidenceKind.setAttribute("aria-label", "证据节点类型");
  for (const value of [
    "all",
    "concept",
    "dossier",
    "milestone",
    "source",
  ] as const) {
    const option = element("option");
    option.value = value;
    option.textContent = value === "all" ? "所有证据节点" : pretty(value);
    evidenceKind.append(option);
  }
  evidenceEdge.id = "evidence-edge";
  evidenceEdge.setAttribute("aria-label", "证据关系类型");
  for (const value of [
    "all",
    "about",
    "cites_as_evidence",
    "contained_in",
  ] as const) {
    const option = element("option");
    option.value = value;
    option.textContent = value === "all" ? "所有证据关系" : pretty(value);
    evidenceEdge.append(option);
  }
  const graphMode = button("概念图", "mode active"),
    historyMode = button("历史谱系", "mode"),
    evidenceMode = button("证据网络", "mode");
  graphMode.id = "graph-mode";
  historyMode.id = "history-mode";
  graphMode.setAttribute("aria-pressed", "true");
  historyMode.setAttribute("aria-pressed", "false");
  evidenceMode.id = "evidence-mode";
  evidenceMode.setAttribute("aria-pressed", "false");
  controls.append(
    scope,
    scopeValue,
    edge,
    capability,
    evidenceKind,
    evidenceEdge,
    graphMode,
    historyMode,
    evidenceMode,
  );
  root.append(controls);
  const syncOverlayTop = () => {
    root.style.setProperty(
      "--mobile-overlay-top",
      `${Math.ceil(controls.getBoundingClientRect().bottom + 8)}px`,
    );
  };
  window.addEventListener("resize", syncOverlayTop);
  const results = element("div", "results");
  results.id = "results";
  results.setAttribute("role", "listbox");
  root.append(results);
  const space = element("main", "space");
  space.id = "space";
  space.setAttribute("aria-label", "概念关系图");
  const graphSurface = element("div", "graph-surface");
  const historyOverlay = element("div", "history-overlay");
  historyOverlay.id = "history-overlay";
  historyOverlay.hidden = true;
  space.append(graphSurface, historyOverlay);
  root.append(space);
  const panel = element("aside", "panel");
  panel.id = "panel";
  panel.hidden = true;
  root.append(panel);
  const learning = element("aside", "learning-view");
  learning.id = "learning-view";
  learning.hidden = true;
  root.append(learning);
  const fallback = element("div", "sr-only");
  fallback.id = "concept-list";
  root.append(fallback);
  const evidenceFallback = element("div", "sr-only");
  evidenceFallback.id = "evidence-list";
  root.append(evidenceFallback);

  const candidates = (): Concept[] =>
    data.graph.nodes.filter((node) => {
      if (
        state.capability !== "all" &&
        node.reviewed_capability.state !== state.capability
      )
        return false;
      if (
        state.scope === "focal" &&
        state.concept &&
        node.id !== state.concept &&
        !data.graph.edges.some(
          (item) =>
            (item.source === state.concept && item.target === node.id) ||
            (item.target === state.concept && item.source === node.id),
        )
      )
        return false;
      if (
        state.scope === "track" &&
        state.scopeValue &&
        !node.tracks.includes(state.scopeValue)
      )
        return false;
      if (
        state.scope === "case" &&
        state.scopeValue &&
        !node.case_labs.includes(state.scopeValue)
      )
        return false;
      const haystack =
        `${node.id} ${node.title} ${node.summary} ${node.kind} ${node.tracks.join(" ")}`.toLowerCase();
      return !state.query || haystack.includes(state.query);
    });
  const visibleEdges = () =>
    data.graph.edges.filter(
      (item) => state.edgeType === "all" || item.type === state.edgeType,
    );
  const currentLearning = () =>
    data.learningState.concepts
      .filter((item) => item.next_review && item.next_review <= localToday())
      .sort(
        (a, b) =>
          a.next_review!.localeCompare(b.next_review!) ||
          a.id.localeCompare(b.id),
      );
  const syncHash = () => writeUrl(state);
  const closeLearning = () => {
    state.learning = null;
    learning.hidden = true;
    learning.classList.remove("open");
  };
  const selectConcept = (id: string, replace = true) => {
    closeLearning();
    state.concept = id;
    state.history = null;
    state.evidence = null;
    if (replace) syncHash();
    render();
  };
  const selectEvidence = (id: string, replace = true) => {
    closeLearning();
    state.view = "evidence";
    state.evidence = id;
    state.concept = null;
    state.history = null;
    if (replace) syncHash();
    render();
  };
  const populateScopeValues = () => {
    scopeValue.replaceChildren();
    const values =
      state.scope === "track"
        ? data.graph.tracks.map((id) => [id, pretty(id)] as const)
        : state.scope === "case"
          ? data.graph.case_labs.map((item) => [item.id, item.title] as const)
          : [];
    if (!values.length) {
      const option = element("option");
      option.value = "";
      option.textContent =
        state.scope === "focal" ? "选择一个概念后显示相邻项" : "无额外筛选";
      scopeValue.append(option);
      scopeValue.disabled = true;
      state.scopeValue = "";
      return;
    }
    scopeValue.disabled = false;
    if (!values.some(([value]) => value === state.scopeValue))
      state.scopeValue = values[0]![0];
    for (const [value, label] of values) {
      const option = element("option");
      option.value = value;
      option.textContent = label;
      scopeValue.append(option);
    }
    scopeValue.value = state.scopeValue;
  };
  const renderFallback = () => {
    fallback.replaceChildren(
      ...data.graph.nodes.map((node) => {
        const item = button(
          `${node.title} — 已审阅能力：${pretty(node.reviewed_capability.state)}`,
        );
        item.dataset.accessible = node.id;
        item.onclick = () => selectConcept(node.id);
        return item;
      }),
    );
  };
  const evidenceLabel = (node: EvidenceNode) => {
    if (state.recall && node.kind === "source") return `来源 · ${node.id}`;
    if (state.recall && node.kind === "milestone")
      return `历史断言 · ${node.id}`;
    return node.title ?? node.claim ?? node.id;
  };
  const evidenceCandidates = () =>
    data.evidenceGraph.nodes.filter((node) => {
      if (state.evidenceKind !== "all" && node.kind !== state.evidenceKind)
        return false;
      const citationText = data.evidenceGraph.edges
        .filter((edge) => edge.from === node.id || edge.to === node.id)
        .map((edge) =>
          state.recall ? "" : `${edge.role ?? ""} ${edge.locator ?? ""}`,
        )
        .join(" ");
      const haystack = state.recall
        ? `${node.id} ${node.kind}`.toLowerCase()
        : `${node.id} ${node.kind} ${node.title ?? ""} ${node.claim ?? ""} ${node.summary ?? ""} ${node.publisher ?? ""} ${node.source_kind ?? ""} ${citationText}`.toLowerCase();
      return !state.query || haystack.includes(state.query);
    });
  const evidenceEdges = () =>
    data.evidenceGraph.edges.filter(
      (edge_) =>
        state.evidenceEdge === "all" || edge_.kind === state.evidenceEdge,
    );
  const renderEvidenceFallback = () => {
    evidenceFallback.replaceChildren(
      ...data.evidenceGraph.nodes.map((node) => {
        const item = button(`${evidenceLabel(node)} — ${pretty(node.kind)}`);
        item.dataset.accessibleEvidence = node.id;
        item.onclick = () => selectEvidence(node.id);
        return item;
      }),
      ...data.evidenceGraph.edges.map((edge_) => {
        const occurrence =
          !state.recall && edge_.kind === "cites_as_evidence"
            ? ` — ${pretty(edge_.role ?? "unknown role")} — ${edge_.locator ?? "missing locator"}`
            : "";
        const item = button(
          `${evidenceLabel(evidenceById.get(edge_.from) ?? { id: edge_.from, kind: "milestone" })} — ${pretty(edge_.kind)} — ${evidenceLabel(evidenceById.get(edge_.to) ?? { id: edge_.to, kind: "source" })}${occurrence}`,
        );
        item.dataset.accessibleEvidenceEdge = `${edge_.from}:${edge_.kind}:${edge_.to}`;
        item.onclick = () => selectEvidence(edge_.from);
        return item;
      }),
    );
  };
  const renderEvidenceResults = () => {
    results.replaceChildren();
    if (!state.query) {
      results.hidden = true;
      return;
    }
    results.hidden = false;
    const matched = evidenceCandidates(),
      shown = matched.slice(0, SEARCH_RESULT_LIMIT);
    for (const node of shown) {
      const item = button("", "result");
      item.setAttribute("role", "option");
      const title = element("strong");
      title.textContent = evidenceLabel(node);
      const summary = element("small");
      summary.textContent = state.recall
        ? pretty(node.kind)
        : node.kind === "milestone"
          ? (node.claim ?? node.id)
          : `${pretty(node.kind)} · ${node.publisher ?? node.source_kind ?? ""}`;
      item.append(title, summary);
      item.onclick = () => {
        search.value = "";
        state.query = "";
        selectEvidence(node.id);
      };
      results.append(item);
    }
    if (!shown.length) {
      const empty = element("p", "result-empty");
      empty.textContent = "没有匹配证据。";
      results.append(empty);
    } else if (matched.length > shown.length) {
      const note = element("p", "result-note");
      note.textContent = `仅显示前 ${SEARCH_RESULT_LIMIT} 个结果；全部 ${matched.length} 个证据节点保留在结构化列表中。`;
      results.append(note);
    }
  };
  const evidenceReverseButtons = (edges: typeof data.evidenceGraph.edges) =>
    edges.map((edge_) => {
      const other = edge_.from === state.evidence ? edge_.to : edge_.from;
      const target = evidenceById.get(other);
      const relation = button(
        evidenceLabel(target ?? { id: other, kind: "source" }),
        "relation",
      );
      relation.onclick = () => selectEvidence(other);
      return relation;
    });
  const renderEvidencePanel = () => {
    panel.replaceChildren();
    const node = state.evidence ? evidenceById.get(state.evidence) : undefined;
    panel.hidden = !node || state.view !== "evidence";
    panel.classList.toggle("open", !panel.hidden);
    if (!node || state.view !== "evidence") return;
    const close = button("×", "panel-close");
    close.setAttribute("aria-label", "关闭详情");
    close.onclick = () => {
      state.evidence = null;
      syncHash();
      render();
    };
    const heading = element("h1");
    heading.textContent = evidenceLabel(node);
    const tags = element("p", "tags");
    tags.textContent = `${pretty(node.kind)} · ${node.id}`;
    panel.append(close, heading, tags);
    const attached = data.evidenceGraph.edges.filter(
      (edge_) => edge_.from === node.id || edge_.to === node.id,
    );
    if (node.kind === "source") {
      if (!state.recall) {
        const meta = element("p", "definition");
        meta.textContent = `${node.publisher ?? ""}${node.source_kind ? ` · ${pretty(node.source_kind)}` : ""}`;
        panel.append(meta);
        const direct = safeHttps(node.canonical_url ?? "");
        if (direct) {
          const link = element("a", "canonical");
          link.href = direct;
          link.target = "_blank";
          link.rel = "noopener noreferrer";
          link.textContent = "打开直接 HTTPS 来源 ↗";
          panel.append(link);
        }
      } else {
        const prompt = element("p", "definition");
        prompt.textContent = "这份来源支撑了哪一条历史断言？";
        panel.append(prompt);
      }
      for (const edge_ of attached.filter(
        (item) => item.kind === "cites_as_evidence",
      )) {
        const milestone = evidenceById.get(edge_.from);
        const section = element("section", "section"),
          label = element("h2");
        label.textContent = "引用关系";
        const text = element("p");
        text.textContent = state.recall
          ? "先回忆它支持的断言与边界。"
          : `里程碑日期：${dateLabel(milestone?.date ?? { year: 0 })}\n断言：${milestone?.claim ?? edge_.from}\n角色：${edge_.role ?? ""}\n定位：${edge_.locator ?? ""}\n边界：${(milestone?.boundaries ?? []).join("；")}`;
        const reverse = button(
          state.recall ? "查看关联断言" : "打开断言",
          "relation",
        );
        reverse.onclick = () => selectEvidence(edge_.from);
        section.append(label, text, reverse);
        panel.append(section);
      }
    } else if (node.kind === "milestone") {
      const text = element("p", "definition");
      text.textContent = state.recall
        ? "这条历史断言关联哪些概念、档案与来源？"
        : `${dateLabel(node.date ?? { year: 0 })}\n${node.claim ?? ""}\n${(node.actors ?? []).join("、")}`;
      panel.append(text);
      const subjects = attached.filter((edge_) => edge_.kind === "about");
      const citations = attached.filter(
        (edge_) => edge_.kind === "cites_as_evidence",
      );
      const dossier = attached.filter((edge_) => edge_.kind === "contained_in");
      for (const [label, items] of [
        ["主题", subjects],
        ["证据档案", dossier],
        ["来源", citations],
      ] as const) {
        if (!items.length) continue;
        const section = element("section", "section"),
          sectionHeading = element("h2");
        sectionHeading.textContent = label;
        section.append(sectionHeading, ...evidenceReverseButtons(items));
        panel.append(section);
      }
      if (!state.recall && node.boundaries?.length) {
        const section = element("section", "section"),
          sectionHeading = element("h2");
        sectionHeading.textContent = "证据边界";
        const text_ = element("p");
        text_.textContent = node.boundaries.join("\n");
        section.append(sectionHeading, text_);
        panel.append(section);
      }
    } else {
      if (!state.recall && node.summary) {
        const text = element("p", "definition");
        text.textContent = node.summary;
        panel.append(text);
      }
      const section = element("section", "section"),
        sectionHeading = element("h2");
      sectionHeading.textContent = "反向关联";
      section.append(sectionHeading, ...evidenceReverseButtons(attached));
      panel.append(section);
      if (node.path) {
        const link = element("a", "canonical");
        link.href = repositoryLink(node.path);
        link.textContent =
          node.kind === "dossier" ? "打开证据档案 ↗" : "打开源知识卡 ↗";
        panel.append(link);
      }
    }
  };
  const renderResults = () => {
    results.replaceChildren();
    if (!state.query) {
      results.hidden = true;
      return;
    }
    results.hidden = false;
    const matched = candidates();
    const shown = matched.slice(0, SEARCH_RESULT_LIMIT);
    for (const node of shown) {
      const item = button("", "result");
      item.setAttribute("role", "option");
      const title = element("strong");
      title.textContent = node.title;
      const summary = element("small");
      summary.textContent = node.summary;
      item.append(title, summary);
      item.onclick = () => {
        search.value = "";
        state.query = "";
        selectConcept(node.id);
      };
      results.append(item);
    }
    if (!shown.length) {
      const empty = element("p", "result-empty");
      empty.textContent = "没有匹配概念。";
      results.append(empty);
    } else if (matched.length > shown.length) {
      const note = element("p", "result-note");
      note.textContent = `仅显示前 ${SEARCH_RESULT_LIMIT} 个结果；全部 ${matched.length} 个概念保留在结构化列表中。`;
      results.append(note);
    }
  };
  const relationIds = (node: Concept, type: EdgeType) => {
    const own = node.relationships[type] ?? [];
    if (type === "prerequisites" || type === "enables") return own;
    return [
      ...new Set([
        ...own,
        ...data.graph.edges
          .filter((item) => item.type === type && item.target === node.id)
          .map((item) => item.source),
      ]),
    ].sort();
  };
  const renderPanel = () => {
    panel.replaceChildren();
    const node = state.concept ? byId.get(state.concept) : undefined;
    panel.hidden = !node || state.view === "history";
    panel.classList.toggle("open", !panel.hidden);
    if (!node || state.view === "history") return;
    const close = button("×", "panel-close");
    close.setAttribute("aria-label", "关闭详情");
    close.onclick = () => {
      state.concept = null;
      syncHash();
      render();
    };
    const title = element("h1");
    title.textContent = node.title;
    panel.append(close, title);
    const tags = element("p", "tags");
    tags.textContent = `已审阅能力：${pretty(node.reviewed_capability.state)} · ${pretty(node.kind)} · ${node.tracks.map(pretty).join(" / ")}`;
    panel.append(tags);
    const definition = element("p", "definition");
    definition.textContent = state.recall
      ? "答案已隐藏。先自行回忆，再揭示定义和关联。"
      : node.summary;
    panel.append(definition);
    if (!state.recall)
      for (const type of edgeTypes) {
        const ids = relationIds(node, type);
        if (!ids.length) continue;
        const section = element("section", "section"),
          heading = element("h2");
        heading.textContent = pretty(type);
        section.append(heading);
        for (const id of ids) {
          const target = byId.get(id);
          const relation = button(target?.title ?? id, "relation");
          relation.dataset.target = id;
          relation.onclick = () => selectConcept(id);
          section.append(relation);
        }
        panel.append(section);
      }
    const learningItem = learningById.get(node.id);
    const progress = element("section", "section"),
      progressHeading = element("h2");
    progressHeading.textContent = "会话观察与复习提示";
    const progressText = element("p");
    progressText.textContent = learningItem
      ? `会话观察：${learningItem.capability_state}\n复习提示：${learningItem.next_review ?? "尚未安排"}\n最近结果：${learningItem.latest_outcome ?? "尚无证据"}`
      : "尚无会话观察；从一个有完整背景的学习单元开始。";
    progress.append(progressHeading, progressText);
    panel.append(progress);
    const reviewed = element("section", "section"),
      reviewedHeading = element("h2"),
      reviewedText = element("p");
    reviewedHeading.textContent = "已审阅能力";
    reviewedText.textContent = `状态：${node.reviewed_capability.state}\n演示日期：${node.reviewed_capability.demonstrated_at ?? "尚未审阅"}\n证据会话：${node.reviewed_capability.evidence_sessions.join("、") || "尚无"}`;
    reviewed.append(reviewedHeading, reviewedText);
    if (node.reviewed_capability.effective_record) {
      const link = element("a", "evidence");
      link.href = repositoryLink(node.reviewed_capability.effective_record);
      link.textContent = "打开有效审阅记录";
      reviewed.append(link);
    }
    panel.append(reviewed);
    const legacy = element("p", "legacy-label");
    legacy.textContent = `旧记录文件名标签：${pretty(node.mastery.status)}`;
    panel.append(legacy);
    const terminology = node.extensions?.terminology;
    if (terminology) {
      const section = element("section", "section"),
        heading = element("h2");
      heading.textContent = "术语来源";
      const term = element("p");
      term.textContent = `${terminology.preferred_english_term}\n核查：${terminology.checked_on}`;
      section.append(heading, term);
      for (const source of terminology.sources) {
        const link = sourceLink(source);
        if (link) section.append(link);
      }
      panel.append(section);
    }
    const paths = [...node.lessons, ...node.records];
    if (paths.length) {
      const section = element("section", "section"),
        heading = element("h2");
      heading.textContent = "学习证据";
      section.append(heading);
      for (const path of paths) {
        const link = element("a", "evidence");
        link.href = repositoryLink(path);
        link.textContent = path;
        section.append(link);
      }
      panel.append(section);
    }
    const canonical = element("a", "canonical");
    canonical.href = repositoryLink(node.path);
    canonical.textContent = "打开源知识卡 ↗";
    panel.append(canonical);
  };
  const visibleDossiers = () =>
    data.history.dossiers.filter((dossier) => {
      if (state.concept && !dossier.concepts.includes(state.concept))
        return false;
      if (
        state.scope === "track" &&
        state.scopeValue &&
        !dossier.tracks.includes(state.scopeValue)
      )
        return false;
      if (state.scope === "case" && state.scopeValue) {
        const belongsToCase = dossier.concepts.some((id) =>
          byId.get(id)?.case_labs.includes(state.scopeValue),
        );
        if (!belongsToCase) return false;
      }
      const haystack =
        `${dossier.id} ${dossier.title} ${dossier.summary} ${dossier.tracks.join(" ")} ${dossier.lessons.join(" ")}`.toLowerCase();
      return !state.query || haystack.includes(state.query);
    });
  const renderHistory = () => {
    historyOverlay.replaceChildren();
    historyOverlay.hidden = false;
    const article = element("article", "timeline");
    const selected = state.history
      ? data.history.dossiers.find((item) => item.id === state.history)
      : undefined;
    if (!selected) {
      const heading = element("h1");
      heading.textContent = state.concept
        ? `${byId.get(state.concept)?.title ?? state.concept} 的历史谱系`
        : "历史谱系";
      article.append(heading);
      const dossiers = visibleDossiers();
      if (!dossiers.length) {
        const empty = element("p");
        empty.textContent = "尚无可核查的历史谱系。这里不会补写推测性故事。";
        article.append(empty);
      }
      for (const dossier of dossiers) {
        const item = button(dossier.title, "relation");
        item.dataset.historyId = dossier.id;
        const detail = element("small");
        detail.textContent = dossier.summary;
        item.append(detail);
        item.onclick = () => {
          state.history = dossier.id;
          syncHash();
          render();
        };
        article.append(item);
      }
    } else {
      const back = button("← 全部历史", "relation");
      back.onclick = () => {
        state.history = null;
        syncHash();
        render();
      };
      const heading = element("h1");
      heading.textContent = state.recall ? "先从证据问题开始" : selected.title;
      article.append(back, heading);
      const summary = element("p");
      summary.textContent = selected.summary;
      article.append(summary);
      if (selected.lessons.length) {
        const lessons = element("section", "section"),
          lessonHeading = element("h2");
        lessonHeading.textContent = "关联课程";
        lessons.append(lessonHeading);
        for (const path of selected.lessons) {
          const lesson = element("a", "evidence");
          lesson.href = repositoryLink(path);
          lesson.textContent = path;
          lessons.append(lesson);
        }
        article.append(lessons);
      }
      for (const milestone of [...selected.milestones].sort(
        compareMilestones,
      )) {
        const section = element("section", "timeline-item"),
          date = element("div", "timeline-date");
        date.textContent = dateLabel(milestone);
        const kind = element("strong");
        kind.textContent = pretty(milestone.kind);
        const actors = element("small", "actors");
        actors.textContent = (milestone.actors ?? []).join("、");
        const claim = element("p");
        claim.textContent = state.recall
          ? "这条记录解决、形式化或批评了什么？"
          : milestone.claim;
        section.append(date, kind);
        if (actors.textContent) section.append(actors);
        section.append(claim);
        for (const source of milestone.sources ?? []) {
          const link = sourceLink(source);
          if (link) section.append(link);
        }
        article.append(section);
      }
      const link = element("a", "canonical");
      link.href = repositoryLink(selected.path);
      link.textContent = "打开证据档案 ↗";
      article.append(link);
    }
    historyOverlay.append(article);
  };
  const renderLearning = (kind: "today" | "continue") => {
    state.learning = kind;
    syncHash();
    learning.hidden = false;
    learning.classList.add("open");
    learning.replaceChildren();
    const heading = element("h1");
    heading.textContent = kind === "today" ? "复习提示" : "继续上次学习";
    learning.append(heading);
    const entries: LearningConcept[] =
      kind === "today" ? currentLearning() : [];
    const resumeCue: Resume | null =
      kind === "continue" ? (data.learningState.resume ?? null) : null;
    if (!entries.length && !resumeCue) {
      const empty = element("p");
      empty.textContent =
        kind === "today"
          ? "今天没有复习提示。可以继续上次学习。"
          : "还没有可恢复的会话。选择一个主题，从整体背景开始。";
      learning.append(empty);
    }
    for (const item of entries) {
      const node = byId.get(item.id),
        choice = button(node?.title ?? item.id, "learning-item");
      const meta = element("small");
      meta.textContent = `复习提示：${item.next_review} · 会话观察：${item.capability_state}`;
      choice.append(meta);
      choice.onclick = () => {
        learning.hidden = true;
        selectConcept(item.id);
      };
      learning.append(choice);
    }
    if (resumeCue) {
      const choice = button("继续学习单元", "learning-item");
      const meta = element("small");
      meta.textContent = `${resumeCue.unit_kind} · ${resumeCue.unit_ref}\n检查点：${resumeCue.checkpoint ?? "无"}\n${resumeCue.summary}`;
      choice.append(meta);
      choice.onclick = () => {
        learning.hidden = true;
        if (resumeCue.unit_kind === "concept" && byId.has(resumeCue.unit_ref)) {
          selectConcept(resumeCue.unit_ref);
          return;
        }
        const path =
          resumeCue.unit_kind === "lesson"
            ? resumeCue.unit_ref
            : `tracks/${resumeCue.unit_ref}/CURRICULUM.md`;
        window.location.assign(repositoryLink(path));
      };
      learning.append(choice);
    }
  };
  const render = () => {
    renderEvidenceFallback();
    populateScopeValues();
    scope.value = state.scope;
    edge.value = state.edgeType;
    capability.value = state.capability;
    graphMode.classList.toggle("active", state.view === "graph");
    historyMode.classList.toggle("active", state.view === "history");
    evidenceMode.classList.toggle("active", state.view === "evidence");
    graphMode.setAttribute("aria-pressed", String(state.view === "graph"));
    historyMode.setAttribute("aria-pressed", String(state.view === "history"));
    evidenceMode.setAttribute(
      "aria-pressed",
      String(state.view === "evidence"),
    );
    const evidenceView = state.view === "evidence";
    scope.hidden = evidenceView;
    scopeValue.hidden = evidenceView;
    edge.hidden = evidenceView;
    capability.hidden = evidenceView;
    evidenceKind.hidden = !evidenceView;
    evidenceEdge.hidden = !evidenceView;
    syncOverlayTop();
    search.placeholder = evidenceView ? "搜索证据 /" : "搜索概念 /";
    search.setAttribute("aria-label", evidenceView ? "搜索证据" : "搜索概念");
    if (evidenceView) renderEvidenceResults();
    else renderResults();
    if (evidenceView) renderEvidencePanel();
    else renderPanel();
    if (state.view === "history") renderHistory();
    else if (evidenceView) {
      historyOverlay.hidden = true;
      const matched = evidenceCandidates();
      const graphNodes = matched.slice(0, GRAPH_NODE_LIMIT);
      if (
        state.evidence &&
        !graphNodes.some((node) => node.id === state.evidence)
      ) {
        const selected = evidenceById.get(state.evidence);
        if (selected) graphNodes.splice(-1, 1, selected);
      }
      renderEvidenceGraph(graphSurface, {
        nodes: graphNodes,
        edges: evidenceEdges(),
        selected: state.evidence,
        recall: state.recall,
        onSelect: selectEvidence,
      });
      if (matched.length > graphNodes.length) {
        const note = element("p", "graph-limit");
        note.textContent = `证据网络显示前 ${GRAPH_NODE_LIMIT} 个匹配节点；全部 ${matched.length} 个节点保留在结构化列表中。请继续筛选以缩小视图。`;
        graphSurface.append(note);
      }
    } else {
      historyOverlay.hidden = true;
      graphSurface.style.removeProperty("height");
      graphSurface.style.removeProperty("bottom");
      const matched = candidates();
      const graphNodes = matched.slice(0, GRAPH_NODE_LIMIT);
      if (
        state.concept &&
        !graphNodes.some((node) => node.id === state.concept)
      ) {
        const selected = byId.get(state.concept);
        if (selected) graphNodes.splice(-1, 1, selected);
      }
      renderGraph(graphSurface, {
        nodes: graphNodes,
        edges: visibleEdges(),
        selected: state.concept,
        recall: state.recall,
        onSelect: selectConcept,
      });
      if (matched.length > graphNodes.length) {
        const note = element("p", "graph-limit");
        note.textContent = `关系图显示前 ${GRAPH_NODE_LIMIT} 个匹配概念；全部 ${matched.length} 个概念保留在结构化列表中。请继续筛选以缩小视图。`;
        graphSurface.append(note);
      }
    }
  };
  let pendingSearchRender: number | null = null;
  search.oninput = () => {
    state.query = search.value.trim().toLowerCase();
    if (state.view === "evidence") renderEvidenceResults();
    else renderResults();
    if (pendingSearchRender !== null) cancelAnimationFrame(pendingSearchRender);
    pendingSearchRender = requestAnimationFrame(() => {
      pendingSearchRender = null;
      render();
    });
  };
  scope.onchange = () => {
    state.scope = scope.value as Scope;
    render();
  };
  scopeValue.onchange = () => {
    state.scopeValue = scopeValue.value;
    render();
  };
  edge.onchange = () => {
    state.edgeType = edge.value as EdgeType | "all";
    render();
  };
  capability.onchange = () => {
    state.capability = capability.value;
    render();
  };
  evidenceKind.onchange = () => {
    state.evidenceKind = evidenceKind.value as EvidenceNodeKind | "all";
    render();
  };
  evidenceEdge.onchange = () => {
    state.evidenceEdge = evidenceEdge.value as EvidenceEdgeKind | "all";
    render();
  };
  graphMode.onclick = () => {
    closeLearning();
    state.view = "graph";
    state.history = null;
    state.evidence = null;
    syncHash();
    render();
  };
  historyMode.onclick = () => {
    closeLearning();
    state.view = "history";
    state.evidence = null;
    syncHash();
    render();
  };
  evidenceMode.onclick = () => {
    closeLearning();
    state.view = "evidence";
    state.concept = null;
    state.history = null;
    syncHash();
    render();
  };
  today.onclick = () => renderLearning("today");
  resume.onclick = () => renderLearning("continue");
  recall.onclick = () => {
    state.recall = !state.recall;
    recall.textContent = state.recall ? "Reveal" : "Recall";
    recall.setAttribute("aria-pressed", String(state.recall));
    syncHash();
    render();
  };
  document.addEventListener("keydown", (event) => {
    if (event.key === "/" && document.activeElement !== search) {
      event.preventDefault();
      search.focus();
    }
    if (event.key === "Escape") {
      state.concept = null;
      state.evidence = null;
      closeLearning();
      syncHash();
      render();
    }
  });
  renderFallback();
  renderEvidenceFallback();
  if (routeWasSanitized) syncHash();
  if (state.learning) renderLearning(state.learning);
  render();
}
function localToday(): string {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}
function dateLabel(item: {
  year: number;
  month?: number | null;
  day?: number | null;
}): string {
  return `${item.year}${item.month ? `-${String(item.month).padStart(2, "0")}` : ""}${item.day ? `-${String(item.day).padStart(2, "0")}` : ""}`;
}
function compareMilestones(
  a: { year: number; month?: number | null; day?: number | null; id: string },
  b: typeof a,
): number {
  return (
    a.year - b.year ||
    (a.month ?? 0) - (b.month ?? 0) ||
    (a.day ?? 0) - (b.day ?? 0) ||
    a.id.localeCompare(b.id)
  );
}

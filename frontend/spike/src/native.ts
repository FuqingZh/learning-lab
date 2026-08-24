import "./style.css";
import { fixture, relations } from "./fixtures.js";
import type { Fixture, Node, Relation } from "./contracts.js";

declare const __SPIKE_CANDIDATE__: string;
const config = (window as Window & { __SPIKE_CONFIG__?: { fixture: string } })
  .__SPIKE_CONFIG__ ?? { fixture: "current" };
const data = fixture(config.fixture);
const byId = new Map(data.nodes.map((node) => [node.id, node]));
let selected = data.nodes[0]?.id ?? "";

function ranks(input: Fixture): Map<string, number> {
  const result = new Map(input.nodes.map((node) => [node.id, 0]));
  for (let round = 0; round < input.nodes.length; round += 1) {
    for (const node of input.nodes)
      for (const prior of node.relationships.prerequisites ?? [])
        result.set(
          node.id,
          Math.max(result.get(node.id) ?? 0, (result.get(prior) ?? 0) + 1),
        );
  }
  return result;
}
function button(
  label: string,
  callback: () => void,
  className = "",
): HTMLButtonElement {
  const item = document.createElement("button");
  item.type = "button";
  item.textContent = label;
  item.className = className;
  item.onclick = callback;
  return item;
}
function render(): void {
  const root = document.querySelector<HTMLDivElement>("#app")!;
  root.replaceChildren();
  const selectedNode = byId.get(selected) ?? data.nodes[0];
  const sidebar = document.createElement("aside");
  sidebar.className = "sidebar";
  sidebar.setAttribute("aria-label", "Knowledge details");
  const heading = document.createElement("h1");
  heading.textContent = "Native DOM/SVG spike";
  sidebar.append(heading);
  const search = document.createElement("input");
  search.className = "search";
  search.type = "search";
  search.placeholder = "Search concepts";
  search.setAttribute("aria-label", "Search concepts");
  sidebar.append(search);
  const resultList = document.createElement("div");
  resultList.className = "results";
  resultList.setAttribute("role", "listbox");
  sidebar.append(resultList);
  const detail = document.createElement("section");
  detail.setAttribute("aria-live", "polite");
  sidebar.append(detail);
  const canvas = document.createElement("main");
  canvas.className = "canvas";
  canvas.setAttribute("aria-label", "Read-only concept graph");
  root.append(sidebar, canvas);
  const updateResults = () => {
    const query = search.value.toLowerCase();
    resultList.replaceChildren(
      ...data.nodes
        .filter((node) =>
          `${node.title} ${node.summary}`.toLowerCase().includes(query),
        )
        .map((node) => {
          const item = button(node.title, () => {
            selected = node.id;
            render();
          });
          item.setAttribute("role", "option");
          return item;
        }),
    );
  };
  search.oninput = updateResults;
  updateResults();
  detail.replaceChildren();
  if (selectedNode) {
    const title = document.createElement("h2");
    title.textContent = selectedNode.title;
    const summary = document.createElement("p");
    summary.textContent = selectedNode.summary;
    detail.append(title, summary);
    for (const type of relations) {
      const ids = selectedNode.relationships[type] ?? [];
      if (!ids.length) continue;
      const sub = document.createElement("h3");
      sub.textContent = type;
      const list = document.createElement("div");
      list.className = "relations";
      ids.forEach((id) =>
        list.append(
          button(`${type}: ${byId.get(id)?.title ?? id}`, () => {
            selected = id;
            render();
          }),
        ),
      );
      detail.append(sub, list);
    }
    const sourceHead = document.createElement("h3");
    sourceHead.textContent = "Sources";
    detail.append(sourceHead);
    selectedNode.sources.forEach((source) => {
      const link = document.createElement("a");
      link.className = "source";
      link.href = source.url;
      link.textContent = `${source.role ?? "source"}: ${source.title ?? source.url}`;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      detail.append(link);
    });
  }
  const graph = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  graph.setAttribute("width", "100%");
  graph.setAttribute("height", "100%");
  graph.setAttribute("aria-hidden", "true");
  canvas.append(graph);
  const rank = ranks(data),
    width = Math.max(600, Math.ceil(Math.sqrt(data.nodes.length)) * 180),
    positions = new Map<string, [number, number]>();
  const groups = new Map<number, Node[]>();
  data.nodes.forEach((node) => {
    const level = rank.get(node.id) ?? 0;
    groups.set(level, [...(groups.get(level) ?? []), node]);
  });
  groups.forEach((nodes, level) =>
    nodes.forEach((node, index) =>
      positions.set(node.id, [90 + level * 180, 80 + index * 58]),
    ),
  );
  data.nodes.forEach((node) =>
    relations.forEach((type) =>
      (node.relationships[type] ?? []).forEach((target) => {
        const a = positions.get(node.id),
          b = positions.get(target);
        if (!a || !b) return;
        const line = document.createElementNS(
          "http://www.w3.org/2000/svg",
          "line",
        );
        line.setAttribute("x1", String(a[0]));
        line.setAttribute("y1", String(a[1]));
        line.setAttribute("x2", String(b[0]));
        line.setAttribute("y2", String(b[1]));
        line.setAttribute("class", `edge ${type}`);
        graph.append(line);
      }),
    ),
  );
  data.nodes.forEach((node) => {
    const [x, y] = positions.get(node.id)!;
    const item = button(
      node.title,
      () => {
        selected = node.id;
        render();
      },
      "graph-node",
    );
    item.style.left = `${x}px`;
    item.style.top = `${y}px`;
    item.setAttribute("aria-label", `${node.title}; select concept`);
    item.dataset.node = node.id;
    canvas.append(item);
  });
  const status = document.createElement("output");
  status.className = "status";
  status.id = "spike-ready";
  status.textContent = `${__SPIKE_CANDIDATE__}:${data.name}:${data.nodes.length}`;
  canvas.append(status);
}
render();

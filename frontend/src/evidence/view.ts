import type { EvidenceEdge, EvidenceNode } from "../contracts.js";
import { button, element, pretty } from "../dom.js";

export interface EvidenceViewOptions {
  nodes: EvidenceNode[];
  edges: EvidenceEdge[];
  selected: string | null;
  recall: boolean;
  onSelect(id: string): void;
}

function label(node: EvidenceNode, recall: boolean): string {
  if (!recall) return node.title ?? node.claim ?? node.id;
  if (node.kind === "source") return `来源 · ${node.id}`;
  if (node.kind === "milestone") return `历史断言 · ${node.id}`;
  return node.title ?? node.id;
}

function graphLabel(node: EvidenceNode, recall: boolean): string {
  if (recall || node.kind !== "milestone") return label(node, recall);
  const date = node.date?.year ?? "?";
  const actor = node.actors?.[0] ?? node.milestone_id ?? node.id;
  return `${date} · ${pretty(node.milestone_kind ?? "milestone")} · ${actor}`;
}

/** A separate, deterministic evidence layout; evidence edges never imply concept rank. */
export function renderEvidenceGraph(
  container: HTMLElement,
  options: EvidenceViewOptions,
): void {
  const ids = new Set(options.nodes.map((node) => node.id));
  const edges = options.edges.filter(
    (edge) => ids.has(edge.from) && ids.has(edge.to),
  );
  const columns = ["concept", "milestone", "dossier", "source"] as const;
  const grouped = new Map(
    columns.map((kind) => [
      kind,
      options.nodes.filter((node) => node.kind === kind),
    ]),
  );
  const largestColumn = Math.max(
    1,
    ...columns.map((kind) => grouped.get(kind)!.length),
  );
  const rowGap = 72;
  const canvasHeight = Math.max(600, 100 + (largestColumn - 1) * rowGap);
  const xByKind = { concept: 110, milestone: 370, dossier: 630, source: 890 };
  const positions = new Map<string, { x: number; y: number }>();
  for (const kind of columns) {
    const nodes = grouped.get(kind)!;
    const columnHeight = Math.max(0, (nodes.length - 1) * rowGap);
    const startY = (canvasHeight - columnHeight) / 2;
    nodes.forEach((node, index) => {
      positions.set(node.id, {
        x: xByKind[kind],
        y: startY + index * rowGap,
      });
    });
  }
  container.replaceChildren();
  container.style.height = `${canvasHeight}px`;
  container.style.bottom = "auto";
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.classList.add("edge-layer", "evidence-edge-layer");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("viewBox", `0 0 1000 ${canvasHeight}`);
  svg.setAttribute("preserveAspectRatio", "none");
  for (const edge of edges) {
    const from = positions.get(edge.from),
      to = positions.get(edge.to);
    if (!from || !to) continue;
    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", String(from.x));
    line.setAttribute("y1", String(from.y));
    line.setAttribute("x2", String(to.x));
    line.setAttribute("y2", String(to.y));
    line.classList.add("edge", "evidence-edge", edge.kind);
    if (
      options.selected &&
      edge.from !== options.selected &&
      edge.to !== options.selected
    )
      line.classList.add("dim");
    svg.append(line);
  }
  container.append(svg);
  for (const node of options.nodes) {
    const pos = positions.get(node.id)!;
    const control = button(
      "",
      `evidence-node ${node.kind}${node.id === options.selected ? " selected" : ""}`,
    );
    const text = element("span", "evidence-node-label");
    text.textContent = graphLabel(node, options.recall);
    control.append(text);
    control.dataset.evidenceId = node.id;
    control.setAttribute(
      "aria-label",
      `${label(node, options.recall)}，${pretty(node.kind)}`,
    );
    control.style.left = `${pos.x / 10}%`;
    control.style.top = `${pos.y}px`;
    control.onclick = () => options.onSelect(node.id);
    container.append(control);
  }
  if (!options.nodes.length) {
    const empty = element("p", "empty");
    empty.textContent = "当前筛选没有证据节点。";
    container.append(empty);
  }
}

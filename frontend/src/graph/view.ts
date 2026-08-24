import type { Concept, Edge } from "../contracts.js";
import { button, element } from "../dom.js";
import { layout } from "./layout.js";
export interface GraphViewOptions {
  nodes: Concept[];
  edges: Edge[];
  selected: string | null;
  recall: boolean;
  onSelect(id: string): void;
}
export function renderGraph(
  container: HTMLElement,
  options: GraphViewOptions,
): void {
  const ids = new Set(options.nodes.map((node) => node.id));
  const visibleEdges = options.edges.filter(
    (edge) => ids.has(edge.source) && ids.has(edge.target),
  );
  const positions = layout(options.nodes, visibleEdges);
  container.replaceChildren();
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.classList.add("edge-layer");
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("viewBox", "0 0 1000 700");
  if (!options.recall)
    for (const edge of visibleEdges) {
      const a = positions.get(edge.source),
        b = positions.get(edge.target);
      if (!a || !b || !ids.has(edge.source) || !ids.has(edge.target)) continue;
      const line = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "line",
      );
      line.setAttribute("x1", String(a.x));
      line.setAttribute("y1", String(a.y));
      line.setAttribute("x2", String(b.x));
      line.setAttribute("y2", String(b.y));
      line.classList.add("edge", edge.type);
      if (
        options.selected &&
        edge.source !== options.selected &&
        edge.target !== options.selected
      )
        line.classList.add("dim");
      svg.append(line);
    }
  container.append(svg);
  for (const node of options.nodes) {
    const pos = positions.get(node.id)!;
    const control = button(
      node.title,
      `concept ${node.mastery.status}${node.id === options.selected ? " selected" : ""}`,
    );
    control.dataset.id = node.id;
    control.setAttribute("aria-label", `${node.title}，${node.mastery.status}`);
    control.style.left = `${pos.x / 10}%`;
    control.style.top = `${pos.y / 7}%`;
    control.onclick = () => options.onSelect(node.id);
    container.append(control);
  }
  if (!options.nodes.length) {
    const empty = element("p", "empty");
    empty.textContent = "当前筛选没有概念。";
    container.append(empty);
  }
}

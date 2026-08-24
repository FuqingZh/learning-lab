import type { Concept, Edge } from "../contracts.js";
export interface Position {
  x: number;
  y: number;
}
const hash = (value: string): number => {
  let h = 2166136261;
  for (const char of value) {
    h ^= char.charCodeAt(0);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
};
/** Deterministic spatial positions; only prerequisite/enables influence rank. */
export function layout(nodes: Concept[], edges: Edge[]): Map<string, Position> {
  const rank = new Map(nodes.map((node) => [node.id, 0]));
  for (let round = 0; round < nodes.length; round += 1)
    for (const edge of edges)
      if (edge.type === "prerequisites" || edge.type === "enables")
        rank.set(
          edge.target,
          Math.max(
            rank.get(edge.target) ?? 0,
            (rank.get(edge.source) ?? 0) + 1,
          ),
        );
  return new Map(
    nodes.map((node, index) => {
      const r = rank.get(node.id) ?? 0;
      const h = hash(node.id);
      return [
        node.id,
        { x: 120 + r * 190 + (h % 57), y: 90 + ((index * 97 + h) % 530) },
      ];
    }),
  );
}

import type { Fixture, Node, Relation, Source } from "./contracts.js";
import current from "../fixtures/current.json" with { type: "json" };

const relations: Relation[] = [
  "prerequisites",
  "enables",
  "contrasts_with",
  "related",
];

function source(id: string) {
  return {
    url: `https://example.org/evidence/${id}`,
    title: `Evidence for ${id}`,
    publisher: "Spike fixture",
    role: "primary",
  };
}

export function synthetic(size: number): Fixture {
  const nodes: Node[] = Array.from({ length: size }, (_, index) => {
    const id = `synthetic-${String(index + 1).padStart(4, "0")}`;
    const previous = index
      ? `synthetic-${String(index).padStart(4, "0")}`
      : undefined;
    const next =
      index + 1 < size
        ? `synthetic-${String(index + 2).padStart(4, "0")}`
        : undefined;
    return {
      id,
      title: `Synthetic concept ${index + 1}`,
      summary: `Deterministic synthetic concept ${index + 1} for graph scale measurement.`,
      relationships: {
        prerequisites: previous ? [previous] : [],
        enables: next ? [next] : [],
        related:
          index > 4 && index % 5 === 0
            ? [`synthetic-${String(index - 4).padStart(4, "0")}`]
            : [],
        contrasts_with:
          index > 6 && index % 7 === 0
            ? [`synthetic-${String(index - 6).padStart(4, "0")}`]
            : [],
      },
      sources: [source(id)],
    };
  });
  return { schema_version: 1, name: `synthetic-${size}`, nodes };
}

export function fixture(name: string): Fixture {
  if (name === "current") {
    const graph = current as {
      nodes: Array<
        Omit<Node, "sources"> & {
          extensions?: { terminology?: { sources?: Source[] } };
        }
      >;
    };
    return {
      schema_version: 1,
      name,
      nodes: graph.nodes.map((node) => ({
        id: node.id,
        title: node.title,
        summary: node.summary,
        relationships: node.relationships,
        sources: node.extensions?.terminology?.sources ?? [source(node.id)],
      })),
    };
  }
  const size = Number(name.replace("synthetic-", ""));
  if (![100, 300, 1000].includes(size))
    throw new Error(`Unknown fixture: ${name}`);
  return synthetic(size);
}

export { relations };

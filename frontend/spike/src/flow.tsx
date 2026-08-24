import "@xyflow/react/dist/style.css";
import "./style.css";
import dagre from "@dagrejs/dagre";
import {
  Background,
  Controls,
  ReactFlow,
  type Edge,
  type Node as FlowNode,
} from "@xyflow/react";
import { createRoot } from "react-dom/client";
import { flushSync } from "react-dom";
import { useMemo, useState, type ReactElement } from "react";
import { fixture, relations } from "./fixtures.js";
import type { Relation } from "./contracts.js";

declare const __SPIKE_CANDIDATE__: string;
const config = (window as Window & { __SPIKE_CONFIG__?: { fixture: string } })
  .__SPIKE_CONFIG__ ?? { fixture: "current" };
const data = fixture(config.fixture);
const byId = new Map(data.nodes.map((node) => [node.id, node]));
function layout(): { nodes: FlowNode[]; edges: Edge[] } {
  const graph = new dagre.graphlib.Graph();
  graph.setDefaultEdgeLabel(() => ({}));
  graph.setGraph({ rankdir: "LR", ranksep: 90, nodesep: 25 });
  data.nodes.forEach((node) =>
    graph.setNode(node.id, { width: 150, height: 38 }),
  );
  const edges: Edge[] = [];
  data.nodes.forEach((node) =>
    (["prerequisites", "enables"] as Relation[]).forEach((type) =>
      (node.relationships[type] ?? []).forEach((target) => {
        graph.setEdge(target, node.id);
        edges.push({
          id: `${type}:${node.id}:${target}`,
          source: target,
          target: node.id,
          label: type,
          focusable: true,
          ariaLabel: `${type}: ${byId.get(target)?.title} to ${node.title}`,
        });
      }),
    ),
  );
  dagre.layout(graph);
  return {
    nodes: data.nodes.map((node) => {
      const point = graph.node(node.id);
      return {
        id: node.id,
        position: { x: point.x - 75, y: point.y - 19 },
        data: { label: node.title },
        ariaLabel: `${node.title}; read-only concept`,
        ariaRole: "button",
        focusable: true,
        draggable: false,
        selectable: true,
      };
    }),
    edges,
  };
}
function App(): ReactElement {
  const [selected, setSelected] = useState(data.nodes[0]?.id ?? "");
  const [query, setQuery] = useState("");
  const graph = useMemo(layout, []);
  const node = byId.get(selected);
  const result = data.nodes.filter((item) =>
    `${item.title} ${item.summary}`.toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <div className="app">
      <aside className="sidebar" aria-label="Knowledge details">
        <h1>React Flow + Dagre spike</h1>
        <input
          type="search"
          className="search"
          aria-label="Search concepts"
          placeholder="Search concepts"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <div className="results" role="listbox">
          {result.map((item) => (
            <button
              role="option"
              key={item.id}
              onClick={() => setSelected(item.id)}
            >
              {item.title}
            </button>
          ))}
        </div>
        {node && (
          <section aria-live="polite">
            <h2>{node.title}</h2>
            <p>{node.summary}</p>
            {relations.map((type) =>
              (node.relationships[type] ?? []).length ? (
                <div key={type}>
                  <h3>{type}</h3>
                  <div className="relations">
                    {(node.relationships[type] ?? []).map((id) => (
                      <button key={id} onClick={() => setSelected(id)}>
                        {type}: {byId.get(id)?.title ?? id}
                      </button>
                    ))}
                  </div>
                </div>
              ) : null,
            )}
            <h3>Sources</h3>
            {node.sources.map((source) => (
              <a
                className="source"
                key={source.url}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                {source.role ?? "source"}: {source.title ?? source.url}
              </a>
            ))}
          </section>
        )}
      </aside>
      <main className="canvas" aria-label="Read-only concept graph">
        <ReactFlow
          className="flow"
          nodes={graph.nodes}
          edges={graph.edges}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable
          onNodeClick={(_, item) => setSelected(item.id)}
          fitView
        >
          <Background />
          <Controls showInteractive={false} />
        </ReactFlow>
        <output className="status" id="spike-ready">
          {__SPIKE_CANDIDATE__}:{data.name}:{data.nodes.length}
        </output>
      </main>
    </div>
  );
}
flushSync(() => createRoot(document.querySelector("#app")!).render(<App />));

# Knowledge explorer frontend

This directory contains the strict TypeScript projection of Learning Lab's
canonical Python data models. The browser does not parse Markdown/YAML and does
not fetch graph data at runtime. `frontend/build.mjs` runs the repository
builders and embeds four exact schema-v1 projections—concept graph, learning
state, history timeline, and evidence graph—into one HTML file before the
bundled application starts.

Use Node.js 24.x from the repository root:

```bash
npm ci
npm run frontend:verify
```

The frontend verification build is written to ignored
`.build/knowledge-map/index.html`. Run `npm run build:site` to regenerate the
checked-in production artifact through the supported Python adapter. The
adapter checks Node 24 and installed dependencies, while this directory owns
the sole production browser implementation.

The UI uses native DOM/SVG rather than a graph framework. Search renders at
most 24 result controls and the graph projects at most 300 matching nodes. The
complete canonical concept set remains available in the structured
`#concept-list` fallback; the evidence network has a separate complete
`#evidence-list` containing its nodes and typed edges. A checked 1000-node
browser fixture enforces a 500 ms filter ceiling on the recorded host.

Graph nodes use `reviewed_capability` as their primary learner-facing status.
It is produced only by validated, structured learning records; old
filename-derived `mastery` is retained strictly as a subordinate compatibility
label. The learning-state projection is separate: its observations and review
cues drive `Today`, while `Continue` dispatches an explicit concept, lesson,
or track recovery cue without inventing a curriculum step.

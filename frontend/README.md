# Knowledge explorer frontend

This directory contains the strict TypeScript projection of Learning Lab's
canonical Python data models. The browser does not parse Markdown/YAML and does
not fetch graph data at runtime. `frontend/build.mjs` runs the three repository
`normalized-data` commands and embeds their exact schema-v1 JSON into one HTML
file before the bundled application starts.

Use Node.js 22.x from the repository root:

```bash
npm ci
npm run frontend:verify
```

The candidate artifact is written to ignored
`.build/knowledge-map/index.html`. During Slice 3 this command does not modify
the checked-in `site/index.html`; the Python renderer remains the published
path until the atomic parity switch.

The UI uses native DOM/SVG rather than a graph framework. Search renders at
most 24 result controls and the graph projects at most 300 matching nodes. The
complete canonical concept set remains available in the structured
`#concept-list` fallback. A checked 1000-node browser fixture enforces a 500 ms
filter ceiling on the recorded host.

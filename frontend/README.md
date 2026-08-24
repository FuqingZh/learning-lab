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

The frontend verification build is written to ignored
`.build/knowledge-map/index.html`. Run `npm run build:site` to regenerate the
checked-in production artifact through the supported Python adapter. The
adapter checks Node 22 and installed dependencies, while this directory owns
the sole production browser implementation.

The UI uses native DOM/SVG rather than a graph framework. Search renders at
most 24 result controls and the graph projects at most 300 matching nodes. The
complete canonical concept set remains available in the structured
`#concept-list` fallback. A checked 1000-node browser fixture enforces a 500 ms
filter ceiling on the recorded host.

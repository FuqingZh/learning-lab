# Graph technology spike

This isolated Slice 2 spike compares strict TypeScript native DOM/SVG with a
read-only React Flow + Dagre candidate. It does not change the production
renderer, canonical builders, or `site/`.

Fixtures: `fixtures/current.json` is a checked-in normalized graph snapshot;
`fixtures/synthetic-spec.json` fixes deterministic 100/300/1000-node data.
The browser never fetches data or parses Markdown/YAML. Every output under
`dist/` is exactly one self-contained HTML file with inlined CSS and JS.

```bash
npm ci
npm run check
npm run build
npm run smoke
npm run hard-gates # expected to exit 1 after recording every row
npm run measure
```

Ordinary reruns write volatile timings under ignored `.results/`. To replace
the committed decision snapshot intentionally, run the same three commands
with `SPIKE_RESULTS_DIR=results`; the expected nonzero hard-gate command must
not prevent the final measure command from running.

`smoke` opens every candidate/fixture with Chrome DevTools Protocol from
`file://` and an actual local `/learning-lab/site/` HTTP mount. It checks the
single-file/no-runtime-network invariant and the search/result keyboard path.
`hard-gates` additionally executes result -> graph node -> typed relationship
-> source and checks the accessibility tree. Candidate bundles are minified
production IIFEs; the build rejects unresolved external imports.

`measure` records three clean-build digests, five clean builds per candidate,
gzip size, nonblank/noncomment candidate source LOC, direct dependency count,
and CDP browser timing.

`measure` verifies candidate source with the locked dev-only Prettier before
LOC is counted; this prevents source layout from distorting the 70% rule.

## Decision

**Select native DOM/SVG + strict TypeScript for the production migration.**
React Flow + Dagre did not pass the plan's hard gates or bounded-cost tests on
the recorded host. The raw evidence is committed in
`results/hard-gates.json` and `results/measurements.json`.

The recorded snapshot is immutable unless the explicit record commands above
are rerun and this decision is updated. SHA-256: hard gates
`f982ff44…dcc630`, smoke `43d23c3f…34e65`, measurements
`ef48b8cb…32b4a`.

| Check                                       |                 Native | React Flow + Dagre | Decision                                                           |
| ------------------------------------------- | ---------------------: | -----------------: | ------------------------------------------------------------------ |
| Current graph ready, file / Pages           |         59.5 / 58.5 ms |   281.2 / 279.4 ms | Both pass                                                          |
| 1000-node ready, file / Pages               |       525.0 / 538.2 ms | 3039.2 / 3277.0 ms | Both pass                                                          |
| 1000-node filter, file / Pages              |     1446.4 / 1281.1 ms |   764.8 / 715.4 ms | Both exceed 500 ms; native production must bound result rendering  |
| AX concept/source/relationship names        |                   Pass |               Pass | Both pass                                                          |
| Full keyboard path changes selected concept |                   Pass |               Fail | React Flow node exposes a button role but Enter does not select it |
| Three clean-build digests                   |                 Stable |             Stable | Both pass                                                          |
| Gzip single-file size                       |                 3929 B |           142031 B | React is over 2x native                                            |
| Formatted candidate source                  |              176 lines |          147 lines | React is 83.5%, not at most 70%                                    |
| Median clean build                          |                0.188 s |            0.368 s | React passes 3x/15 s bound                                         |
| Direct production dependencies              | 0 for native candidate |                  4 | React passes six-dependency bound                                  |

`npm run hard-gates` intentionally exits nonzero after writing all rows when a
candidate violates a hard threshold. `npm run measure` reads that raw result,
records host/tool versions and cost measurements, and emits the selected
candidate mechanically.

The native spike is not production code. Slice 3 must preserve the current
site contracts and reduce the 1000-node filter update below 500 ms, for example
by limiting rendered search results while preserving a complete structured
fallback. The spike and its dependencies are removed after the production
TypeScript path converges.

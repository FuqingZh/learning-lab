import { build } from "esbuild";
import { mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { join } from "node:path";

const root = new URL("..", import.meta.url).pathname;
const output = join(root, "dist");
const candidates = [
  { name: "native", entry: "src/native.ts" },
  { name: "flow", entry: "src/flow.tsx" },
].filter((candidate) => !process.argv[2] || candidate.name === process.argv[2]);
if (!candidates.length)
  throw new Error(`Unknown candidate: ${process.argv[2]}`);
const fixtures = [
  "current",
  "synthetic-100",
  "synthetic-300",
  "synthetic-1000",
];
const shell = (script, style, fixture) =>
  `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Learning Lab graph spike</title><style>${style}</style></head><body><a class="skip" href="#app">Skip to graph application</a><div id="app"></div><script>window.__SPIKE_CONFIG__=${JSON.stringify({ fixture })};window.__spikeStart=performance.now();window.addEventListener("error",e=>document.body.dataset.spikeError=e.message);</script><script>${script}</script></body></html>`;

await rm(output, { recursive: true, force: true });
await mkdir(output, { recursive: true });
for (const candidate of candidates) {
  const result = await build({
    entryPoints: [join(root, candidate.entry)],
    bundle: true,
    write: false,
    outdir: join(output, ".inline"),
    format: "iife",
    platform: "browser",
    target: ["chrome101"],
    minify: true,
    legalComments: "none",
    metafile: true,
    loader: { ".json": "json" },
    define: {
      __SPIKE_CANDIDATE__: JSON.stringify(candidate.name),
      "process.env.NODE_ENV": JSON.stringify("production"),
    },
  });
  const externalImports = Object.values(result.metafile.outputs).flatMap(
    (artifact) => artifact.imports.filter((item) => item.external),
  );
  if (externalImports.length)
    throw new Error(
      `External runtime imports in ${candidate.name}: ${externalImports
        .map((item) => item.path)
        .join(", ")}`,
    );
  const script = result.outputFiles.find((file) =>
    file.path.endsWith(".js"),
  )?.text;
  const style =
    result.outputFiles.find((file) => file.path.endsWith(".css"))?.text ?? "";
  if (!script) throw new Error(`No JavaScript output for ${candidate.name}`);
  for (const fixture of fixtures)
    await writeFile(
      join(output, `${candidate.name}-${fixture}.html`),
      shell(script, style, fixture),
    );
}

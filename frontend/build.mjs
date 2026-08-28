import { execFileSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const frontend = dirname(fileURLToPath(import.meta.url));
const root = resolve(frontend, "..");

function optionValue(arguments_, name) {
  const index = arguments_.indexOf(name);
  return index === -1 ? null : (arguments_[index + 1] ?? null);
}

function requiredOutput(arguments_) {
  const value = optionValue(arguments_, "--output");
  if (!value) {
    throw new Error("frontend build requires --output <html-path>");
  }
  return resolve(root, value);
}

function requireNode24() {
  const major = Number(process.versions.node.split(".")[0]);
  if (major !== 24) {
    throw new Error(
      `Learning Lab frontend requires Node.js 24.x; found ${process.version}. Install Node.js 24 and run npm ci.`,
    );
  }
}

function normalizedData(script, dataRoot, projection = "normalized-data") {
  const command = process.env.PYTHON ?? "python3";
  let output;
  try {
    output = execFileSync(
      command,
      [resolve(dataRoot, "scripts", script), projection, "--root", dataRoot],
      {
        cwd: dataRoot,
        encoding: "utf8",
        stdio: ["ignore", "pipe", "pipe"],
      },
    );
  } catch (error) {
    const detail = error?.stderr?.toString().trim() || error?.message;
    throw new Error(`${script} ${projection} failed: ${detail}`);
  }
  let data;
  try {
    data = JSON.parse(output);
  } catch (error) {
    throw new Error(`${script} ${projection} emitted invalid JSON: ${error}`);
  }
  if (data?.schema_version !== 1) {
    throw new Error(
      `${script} ${projection} requires normalized schema version 1`,
    );
  }
  return data;
}

function requireSchemaVersion(value, label) {
  if (
    !value ||
    typeof value !== "object" ||
    Array.isArray(value) ||
    value.schema_version !== 1
  ) {
    throw new Error(`${label} requires normalized schema version 1`);
  }
  return value;
}

async function frontendData(arguments_, dataRoot) {
  const dataFile = optionValue(arguments_, "--data-file");
  if (!dataFile) {
    return {
      graph: normalizedData("build-knowledge-map.py", dataRoot),
      learningState: normalizedData("build-learning-state.py", dataRoot),
      history: normalizedData("build-knowledge-history.py", dataRoot),
      evidenceGraph: normalizedData(
        "build-knowledge-history.py",
        dataRoot,
        "normalized-evidence-data",
      ),
    };
  }
  let value;
  try {
    value = JSON.parse(await readFile(resolve(root, dataFile), "utf8"));
  } catch (error) {
    throw new Error(`frontend data file is not valid JSON: ${error}`);
  }
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("frontend data file must contain a JSON object");
  }
  return {
    graph: requireSchemaVersion(value.graph, "GRAPH"),
    learningState: requireSchemaVersion(value.learningState, "LEARNING_STATE"),
    history: requireSchemaVersion(value.history, "HISTORY"),
    evidenceGraph: requireSchemaVersion(value.evidenceGraph, "EVIDENCE_GRAPH"),
  };
}

function safeJson(value) {
  return JSON.stringify(value)
    .replaceAll("<", "\\u003c")
    .replaceAll(">", "\\u003e")
    .replaceAll("&", "\\u0026")
    .replaceAll("\u2028", "\\u2028")
    .replaceAll("\u2029", "\\u2029");
}

function htmlShell({
  graph,
  learningState,
  history,
  evidenceGraph,
  script,
  style,
}) {
  return `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="robots" content="noindex,nofollow">
<title>Learning Lab · Knowledge Space</title>
<style>${style}</style>
</head>
<body>
<a class="sr-only" href="#concept-list">跳到可访问词条列表</a>
<div id="app"></div>
<script id="learning-lab-data">const GRAPH = ${safeJson(graph)};
const LEARNING_STATE = ${safeJson(learningState)};
const HISTORY = ${safeJson(history)};
const EVIDENCE_GRAPH = ${safeJson(evidenceGraph)};
const byId = new Map(GRAPH.nodes.map((node) => [node.id, node]));
window.__LEARNING_LAB_DATA__ = { graph: GRAPH, learningState: LEARNING_STATE, history: HISTORY, evidenceGraph: EVIDENCE_GRAPH };</script>
<script>${script.replaceAll("</script", "<\\/script")}</script>
</body>
</html>
`;
}

async function main() {
  requireNode24();
  const arguments_ = process.argv.slice(2);
  const output = requiredOutput(arguments_);
  const dataRoot = resolve(root, optionValue(arguments_, "--root") ?? root);
  let build;
  try {
    ({ build } = await import("esbuild"));
  } catch {
    throw new Error(
      "Learning Lab frontend dependencies are missing. Run npm ci with Node.js 24.x.",
    );
  }
  const { graph, learningState, history, evidenceGraph } = await frontendData(
    arguments_,
    dataRoot,
  );
  const result = await build({
    entryPoints: [resolve(frontend, "src/entry.ts")],
    bundle: true,
    write: false,
    outdir: resolve(frontend, ".inline"),
    format: "iife",
    platform: "browser",
    target: ["chrome101"],
    minify: true,
    legalComments: "none",
    metafile: true,
  });
  const externalImports = Object.values(result.metafile.outputs).flatMap(
    (artifact) => artifact.imports.filter((item) => item.external),
  );
  if (externalImports.length) {
    throw new Error(
      `frontend build left external runtime imports: ${externalImports
        .map((item) => item.path)
        .join(", ")}`,
    );
  }
  const script = result.outputFiles.find((file) => file.path.endsWith(".js"));
  const style = result.outputFiles.find((file) => file.path.endsWith(".css"));
  if (!script || !style) {
    throw new Error("frontend build did not produce inline JavaScript and CSS");
  }
  await mkdir(dirname(output), { recursive: true });
  await writeFile(
    output,
    htmlShell({
      graph,
      learningState,
      history,
      evidenceGraph,
      script: script.text,
      style: style.text,
    }),
    "utf8",
  );
  console.log(`knowledge map frontend: ${relative(root, output)}`);
}

try {
  await main();
} catch (error) {
  console.error(
    `knowledge map frontend build failed: ${error instanceof Error ? error.message : String(error)}`,
  );
  process.exitCode = 1;
}

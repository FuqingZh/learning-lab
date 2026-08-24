import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { gzipSync } from "node:zlib";
import { cpus, totalmem, platform, release, arch } from "node:os";
import { mkdir, readFile, readdir, rm, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(new URL("..", import.meta.url).pathname);
const resultsDirectory = resolve(
  root,
  process.env.SPIKE_RESULTS_DIR ?? ".results",
);
const sh = (command, args) =>
  execFileSync(command, args, { cwd: root, encoding: "utf8" }).trim();
sh("node", [
  "node_modules/prettier/bin/prettier.cjs",
  "--check",
  "src/native.ts",
  "src/flow.tsx",
]);
const hashes = {};
for (const candidate of ["native", "flow"]) {
  hashes[candidate] = [];
  for (let i = 0; i < 3; i += 1) {
    await rm("dist", { recursive: true, force: true });
    sh("node", ["tools/build.mjs", candidate]);
    hashes[candidate].push(
      createHash("sha256")
        .update(await readFile(`dist/${candidate}-current.html`))
        .digest("hex"),
    );
  }
}
const timings = {};
for (const candidate of ["native", "flow"]) {
  const samples = [];
  for (let i = 0; i < 5; i += 1) {
    await rm("dist", { recursive: true, force: true });
    const start = process.hrtime.bigint();
    sh("node", ["tools/build.mjs", candidate]);
    samples.push(Number(process.hrtime.bigint() - start) / 1e9);
  }
  timings[candidate] = samples;
}
sh("node", ["tools/build.mjs"]);
const gzip = {};
for (const candidate of ["native", "flow"])
  gzip[candidate] = gzipSync(
    await readFile(`dist/${candidate}-current.html`),
  ).length;
const lines = {};
for (const candidate of ["native", "flow"]) {
  const file = await readFile(
    `src/${candidate}.${candidate === "flow" ? "tsx" : "ts"}`,
    "utf8",
  );
  lines[candidate] = file
    .split("\n")
    .filter((line) => line.trim() && !line.trim().startsWith("//")).length;
}
const dependencies = Object.keys(
  JSON.parse(await readFile("package.json", "utf8")).dependencies,
).length;
const median = (values) => {
  const ordered = [...values].sort((left, right) => left - right);
  return ordered[Math.floor(ordered.length / 2)];
};
const hardGates = JSON.parse(
  await readFile(resolve(resultsDirectory, "hard-gates.json"), "utf8"),
);
const smoke = JSON.parse(
  await readFile(resolve(resultsDirectory, "smoke.json"), "utf8"),
);
const smokePassed =
  smoke.rows.length === 16 && smoke.rows.every((row) => row.passed);
const hardGateFailed = (row) =>
  row.error ||
  row.ready_ms === null ||
  row.ready_ms > 5000 ||
  row.filter_ms === null ||
  row.filter_ms > 500 ||
  !row.ax_concept ||
  !row.ax_source ||
  !row.state_changed ||
  (row.fixture === "current" &&
    (!row.keyboard_path_pass || !row.ax_relationship)) ||
  row.console_errors.length > 0 ||
  row.runtime_errors.length > 0 ||
  Boolean(row.page_error);
const flowFailures = hardGates.rows.filter(
  (row) => row.candidate === "flow" && hardGateFailed(row),
);
const costChecks = {
  source_lines_at_most_70_percent: lines.flow <= Math.floor(lines.native * 0.7),
  gzip_at_most_twice_native_and_750_kib:
    gzip.flow <= gzip.native * 2 && gzip.flow <= 750 * 1024,
  median_build_at_most_three_times_native_and_15_seconds:
    median(timings.flow) <= median(timings.native) * 3 &&
    median(timings.flow) <= 15,
  direct_production_dependencies_at_most_six: dependencies <= 6,
};
const measurements = {
  schema_version: 1,
  commands: [
    hardGates.command,
    smoke.command,
    `${process.env.SPIKE_RESULTS_DIR ? `SPIKE_RESULTS_DIR=${process.env.SPIKE_RESULTS_DIR} ` : ""}node tools/measure.mjs`,
  ],
  host: {
    platform: platform(),
    release: release(),
    architecture: arch(),
    cpu: cpus()[0]?.model ?? "unknown",
    cpu_count: cpus().length,
    memory_bytes: totalmem(),
    node: process.version,
    npm: sh("npm", ["--version"]),
    chrome: sh(process.env.CHROME ?? "/usr/bin/google-chrome", ["--version"]),
  },
  hashes,
  deterministic: Object.values(hashes).every(
    (items) => new Set(items).size === 1,
  ),
  timings_seconds: timings,
  median_build_seconds: {
    native: median(timings.native),
    flow: median(timings.flow),
  },
  gzip_bytes: gzip,
  formatted_source_lines: lines,
  prettier_check: true,
  direct_production_dependencies: dependencies,
  hard_gate_failures: flowFailures.map((row) => ({
    fixture: row.fixture,
    mode: row.mode,
    ready_ms: row.ready_ms,
    filter_ms: row.filter_ms,
    ax_concept: row.ax_concept,
    ax_source: row.ax_source,
    keyboard_path_pass: row.keyboard_path_pass,
    ax_relationship: row.ax_relationship,
    state_changed: row.state_changed,
    console_errors: row.console_errors,
    runtime_errors: row.runtime_errors,
    page_error: row.page_error,
    error: row.error,
  })),
  cost_checks: costChecks,
  selected_candidate:
    smokePassed &&
    flowFailures.length === 0 &&
    Object.values(costChecks).every(Boolean)
      ? "react-flow-dagre"
      : "native-dom-svg-typescript",
  files: await readdir("dist"),
  smoke_passed: smokePassed,
  smoke_failures: smoke.rows
    .filter((row) => !row.passed)
    .map((row) => ({
      file: row.file,
      mode: row.mode,
      static_checks: row.static_checks,
      runtime_errors: row.runtime_errors,
      console_errors: row.console_errors,
      error: row.error,
    })),
};
await mkdir(resultsDirectory, { recursive: true });
await writeFile(
  resolve(resultsDirectory, "measurements.json"),
  `${JSON.stringify(measurements, null, 2)}\n`,
);
console.log(JSON.stringify(measurements, null, 2));

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import ts from "typescript";
import { inspect, servePages, withBrowser } from "./browser.mjs";

const root = resolve(new URL("..", import.meta.url).pathname);
const resultsDirectory = resolve(
  root,
  process.env.SPIKE_RESULTS_DIR ?? ".results",
);
const variants = ["native", "flow"].flatMap((candidate) =>
  ["current", "synthetic-100", "synthetic-300", "synthetic-1000"].map(
    (fixture) => `${candidate}-${fixture}.html`,
  ),
);
const pages = await servePages(root);
const rows = [];
function hasModuleImport(html) {
  const scripts = [
    ...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi),
  ];
  return scripts.some((match, index) => {
    const source = ts.createSourceFile(
      `inline-${index}.js`,
      match[1],
      ts.ScriptTarget.ESNext,
      true,
      ts.ScriptKind.JS,
    );
    let found = false;
    const visit = (node) => {
      if (
        ts.isImportDeclaration(node) ||
        (ts.isCallExpression(node) &&
          node.expression.kind === ts.SyntaxKind.ImportKeyword)
      )
        found = true;
      if (!found) ts.forEachChild(node, visit);
    };
    visit(source);
    return found;
  });
}
try {
  for (const file of variants) {
    const path = resolve(root, "dist", file);
    const html = await readFile(path, "utf8");
    const staticChecks = {
      doctype: html.startsWith("<!doctype html>"),
      no_external_script: !/<script[^>]+\ssrc=/i.test(html),
      no_external_stylesheet: !/<link[^>]+rel=["']stylesheet/i.test(html),
      no_module_script: !/type=["']module["']/i.test(html),
      no_remote_runtime_asset:
        !/<(?:script|link|img|source|video|audio|iframe)\b[^>]+(?:src|href)=["']https?:/i.test(
          html,
        ),
      no_runtime_fetch: !/\bfetch\s*\(/.test(html),
      no_module_import: !hasModuleImport(html),
    };
    const selfContained = Object.values(staticChecks).every(Boolean);
    for (const [mode, url] of [
      ["file", `file://${path}`],
      ["pages", `${pages.url}${file}`],
    ]) {
      try {
        const runtimeErrors = [];
        const consoleErrors = [];
        const result = await withBrowser(async (client) => {
          client.Runtime.exceptionThrown(({ exceptionDetails }) => {
            runtimeErrors.push(
              exceptionDetails.exception?.description ??
                exceptionDetails.text ??
                "Unreported runtime exception",
            );
          });
          client.Runtime.consoleAPICalled(({ type, args }) => {
            if (type === "error")
              consoleErrors.push(
                args.map((arg) => arg.value ?? arg.description).join(" "),
              );
          });
          return inspect(client, url);
        });
        const passed =
          selfContained &&
          !result.before.error &&
          Object.values(result.before).slice(0, 4).every(Boolean) &&
          result.afterSearch.option &&
          result.beforeTitle !== result.resultTitle &&
          !result.after.error &&
          runtimeErrors.length === 0 &&
          consoleErrors.length === 0;
        rows.push({
          file,
          mode,
          url:
            mode === "file"
              ? `file://<repo>/frontend/spike/dist/${file}`
              : `/learning-lab/site/${file}`,
          static_checks: staticChecks,
          self_contained: selfContained,
          runtime_errors: runtimeErrors,
          console_errors: consoleErrors,
          passed,
          result,
          error: null,
        });
      } catch (error) {
        rows.push({
          file,
          mode,
          url:
            mode === "file"
              ? `file://<repo>/frontend/spike/dist/${file}`
              : `/learning-lab/site/${file}`,
          static_checks: staticChecks,
          self_contained: selfContained,
          runtime_errors: [],
          console_errors: [],
          passed: false,
          result: null,
          error: error instanceof Error ? error.message : String(error),
        });
      }
    }
  }
} finally {
  await pages.close();
}
await mkdir(resultsDirectory, { recursive: true });
await writeFile(
  resolve(resultsDirectory, "smoke.json"),
  `${JSON.stringify(
    {
      schema_version: 1,
      command: `${process.env.SPIKE_RESULTS_DIR ? `SPIKE_RESULTS_DIR=${process.env.SPIKE_RESULTS_DIR} ` : ""}node tools/smoke.mjs`,
      rows,
    },
    null,
    2,
  )}\n`,
);
if (rows.some((row) => !row.passed)) process.exitCode = 1;
console.log(
  rows.every((row) => row.passed)
    ? `smoke passed: ${variants.length} self-contained artifacts via file:// and /learning-lab/site/; CDP search/result path executed`
    : `smoke failed: ${rows.filter((row) => !row.passed).length} of ${rows.length} delivery paths`,
);

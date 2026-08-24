import { mkdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { inspect, servePages, withBrowser } from "./browser.mjs";

const root = resolve(new URL("..", import.meta.url).pathname);
const resultsDirectory = resolve(
  root,
  process.env.SPIKE_RESULTS_DIR ?? ".results",
);
const output = resolve(resultsDirectory, "hard-gates.json");
const cases = ["native", "flow"].flatMap((candidate) =>
  ["current", "synthetic-1000"].map((fixture) => ({ candidate, fixture })),
);
const pages = await servePages(root);
const rows = [];
const failed = (row) =>
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
try {
  for (const item of cases)
    for (const mode of ["file", "pages"]) {
      const file = `${item.candidate}-${item.fixture}.html`;
      const url =
        mode === "file" ? `file://${root}/dist/${file}` : `${pages.url}${file}`;
      try {
        rows.push(
          await withBrowser(async (client) => {
            const errors = [];
            const runtimeErrors = [];
            client.Runtime.consoleAPICalled(({ type, args }) => {
              if (type === "error")
                errors.push(
                  args.map((arg) => arg.value ?? arg.description).join(" "),
                );
            });
            client.Runtime.exceptionThrown(({ exceptionDetails }) => {
              runtimeErrors.push(
                exceptionDetails.exception?.description ??
                  exceptionDetails.text ??
                  "Unreported runtime exception",
              );
            });
            const started = performance.now();
            const state = await inspect(client, url);
            const ax = await client.Accessibility.getFullAXTree();
            const named = ax.nodes
              .filter(
                (node) =>
                  ["button", "link"].includes(node.role?.value) &&
                  node.name?.value,
              )
              .map((node) => ({
                role: node.role.value,
                name: node.name.value,
              }));
            const concept = named.find(
              (node) =>
                node.role === "button" &&
                /concept|idempotency|partial/i.test(node.name),
            );
            const source = named.find(
              (node) =>
                node.role === "link" &&
                /source|rfc|amazon|evidence/i.test(node.name),
            );
            return {
              ...item,
              mode,
              url:
                mode === "file"
                  ? `file://<repo>/frontend/spike/dist/${file}`
                  : `/learning-lab/site/${file}`,
              ready_ms: state.readyMs,
              filter_ms: state.filterMs,
              input_value: state.afterSearch.value,
              result_count: state.afterSearch.count,
              result_focus: state.resultFocus,
              result_title: state.resultTitle,
              keyboard_path: state.keyboardPath,
              keyboard_path_pass: state.keyboardPath?.passed ?? null,
              ax_relationship: Boolean(
                state.keyboardPath?.relationship_ax_name,
              ),
              keyboard_focus: state.after.focus,
              keyboard_focus_text: state.after.focus_text,
              keyboard_focus_role: state.after.focus_role,
              detail_before: state.beforeTitle,
              detail_after: state.after.title,
              state_changed: state.beforeTitle !== state.resultTitle,
              ax_named_interactive_count: named.length,
              ax_named_interactive_sample: named.slice(0, 12),
              ax_concept: Boolean(concept),
              ax_concept_name: concept?.name ?? null,
              ax_source: Boolean(source),
              ax_source_name: source?.name ?? null,
              console_errors: errors,
              runtime_errors: runtimeErrors,
              elapsed_ms: performance.now() - started,
              page_error: state.before.error ?? state.after.error,
              error: null,
            };
          }),
        );
      } catch (error) {
        rows.push({
          ...item,
          mode,
          url:
            mode === "file"
              ? `file://<repo>/frontend/spike/dist/${file}`
              : `/learning-lab/site/${file}`,
          ready_ms: null,
          filter_ms: null,
          input_value: null,
          result_count: null,
          result_focus: null,
          result_title: null,
          keyboard_path: null,
          keyboard_path_pass: null,
          ax_relationship: false,
          keyboard_focus: null,
          keyboard_focus_text: null,
          keyboard_focus_role: null,
          detail_before: null,
          detail_after: null,
          state_changed: false,
          ax_named_interactive_count: 0,
          ax_named_interactive_sample: [],
          ax_concept: false,
          ax_concept_name: null,
          ax_source: false,
          ax_source_name: null,
          console_errors: [],
          runtime_errors: [],
          elapsed_ms: null,
          page_error: null,
          error: error instanceof Error ? error.message : String(error),
        });
      }
    }
} finally {
  await pages.close();
}
await mkdir(resultsDirectory, { recursive: true });
await writeFile(
  output,
  JSON.stringify(
    {
      schema_version: 1,
      command: `${process.env.SPIKE_RESULTS_DIR ? `SPIKE_RESULTS_DIR=${process.env.SPIKE_RESULTS_DIR} ` : ""}node tools/hard-gates.mjs`,
      chrome: process.env.CHROME ?? "/usr/bin/google-chrome",
      rows,
    },
    null,
    2,
  ) + "\n",
);
console.log(output);
if (rows.some(failed)) process.exitCode = 1;

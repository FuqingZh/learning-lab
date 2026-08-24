import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { execFileSync } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import test from "node:test";
import CDP from "chrome-remote-interface";

const root = resolve(new URL("../..", import.meta.url).pathname);
const chrome = process.env.CHROME ?? "/usr/bin/google-chrome";
const temporary = await mkdtemp(join(tmpdir(), "learning-lab-scale-"));

function syntheticGraph(size) {
  const nodes = Array.from({ length: size }, (_, index) => {
    const number = index + 1;
    const id = `synthetic-${String(number).padStart(4, "0")}`;
    const prerequisite =
      index === 0 ? [] : [`synthetic-${String(index).padStart(4, "0")}`];
    return {
      id,
      title: `Synthetic concept ${number}`,
      summary: `Deterministic scale concept ${number}`,
      kind: "foundation",
      path: `concepts/${id}.md`,
      tracks: ["synthetic"],
      lessons: [],
      records: [],
      case_labs: [],
      mastery: { status: "not-started", effective_record: null },
      relationships: {
        prerequisites: prerequisite,
        enables: [],
        contrasts_with: [],
        related: [],
      },
    };
  });
  return {
    schema_version: 1,
    tracks: ["synthetic"],
    case_labs: [],
    nodes,
    edges: nodes.flatMap((node) =>
      node.relationships.prerequisites.map((source) => ({
        source,
        target: node.id,
        type: "prerequisites",
      })),
    ),
  };
}

async function freePort() {
  const { createServer } = await import("node:net");
  const server = createServer();
  await new Promise((resolve_) => server.listen(0, "127.0.0.1", resolve_));
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("no test port");
  await new Promise((resolve_) => server.close(resolve_));
  return address.port;
}

async function waitForChrome(port) {
  for (let attempt = 0; attempt < 60; attempt += 1) {
    try {
      await fetch(`http://127.0.0.1:${port}/json/version`);
      return;
    } catch {
      await new Promise((resolve_) => setTimeout(resolve_, 100));
    }
  }
  throw new Error("Chrome CDP did not start");
}

async function inspect(url) {
  const port = await freePort();
  const profile = join(temporary, `chrome-${port}`);
  const child = spawn(
    chrome,
    [
      "--headless",
      "--no-sandbox",
      "--disable-gpu",
      "--disable-crash-reporter",
      `--user-data-dir=${profile}`,
      `--remote-debugging-port=${port}`,
      "about:blank",
    ],
    { stdio: "ignore" },
  );
  try {
    await waitForChrome(port);
    const client = await CDP({ port });
    try {
      const { Page, Runtime } = client;
      await Promise.all([Page.enable(), Runtime.enable()]);
      const errors = [];
      Runtime.exceptionThrown(({ exceptionDetails }) => {
        errors.push(
          exceptionDetails.exception?.description ?? exceptionDetails.text,
        );
      });
      const navigationStarted = performance.now();
      const loaded = new Promise((resolve_) => Page.loadEventFired(resolve_));
      await Page.navigate({ url });
      await loaded;
      const loadElapsed = performance.now() - navigationStarted;
      const result = await Runtime.evaluate({
        expression: `new Promise((resolve) => {
          const input = document.querySelector('#search');
          const start = performance.now();
          input.value = 'synthetic';
          input.dispatchEvent(new Event('input', { bubbles: true }));
          requestAnimationFrame(() => requestAnimationFrame(() => {
            const elapsed = performance.now() - start;
            const results = document.querySelectorAll('#results [role=option]').length;
            const fallback = document.querySelectorAll('#concept-list [data-accessible]').length;
            const nodes = document.querySelectorAll('.graph-surface .concept').length;
            document.querySelector('[data-accessible="synthetic-1000"]').click();
            const selectedRetained = Boolean(document.querySelector('.graph-surface [data-id="synthetic-1000"]'));
            document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
            resolve({
              elapsed,
              results,
              fallback,
              nodes,
              selectedRetained,
              escapeCleared: !location.hash.includes('concept=') && !document.querySelector('#panel').classList.contains('open'),
              marker: document.documentElement.dataset.learningLabFrontend,
            });
          }));
        })`,
        awaitPromise: true,
        returnByValue: true,
      });
      if (result.exceptionDetails) {
        throw new Error(
          result.exceptionDetails.exception?.description ??
            result.exceptionDetails.text,
        );
      }
      return { ...result.result.value, loadElapsed, errors };
    } finally {
      await client.close();
    }
  } finally {
    child.kill("SIGTERM");
  }
}

test.after(async () => {
  await rm(temporary, { recursive: true, force: true });
});

test("1000-node search stays bounded while fallback remains complete", async (t) => {
  const canonical = join(temporary, "canonical.html");
  execFileSync("node", ["frontend/build.mjs", "--output", canonical], {
    cwd: root,
    stdio: "pipe",
  });
  const fixture = JSON.stringify(syntheticGraph(1000)).replaceAll(
    "<",
    "\\u003c",
  );
  const html = (await readFile(canonical, "utf8")).replace(
    /const GRAPH = .*;\nconst LEARNING_STATE =/,
    `const GRAPH = ${fixture};\nconst LEARNING_STATE =`,
  );
  const output = join(temporary, "synthetic-1000.html");
  await writeFile(output, html);
  const result = await inspect(pathToFileURL(output).href);
  assert.deepEqual(result.errors, []);
  assert.equal(result.marker, "typescript");
  assert.equal(result.results, 24);
  assert.equal(result.fallback, 1000);
  assert.equal(result.nodes, 300);
  assert.equal(result.selectedRetained, true);
  assert.equal(result.escapeCleared, true);
  assert.ok(result.loadElapsed <= 5000, result);
  assert.ok(result.elapsed <= 500, result);
  t.diagnostic(
    `1000-node page loaded in ${result.loadElapsed.toFixed(1)} ms; filter settled in ${result.elapsed.toFixed(1)} ms with ${result.results} visible results, ${result.nodes} graph nodes, and ${result.fallback} fallback entries`,
  );
});

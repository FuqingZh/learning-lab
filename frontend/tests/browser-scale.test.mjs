import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { execFileSync } from "node:child_process";
import { once } from "node:events";
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

function syntheticEvidenceGraph() {
  return {
    schema_version: 1,
    nodes: [
      {
        id: "concept:synthetic-0001",
        kind: "concept",
        title: "Synthetic concept",
        path: "concepts/synthetic-0001.md",
      },
      {
        id: "dossier:synthetic-history",
        kind: "dossier",
        title: "Synthetic dossier",
        path: "histories/synthetic-history.md",
        summary: "Synthetic evidence dossier.",
      },
      {
        id: "milestone:synthetic-history:claim-1",
        kind: "milestone",
        dossier_id: "synthetic-history",
        milestone_id: "claim-1",
        milestone_kind: "formalization",
        claim: "Synthetic bounded claim.",
        date: { year: 2000, month: 1, day: null },
        boundaries: ["Does not establish anything beyond this fixture."],
        actors: ["Fixture author"],
      },
      {
        id: "source-synthetic",
        kind: "source",
        title: "Synthetic source",
        publisher: "Fixture publisher",
        source_kind: "standard",
        canonical_url: "https://example.test/source",
      },
    ],
    edges: [
      {
        kind: "about",
        from: "milestone:synthetic-history:claim-1",
        to: "concept:synthetic-0001",
      },
      {
        kind: "contained_in",
        from: "milestone:synthetic-history:claim-1",
        to: "dossier:synthetic-history",
      },
      {
        kind: "cites_as_evidence",
        from: "milestone:synthetic-history:claim-1",
        to: "source-synthetic",
        role: "primary",
        locator: "Section synthetic",
        url: "https://example.test/source#synthetic",
      },
    ],
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

async function waitForChrome(port, child, launch) {
  for (let attempt = 0; attempt < 200; attempt += 1) {
    if (launch.error) throw launch.error;
    if (child.exitCode !== null) {
      throw new Error(
        `Chrome exited with ${child.exitCode} before CDP startup${launch.stderr ? `: ${launch.stderr}` : ""}`,
      );
    }
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/version`);
      if (response.ok) return;
    } catch {}
    await new Promise((resolve_) => setTimeout(resolve_, 100));
  }
  throw new Error(
    `Chrome CDP did not start within 20 seconds${launch.stderr ? `: ${launch.stderr}` : ""}`,
  );
}

async function stopChrome(child) {
  if (child.exitCode !== null || child.signalCode !== null) return;
  const exited = once(child, "exit");
  child.kill("SIGTERM");
  const force = setTimeout(() => {
    if (child.exitCode === null && child.signalCode === null)
      child.kill("SIGKILL");
  }, 2000);
  try {
    await exited;
  } finally {
    clearTimeout(force);
  }
}

async function inspect(url) {
  const port = await freePort();
  const profile = join(temporary, `chrome-${port}`);
  const launch = { error: null, stderr: "" };
  const child = spawn(
    chrome,
    [
      "--headless=new",
      "--no-sandbox",
      "--disable-gpu",
      "--disable-dev-shm-usage",
      "--no-first-run",
      "--no-default-browser-check",
      "--disable-crash-reporter",
      `--user-data-dir=${profile}`,
      `--remote-debugging-port=${port}`,
      "about:blank",
    ],
    { stdio: ["ignore", "ignore", "pipe"] },
  );
  child.once("error", (error) => {
    launch.error = error;
  });
  child.stderr?.on("data", (chunk) => {
    launch.stderr = `${launch.stderr}${chunk}`.slice(-4000).trim();
  });
  try {
    await waitForChrome(port, child, launch);
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
        expression: `(async () => {
          const input = document.querySelector('#search');
          const measure = (query) => new Promise((resolve) => {
            const start = performance.now();
            input.value = query;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            requestAnimationFrame(() => requestAnimationFrame(() => {
              resolve(performance.now() - start);
            }));
          });
          const samples = [];
          for (const query of ['synthetic', 'concept', 'synthetic']) {
            samples.push(await measure(query));
          }
          const elapsed = [...samples].sort((a, b) => a - b)[1];
          const results = document.querySelectorAll('#results [role=option]').length;
          const fallback = document.querySelectorAll('#concept-list [data-accessible]').length;
          const nodes = document.querySelectorAll('.graph-surface .concept').length;
          document.querySelector('[data-accessible="synthetic-1000"]').click();
          const selectedRetained = Boolean(document.querySelector('.graph-surface [data-id="synthetic-1000"]'));
          document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
          return {
            elapsed,
            samples,
            results,
            fallback,
            nodes,
            selectedRetained,
            escapeCleared: !location.hash.includes('concept=') && !document.querySelector('#panel').classList.contains('open'),
            marker: document.documentElement.dataset.learningLabFrontend,
          };
        })()`,
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
    await stopChrome(child);
  }
}

async function inspectEvidence(url) {
  const port = await freePort();
  const child = spawn(
    chrome,
    [
      "--headless=new",
      "--no-sandbox",
      "--disable-gpu",
      "--disable-dev-shm-usage",
      "--no-first-run",
      "--no-default-browser-check",
      "--disable-crash-reporter",
      `--user-data-dir=${join(temporary, `chrome-evidence-${port}`)}`,
      `--remote-debugging-port=${port}`,
      "about:blank",
    ],
    { stdio: ["ignore", "ignore", "pipe"] },
  );
  const launch = { error: null, stderr: "" };
  child.once("error", (error) => {
    launch.error = error;
  });
  try {
    await waitForChrome(port, child, launch);
    const client = await CDP({ port });
    try {
      const { Page, Runtime } = client;
      await Promise.all([Page.enable(), Runtime.enable()]);
      const loaded = new Promise((resolve_) => Page.loadEventFired(resolve_));
      await Page.navigate({ url });
      await loaded;
      const result = await Runtime.evaluate({
        expression: `({
        nodes: document.querySelectorAll('.evidence-node').length,
        fallback: document.querySelectorAll('#evidence-list [data-accessible-evidence]').length,
        source: document.querySelector('[data-evidence-id="source-synthetic"]')?.textContent,
        panel: document.querySelector('#panel')?.textContent
      })`,
        returnByValue: true,
      });
      if (result.exceptionDetails)
        throw new Error(result.exceptionDetails.text);
      return result.result.value;
    } finally {
      await client.close();
    }
  } finally {
    await stopChrome(child);
  }
}

test.after(async () => {
  await rm(temporary, {
    recursive: true,
    force: true,
    maxRetries: 5,
    retryDelay: 100,
  });
});

test("1000-node production search stays bounded with a complete fallback", async (t) => {
  const canonical = join(temporary, "canonical.html");
  execFileSync("node", ["frontend/build.mjs", "--output", canonical], {
    cwd: root,
    stdio: "pipe",
  });
  const fixture = JSON.stringify(syntheticGraph(1000)).replaceAll(
    "<",
    "\\u003c",
  );
  const evidence = JSON.stringify(syntheticEvidenceGraph()).replaceAll(
    "<",
    "\\u003c",
  );
  const html = (await readFile(canonical, "utf8"))
    .replace(
      /const GRAPH = .*;\nconst LEARNING_STATE =/,
      `const GRAPH = ${fixture};\nconst LEARNING_STATE =`,
    )
    .replace(
      /const EVIDENCE_GRAPH = .*;\nconst byId/,
      `const EVIDENCE_GRAPH = ${evidence};\nconst byId`,
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
  assert.ok(result.loadElapsed <= 5000, JSON.stringify(result));
  assert.ok(result.elapsed <= 500, JSON.stringify(result));
  t.diagnostic(
    `1000-node page loaded in ${result.loadElapsed.toFixed(1)} ms; median filter settled in ${result.elapsed.toFixed(1)} ms from [${result.samples.map((value) => value.toFixed(1)).join(", ")}] with ${result.results} visible results, ${result.nodes} graph nodes, and ${result.fallback} fallback entries`,
  );
  const evidenceResult = await inspectEvidence(
    `${pathToFileURL(output).href}#view=evidence&evidence=source-synthetic`,
  );
  assert.equal(evidenceResult.nodes, 4);
  assert.equal(evidenceResult.fallback, 4);
  assert.equal(evidenceResult.source, "Synthetic source");
  assert.match(evidenceResult.panel, /Section synthetic/);
  const recallResult = await inspectEvidence(
    `${pathToFileURL(output).href}#view=evidence&evidence=source-synthetic&recall=1`,
  );
  assert.equal(recallResult.source, "来源 · source-synthetic");
  assert.doesNotMatch(recallResult.panel, /Synthetic source|Section synthetic/);
});

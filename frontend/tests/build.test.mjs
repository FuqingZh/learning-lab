import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import test from "node:test";

const root = resolve(new URL("../..", import.meta.url).pathname);
const temporary = await mkdtemp(join(tmpdir(), "learning-lab-frontend-"));

function run(command, arguments_) {
  return execFileSync(command, arguments_, {
    cwd: root,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
}

function build(name) {
  const output = join(temporary, name);
  run("node", ["frontend/build.mjs", "--output", output]);
  return readFile(output, "utf8");
}

function normalized(script, projection = "normalized-data") {
  return JSON.parse(
    run("python3", [`scripts/${script}`, projection, "--root", root]),
  );
}

function embedded(html, name) {
  const match = html.match(new RegExp(`const ${name} = (.*);\\n`));
  assert.ok(match, `missing embedded ${name}`);
  return JSON.parse(match[1]);
}

test.after(async () => {
  await rm(temporary, { recursive: true, force: true });
});

test("verification builds are deterministic and leave the production site untouched", async () => {
  const productionBefore = await readFile(resolve(root, "site/index.html"));
  const first = await build("first.html");
  const second = await build("second.html");
  assert.equal(first, second);
  assert.deepEqual(
    await readFile(resolve(root, "site/index.html")),
    productionBefore,
  );
});

test("the frontend embeds the exact four canonical projections", async () => {
  const html = await build("canonical.html");
  assert.deepEqual(
    embedded(html, "GRAPH"),
    normalized("build-knowledge-map.py"),
  );
  assert.deepEqual(
    embedded(html, "LEARNING_STATE"),
    normalized("build-learning-state.py"),
  );
  assert.deepEqual(
    embedded(html, "HISTORY"),
    normalized("build-knowledge-history.py"),
  );
  assert.deepEqual(
    embedded(html, "EVIDENCE_GRAPH"),
    normalized("build-knowledge-history.py", "normalized-evidence-data"),
  );
});

test("the frontend is one offline HTML artifact with no runtime dependency", async () => {
  const html = await build("offline.html");
  assert.match(html, /^<!doctype html>/);
  assert.doesNotMatch(html, /<script[^>]+\bsrc=/i);
  assert.doesNotMatch(html, /<script[^>]+\btype=["']module/i);
  assert.doesNotMatch(html, /<link[^>]+\bhref=/i);
  assert.doesNotMatch(html, /\bfetch\s*\(/);
  assert.doesNotMatch(html, /\bimport\s*\(/);
  assert.match(html, /window\.__LEARNING_LAB_DATA__ =/);
});

import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { mkdtemp, readFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import CDP from "chrome-remote-interface";

const profile = await mkdtemp(join(tmpdir(), "learning-lab-sample-viewer-"));
const page = new URL(
  "../../../.build/react-sample-viewer/index.html",
  import.meta.url,
);
const chrome = spawn(
  process.env.CHROME ?? "/usr/bin/google-chrome",
  [
    "--headless",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--no-first-run",
    "--no-default-browser-check",
    `--user-data-dir=${profile}`,
    "--remote-debugging-port=0",
    "about:blank",
  ],
  { stdio: ["ignore", "ignore", "pipe"] },
);
let stderr = "";
chrome.stderr.on("data", (chunk) => {
  stderr = (stderr + chunk).slice(-4000);
});
let launchError;
chrome.on("error", (error) => {
  launchError = error;
});
let client;
const watchdog = setTimeout(() => chrome.kill("SIGKILL"), 30000);

try {
  let port;
  for (let attempt = 0; attempt < 100; attempt += 1) {
    if (launchError) throw launchError;
    if (chrome.exitCode !== null || chrome.signalCode !== null) {
      throw new Error("Chrome exited before startup");
    }
    try {
      port = Number(
        (await readFile(join(profile, "DevToolsActivePort"), "utf8")).split(
          "\n",
        )[0],
      );
      if (port) break;
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
    }
    await delay(100);
  }
  assert.ok(port, `Chrome must start within 10 seconds: ${stderr}`);
  client = await CDP({ port });
  const errors = [];
  client.Runtime.exceptionThrown((event) =>
    errors.push(event.exceptionDetails),
  );
  await Promise.all([client.Page.enable(), client.Runtime.enable()]);

  async function evaluate(expression) {
    const response = await client.Runtime.evaluate({
      expression,
      awaitPromise: true,
      returnByValue: true,
    });
    assert.equal(
      response.exceptionDetails,
      undefined,
      "browser evaluation failed",
    );
    return response.result.value;
  }

  async function settle() {
    await evaluate(
      "new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))",
    );
  }

  async function snapshot() {
    return evaluate(`({
      state: document.querySelector('#state').textContent,
      details: document.querySelector('#details').textContent,
      a: document.querySelector('#sample-a').getAttribute('aria-pressed'),
      b: document.querySelector('#sample-b').getAttribute('aria-pressed')
    })`);
  }

  function expectView(view, id) {
    assert.equal(view.state, `selectedSampleId = ${id}`);
    assert.equal(view.a, String(id === "sample-A"));
    assert.equal(view.b, String(id === "sample-B"));
    const expected =
      id === null
        ? "请选择一个样本。"
        : id === "sample-A"
          ? "样本 A分组：对照组Reads：1200000"
          : "样本 B分组：处理组Reads：1800000";
    assert.equal(view.details, expected);
  }

  const loaded = client.Page.loadEventFired();
  await client.Page.navigate({ url: page.href });
  await loaded;
  await settle();
  expectView(await snapshot(), null);

  // Negative control: the checker must reject stale displayed content.
  const initial = await snapshot();
  assert.throws(
    () => expectView({ ...initial, details: "stale result" }, null),
    assert.AssertionError,
  );

  for (const [button, expected] of [
    ["sample-a", "sample-A"],
    ["sample-b", "sample-B"],
    ["sample-b", "sample-B"],
    ["clear", null],
    ["clear", null],
    ["sample-a", "sample-A"],
  ]) {
    await evaluate(
      `document.getElementById(${JSON.stringify(button)}).click()`,
    );
    await settle();
    expectView(await snapshot(), expected);
  }
  const reloaded = client.Page.loadEventFired();
  await client.Page.reload();
  await reloaded;
  await settle();
  expectView(await snapshot(), null);
  assert.deepEqual(errors, [], "no uncaught browser exceptions");
  console.log(
    "PASS: initial, A, B, repeated B, clear, repeated clear, reselect, reload; negative control rejected",
  );
} finally {
  if (client) await client.close();
  if (chrome.exitCode === null && chrome.signalCode === null && chrome.pid) {
    const exited = once(chrome, "exit");
    chrome.kill("SIGTERM");
    const force = setTimeout(() => chrome.kill("SIGKILL"), 2000);
    await exited.finally(() => clearTimeout(force));
  }
  clearTimeout(watchdog);
  console.log(`Temporary Chrome profile retained: ${profile}`);
}

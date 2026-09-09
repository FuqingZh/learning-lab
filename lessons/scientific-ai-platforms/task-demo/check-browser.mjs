import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { setTimeout as delay } from "node:timers/promises";
import CDP from "chrome-remote-interface";

const profile = await mkdtemp(join(tmpdir(), "learning-lab-task-demo-"));
const api = spawn("python3", [new URL("lab.py", import.meta.url).pathname,
  "api", "--db", join(profile, "jobs.sqlite"), "--port", "0"]);
let apiOutput = "";
let apiError;
api.stdout.on("data", (chunk) => { apiOutput += chunk; });
api.on("error", (error) => { apiError = error; });
let worker;
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
  for (let attempt = 0; attempt < 50 && !apiOutput.includes("\n"); attempt++) {
    if (apiError) throw apiError;
    if (api.exitCode !== null) throw new Error("API exited before startup");
    await delay(100);
  }
  const page = apiOutput.split("\n")[0].trim();
  assert.match(page, /^http:\/\/127\.0\.0\.1:\d+$/, "API must start within 5 seconds");
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

  await client.Page.navigate({ url: page });
  async function until(expression) {
    for (let i = 0; i < 100; i++) {
      if (await evaluate(expression)) return;
      await delay(100);
    }
    throw new Error("Browser condition timed out: " + expression);
  }
  await until("!!document.getElementById('submit')");
  await evaluate("document.getElementById('submit').click()");
  await until("document.getElementById('task').textContent.includes('queued')");
  const operation = await evaluate("localStorage.getItem('task-demo-operation')");
  await evaluate("document.getElementById('pause').click()");
  worker = spawn("python3", [new URL("lab.py", import.meta.url).pathname,
    "worker", "--db", join(profile, "jobs.sqlite"), "--duration", ".3"]);
  await delay(1000);
  assert.ok(await evaluate("document.getElementById('task').textContent.includes('queued')"));
  await evaluate("document.getElementById('resume').click()");
  await until("document.getElementById('task').textContent.includes('succeeded')");
  await client.Page.reload();
  await until("!!document.getElementById('task') && document.getElementById('task').textContent.includes('succeeded')");
  assert.equal(await evaluate("localStorage.getItem('task-demo-operation')"), operation);
  // Make query transport fail; the persisted task must retain its terminal result.
  await evaluate("window.queryAttempts = 0; window.fetch = async () => { window.queryAttempts++; throw new Error('test network outage') }; document.getElementById('resume').click()");
  await until("document.getElementById('request').textContent.includes('自动查询已暂停')");
  assert.ok(await evaluate("document.getElementById('task').textContent.includes('succeeded')"));
  assert.equal(await evaluate("window.queryAttempts"), 3);
  assert.deepEqual(errors, []);
  console.log("PASS: browser submit, pause, resume, reload and bounded query retries");
} finally {
  if (client) await client.close();
  for (const process of [worker, api, chrome]) {
    if (process && process.exitCode === null && process.signalCode === null) {
      const ended = once(process, "exit");
      process.kill("SIGTERM");
      const forceStop = setTimeout(() => process.kill("SIGKILL"), 3000);
      await ended;
      clearTimeout(forceStop);
    }
  }
  clearTimeout(watchdog);
  await rm(profile, { recursive: true, force: true });
}

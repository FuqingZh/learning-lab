import CDP from "chrome-remote-interface";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";

const chrome = process.env.CHROME ?? "/usr/bin/google-chrome";
let nextPort = 9422;
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
async function chromeReady(port) {
  for (let attempt = 0; attempt < 50; attempt += 1) {
    try {
      await fetch(`http://127.0.0.1:${port}/json/version`);
      return;
    } catch {
      await wait(100);
    }
  }
  throw new Error("Chrome CDP did not start");
}
export async function withBrowser(run) {
  const port = nextPort++;
  const profile = `/tmp/learning-lab-spike-cdp-${port}`;
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
    await chromeReady(port);
    const client = await CDP({ port });
    try {
      return await run(client);
    } finally {
      await client.close();
    }
  } finally {
    child.kill("SIGTERM");
  }
}
export async function servePages(root) {
  const server = createServer(async (request, response) => {
    const pathname = new URL(request.url ?? "/", "http://127.0.0.1").pathname;
    const prefix = "/learning-lab/site/";
    const name = pathname.startsWith(prefix)
      ? pathname.slice(prefix.length)
      : "";
    if (!name || name.includes("/")) return response.writeHead(404).end();
    try {
      const body = await readFile(`${root}/dist/${name}`);
      response.writeHead(200, { "content-type": "text/html" }).end(body);
    } catch {
      response.writeHead(404).end();
    }
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  if (!address || typeof address === "string")
    throw new Error("Pages server unavailable");
  return {
    url: `http://127.0.0.1:${address.port}/learning-lab/site/`,
    close: () => new Promise((resolve) => server.close(resolve)),
  };
}
export async function inspect(client, url) {
  const { Page, Runtime, Input, Accessibility } = client;
  await Promise.all([Page.enable(), Runtime.enable(), Accessibility.enable()]);
  const loaded = new Promise((resolve) => Page.loadEventFired(resolve));
  await Page.navigate({ url });
  await loaded;
  const evaluate = async (expression) =>
    (
      await Runtime.evaluate({
        expression,
        returnByValue: true,
        awaitPromise: true,
      })
    ).result.value;
  const settle = () =>
    evaluate(
      `new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))`,
    );
  const press = async (key, code, virtualKeyCode, text = undefined) => {
    await Input.dispatchKeyEvent({
      type: "keyDown",
      key,
      code,
      text,
      unmodifiedText: text,
      windowsVirtualKeyCode: virtualKeyCode,
      nativeVirtualKeyCode: virtualKeyCode,
    });
    await Input.dispatchKeyEvent({
      type: "keyUp",
      key,
      code,
      windowsVirtualKeyCode: virtualKeyCode,
      nativeVirtualKeyCode: virtualKeyCode,
    });
  };
  const activate = () => press("Enter", "Enter", 13, "\r");
  const tabUntil = async (condition, maximum = 40) => {
    for (let index = 0; index < maximum; index += 1) {
      await press("Tab", "Tab", 9);
      const focused = await evaluate(
        `(()=>{const element=document.activeElement;return {matched:!!element&&(${condition}),tag:element?.tagName||null,text:(element?.textContent?.trim()||null)?.slice(0,200)??null,role:element?.getAttribute('role')||null}})()`,
      );
      if (focused.matched) return focused;
    }
    throw new Error(`keyboard focus did not reach ${condition}`);
  };
  for (
    let attempt = 0;
    attempt < 50 &&
    !(await evaluate(`!!document.querySelector('input[type=search]')`));
    attempt += 1
  )
    await wait(100);
  for (
    let attempt = 0;
    attempt < 50 &&
    !(await evaluate(`!!document.querySelector('#spike-ready')`));
    attempt += 1
  )
    await wait(20);
  const readyMs = await evaluate(`performance.now()-window.__spikeStart`);
  const before = await evaluate(
    `({ready:!!document.querySelector('#spike-ready'),search:!!document.querySelector('input[type=search]'),node:!!document.querySelector('[data-node],.react-flow__node'),source:!!document.querySelector('a.source'),error:document.body.dataset.spikeError||null})`,
  );
  const beforeTitle = await evaluate(
    `document.querySelector('.sidebar h2')?.textContent||null`,
  );
  await evaluate(`document.querySelector('input[type=search]')?.focus()`);
  const filterStart = await evaluate(`performance.now()`);
  for (const char of url.includes("current")
    ? "Idempotency key"
    : "Synthetic concept 2")
    await Input.dispatchKeyEvent({ type: "char", text: char });
  await settle();
  const filterMs = await evaluate(`performance.now()-${filterStart}`);
  const afterSearch = await evaluate(
    `({option:!!document.querySelector('[role=option]'),value:document.querySelector('input[type=search]')?.value,count:document.querySelectorAll('[role=option]').length})`,
  );
  const resultFocus = await tabUntil(`element.matches('[role=option]')`);
  await activate();
  await settle();
  const resultTitle = await evaluate(
    `document.querySelector('.sidebar h2')?.textContent||null`,
  );

  let keyboardPath = null;
  if (url.includes("current")) {
    const graphFocus = await tabUntil(
      `element.matches('.graph-node,.react-flow__node')&&element.textContent?.trim()==='Idempotency'`,
    );
    await activate();
    await settle();
    const graphTitle = await evaluate(
      `document.querySelector('.sidebar h2')?.textContent||null`,
    );
    const relationshipFocus = await tabUntil(
      `element.matches('.relations button')`,
    );
    const relationshipTree = await Accessibility.getFullAXTree();
    const relationAxName =
      relationshipTree.nodes.find(
        (node) =>
          node.role?.value === "button" &&
          /prerequisites|enables|contrasts_with|related/.test(
            node.name?.value ?? "",
          ),
      )?.name?.value ?? null;
    await activate();
    await settle();
    const relationshipTitle = await evaluate(
      `document.querySelector('.sidebar h2')?.textContent||null`,
    );
    await evaluate(
      `window.__spikeSourceActivated=false;document.addEventListener('click',event=>{const link=event.target.closest?.('a.source');if(link){event.preventDefault();window.__spikeSourceActivated=true}},{capture:true,once:true})`,
    );
    const sourceFocus = await tabUntil(`element.matches('a.source')`);
    await activate();
    await settle();
    const sourceActivated = await evaluate(
      `window.__spikeSourceActivated===true`,
    );
    keyboardPath = {
      result_focus: resultFocus,
      result_title: resultTitle,
      graph_focus: graphFocus,
      graph_title: graphTitle,
      relationship_focus: relationshipFocus,
      relationship_ax_name: relationAxName,
      relationship_title: relationshipTitle,
      source_focus: sourceFocus,
      source_activated: sourceActivated,
      passed:
        beforeTitle !== resultTitle &&
        resultTitle !== graphTitle &&
        graphTitle !== relationshipTitle &&
        Boolean(relationAxName) &&
        sourceActivated,
    };
  }
  const after = await evaluate(
    `({focus:document.activeElement?.tagName,focus_text:(document.activeElement?.textContent?.trim()||null)?.slice(0,200)??null,focus_role:document.activeElement?.getAttribute('role'),title:document.querySelector('.sidebar h2')?.textContent||null,ready:!!document.querySelector('#spike-ready'),error:document.body.dataset.spikeError||null})`,
  );
  return {
    before,
    afterSearch,
    after,
    readyMs,
    filterMs,
    beforeTitle,
    resultFocus,
    resultTitle,
    keyboardPath,
  };
}

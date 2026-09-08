import { build } from "esbuild";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const directory = fileURLToPath(new URL(".", import.meta.url));
const repository = fileURLToPath(new URL("../../../", import.meta.url));
const output = join(repository, ".build/react-sample-viewer");
// Reuse the installed spike dependencies without changing manifests or lockfiles.
const bundle = await build({
  entryPoints: [join(directory, "app.jsx")],
  nodePaths: [join(repository, "frontend/spike/node_modules")],
  bundle: true,
  write: false,
  format: "iife",
  jsx: "automatic",
  define: { "process.env.NODE_ENV": '"development"' },
});
const html = await readFile(join(directory, "index.html"), "utf8");
const script = bundle.outputFiles[0].text.replaceAll("</script", "<\\/script");
await mkdir(output, { recursive: true });
await writeFile(
  join(output, "index.html"),
  html.replace("/* APP_BUNDLE */", () => script),
);
console.log(join(output, "index.html"));

export function element<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  className?: string,
): HTMLElementTagNameMap[K] {
  const node = document.createElement(tag);
  if (className) node.className = className;
  return node;
}
export function button(label: string, className?: string): HTMLButtonElement {
  const node = element("button", className);
  node.type = "button";
  node.textContent = label;
  return node;
}
export function pretty(value: string): string {
  return value.replaceAll("_", " ").replaceAll("-", " ");
}
export function safeHttps(value: string): string | null {
  try {
    const url = new URL(value);
    return url.protocol === "https:" ? url.href : null;
  } catch {
    return null;
  }
}
export function sourceLink(
  source: { url: string; title?: string; publisher?: string; role?: string },
  className = "evidence",
): HTMLAnchorElement | null {
  const href = safeHttps(source.url);
  if (!href) return null;
  const link = element("a", className);
  link.href = href;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.textContent =
    [source.role, source.publisher, source.title].filter(Boolean).join(" · ") ||
    href;
  return link;
}
export function repositoryLink(path: string): string {
  const encoded = path.split("/").map(encodeURIComponent).join("/");
  return location.protocol === "file:"
    ? `../${encoded}`
    : `https://github.com/FuqingZh/learning-lab/blob/main/${encoded}`;
}

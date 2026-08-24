export interface UrlState {
  concept: string | null;
  history: string | null;
  learning: "today" | "continue" | null;
  recall: boolean;
  view: "graph" | "history";
}
export function readUrl(): UrlState {
  const p = new URLSearchParams(location.hash.slice(1));
  const learning = p.get("learning");
  return {
    concept: p.get("concept"),
    history: p.get("history"),
    learning: learning === "today" || learning === "continue" ? learning : null,
    recall: p.get("recall") === "1",
    view: p.get("view") === "history" ? "history" : "graph",
  };
}
export function writeUrl(state: UrlState): void {
  const p = new URLSearchParams();
  if (state.concept) p.set("concept", state.concept);
  if (state.history) p.set("history", state.history);
  if (state.learning) p.set("learning", state.learning);
  if (state.recall) p.set("recall", "1");
  if (state.view === "history") p.set("view", "history");
  history.replaceState(
    null,
    "",
    p.size ? `#${p}` : `${location.pathname}${location.search}`,
  );
}

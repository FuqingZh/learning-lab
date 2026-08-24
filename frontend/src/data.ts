import type { FrontendData } from "./contracts.js";

declare global {
  interface Window {
    __LEARNING_LAB_DATA__?: FrontendData;
  }
}

export function injectedData(): FrontendData {
  const data = window.__LEARNING_LAB_DATA__;
  if (
    !data ||
    data.graph?.schema_version !== 1 ||
    data.learningState?.schema_version !== 1 ||
    data.history?.schema_version !== 1
  ) {
    throw new Error(
      "Learning Lab frontend requires build-time GRAPH, LEARNING_STATE, and HISTORY schema version 1 data.",
    );
  }
  return data;
}

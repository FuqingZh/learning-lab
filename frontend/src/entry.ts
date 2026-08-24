import { mountKnowledgeExplorer } from "./app.js";
import { injectedData } from "./data.js";
import "./style.css";

const root = document.querySelector<HTMLElement>("#app");
if (!root)
  throw new Error("Learning Lab frontend requires an #app mount point.");
mountKnowledgeExplorer(root, injectedData());
document.documentElement.dataset.learningLabFrontend = "typescript";

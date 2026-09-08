import { useState } from "react";
import { createRoot } from "react-dom/client";

// Fictional teaching data, not experimental results.
const samples = {
  "sample-A": { name: "样本 A", group: "对照组", reads: 1200000 },
  "sample-B": { name: "样本 B", group: "处理组", reads: 1800000 },
};

function SampleList(props) {
  function selectA() {
    props.onSelect("sample-A");
  }

  function selectB() {
    props.onSelect("sample-B");
  }

  return (
    <section aria-labelledby="list-title">
      <h2 id="list-title">选择样本</h2>
      <button
        id="sample-a"
        onClick={selectA}
        aria-pressed={props.selectedId === "sample-A"}
      >
        样本 A <small>对照组</small>
      </button>
      <button
        id="sample-b"
        onClick={selectB}
        aria-pressed={props.selectedId === "sample-B"}
      >
        样本 B <small>处理组</small>
      </button>
    </section>
  );
}

function SampleDetails(props) {
  if (props.sample === null) {
    return <p id="details">请选择一个样本。</p>;
  }

  return (
    <div id="details">
      <h3>{props.sample.name}</h3>
      <p>分组：{props.sample.group}</p>
      <p>Reads：{props.sample.reads}</p>
    </div>
  );
}

function App() {
  const [selectedSampleId, setSelectedSampleId] = useState(null);

  function selectSample(id) {
    setSelectedSampleId(id);
  }

  function clearSelection() {
    setSelectedSampleId(null);
  }

  let selectedSample = null;
  if (selectedSampleId !== null) {
    selectedSample = samples[selectedSampleId];
  }

  return (
    <main>
      <header>
        <span className="eyebrow">LEARNING LAB · REACT</span>
        <h1>样本浏览器</h1>
        <p>选择样本，查看详情，再清除选择。数据均为虚构教学示例。</p>
      </header>
      <div className="toolbar">
        <output id="state" aria-live="polite">
          selectedSampleId = {String(selectedSampleId)}
        </output>
        <button id="clear" onClick={clearSelection}>
          清除选择
        </button>
      </div>
      <div className="panels">
        <SampleList selectedId={selectedSampleId} onSelect={selectSample} />
        <section aria-labelledby="details-title" aria-live="polite">
          <h2 id="details-title">样本详情</h2>
          <SampleDetails sample={selectedSample} />
        </section>
      </div>
      <footer>本例没有后端或数据库；刷新页面会回到未选择状态。</footer>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);

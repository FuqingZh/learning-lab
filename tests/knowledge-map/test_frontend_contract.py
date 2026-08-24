#!/usr/bin/env python3
"""Browser and embedding contracts for the generated knowledge explorer.

The suite exercises the supported Python entrypoint as a black box while the
TypeScript frontend remains the sole browser implementation. The canonical
Python data models must not be reinterpreted by either layer.
"""

from __future__ import annotations

import contextlib
import http.server
import json
import os
import re
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RENDERER = ROOT / "scripts" / "render-knowledge-map-site.py"
CHROME = shutil.which("google-chrome") or shutil.which("chromium")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Keep the local Pages-path fixture server quiet during contract tests."""

    def log_message(self, format: str, *args: object) -> None:
        pass


@contextlib.contextmanager
def serve(directory: Path):
    """Serve ``directory`` at a loopback origin with an ephemeral port."""

    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(directory), **kwargs)
    with socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_address[1]}"
        finally:
            server.shutdown()
            thread.join()


class TestFrontendContract(unittest.TestCase):
    maxDiff = None

    def render(self, output: Path) -> str:
        result = subprocess.run(
            ["python3", str(RENDERER), "--root", str(ROOT), "--output", str(output)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return output.read_text(encoding="utf-8")

    def normalized(self, script: str, projection: str = "normalized-data") -> object:
        result = subprocess.run(
            ["python3", str(ROOT / "scripts" / script), projection, "--root", str(ROOT)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def browser_dump(
        self,
        source: Path,
        fragment: str,
        probe: str,
        *,
        url: str | None = None,
        window_size: str | None = None,
        reduced_motion: bool = False,
    ) -> str:
        self.assertIsNotNone(CHROME, "Chrome or Chromium is required for frontend contracts")
        instrumented = source.with_name("instrumented.html")
        html = source.read_text(encoding="utf-8")
        html = html.replace("</body>", f"<script>window.addEventListener('load',()=>{{{probe}}});</script></body>")
        instrumented.write_text(html, encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            environment = os.environ.copy()
            environment.update(
                {
                    "TMPDIR": str(temporary),
                    "XDG_CONFIG_HOME": str(temporary / "config"),
                    "XDG_CACHE_HOME": str(temporary / "cache"),
                }
            )
            command = [
                str(CHROME),
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-breakpad",
                "--disable-crash-reporter",
                f"--user-data-dir={temporary / 'profile'}",
                "--dump-dom",
            ]
            if window_size:
                command.append(f"--window-size={window_size}")
            if reduced_motion:
                command.append("--force-prefers-reduced-motion")
            target = url or instrumented.as_uri()
            result = subprocess.run(
                command + [target + fragment],
                text=True,
                capture_output=True,
                check=False,
                timeout=25,
                env=environment,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    @staticmethod
    def embedded(content: str, name: str, following: str) -> object:
        matched = re.search(
            rf"const {name}\s*=\s*(\{{.*?\}});\s*const {following}\s*=",
            content,
            flags=re.DOTALL,
        )
        if matched is None:
            raise AssertionError(f"missing embedded {name} payload")
        return json.loads(matched.group(1))

    def test_embedded_models_are_exact_canonical_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            content = self.render(Path(directory) / "index.html")

        self.assertEqual(
            self.embedded(content, "GRAPH", "LEARNING_STATE"),
            self.normalized("build-knowledge-map.py"),
        )
        self.assertEqual(
            self.embedded(content, "LEARNING_STATE", "HISTORY"),
            self.normalized("build-learning-state.py"),
        )
        self.assertEqual(
            self.embedded(content, "HISTORY", "EVIDENCE_GRAPH"),
            self.normalized("build-knowledge-history.py"),
        )
        self.assertEqual(
            self.embedded(content, "EVIDENCE_GRAPH", "byId"),
            self.normalized(
                "build-knowledge-history.py", "normalized-evidence-data"
            ),
        )

    def test_three_clean_renders_are_byte_identical_and_have_no_runtime_assets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rendered = [self.render(root / f"site-{index}.html") for index in range(3)]
        self.assertEqual(rendered[0], rendered[1])
        self.assertEqual(rendered[1], rendered[2])
        content = rendered[0]
        self.assertNotRegex(content, r"(?i)<script[^>]+\bsrc=")
        self.assertNotRegex(content, r"(?i)<script[^>]+\btype=[\"']module")
        self.assertNotRegex(content, r"(?i)<link[^>]+\bhref=")
        self.assertNotRegex(content, r"\bfetch\s*\(")
        self.assertNotRegex(content, r"\bimport\s*\(")

    def test_file_hash_routes_keep_concept_history_learning_and_recall_state(self) -> None:
        probe = """
document.body.dataset.panel=String(document.querySelector('#panel').classList.contains('open'));
document.body.dataset.history=String(!document.querySelector('#history-overlay').hidden);
document.body.dataset.learning=String(document.querySelector('#learning-view').classList.contains('open'));
document.body.dataset.recall=document.querySelector('#recall-toggle').getAttribute('aria-pressed');
document.body.dataset.evidence=String(document.querySelector('#panel').textContent.includes('Cooperating Sequential Processes'));
document.body.dataset.body=document.body.textContent;
"""
        cases = {
            "#concept=idempotency": {"data-panel=\"true\"": True},
            "#history=idempotency-history&view=history": {"data-history=\"true\"": True},
            "#learning=today": {"data-learning=\"true\"": True},
            "#learning=continue": {"data-learning=\"true\"": True},
            "#concept=idempotency&recall=1": {"data-panel=\"true\"": True, "data-recall=\"true\"": True},
            "#view=evidence&evidence=source-e69e9cccb6f79c4f": {
                "data-panel=\"true\"": True,
                "data-evidence=\"true\"": True,
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "index.html"
            self.render(output)
            for fragment, expectations in cases.items():
                with self.subTest(fragment=fragment):
                    dom = self.browser_dump(output, fragment, probe)
                    for expected in expectations:
                        self.assertIn(expected, dom)
                    if "recall=1" in fragment:
                        self.assertIn("答案已隐藏。", dom)

    def test_simulated_pages_subpath_loads_and_preserves_deep_link(self) -> None:
        probe = """
document.body.dataset.path=location.pathname;
document.body.dataset.panel=String(document.querySelector('#panel').classList.contains('open'));
document.body.dataset.history=String(!document.querySelector('#history-overlay').hidden);
document.body.dataset.evidence=String(document.querySelector('#panel').textContent.includes('Cooperating Sequential Processes'));
"""
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            output = temporary / "learning-lab" / "site" / "index.html"
            self.render(output)
            with serve(temporary) as origin:
                dom = self.browser_dump(
                    output,
                    "#concept=idempotency&history=idempotency-history&view=history",
                    probe,
                    url=f"{origin}/learning-lab/site/instrumented.html",
                )
                evidence_dom = self.browser_dump(
                    output,
                    "#view=evidence&evidence=source-e69e9cccb6f79c4f",
                    probe,
                    url=f"{origin}/learning-lab/site/instrumented.html",
                )
        self.assertIn('data-path="/learning-lab/site/instrumented.html"', dom)
        self.assertIn('data-panel="false"', dom)
        self.assertIn('data-history="true"', dom)
        self.assertIn('data-path="/learning-lab/site/instrumented.html"', evidence_dom)
        self.assertIn('data-panel="true"', evidence_dom)
        self.assertIn('data-evidence="true"', evidence_dom)

    def test_keyboard_native_controls_and_structured_concept_fallback(self) -> None:
        probe = """
const search=document.querySelector('#search');search.focus();search.value='idempotency';search.dispatchEvent(new Event('input',{bubbles:true}));
const result=document.querySelector('#results [role="option"]');
document.body.dataset.searchFocus=String(document.activeElement===search);
document.body.dataset.result=String(result&&result.tagName==='BUTTON'&&result.tabIndex===0);
result.click();
const relation=document.querySelector('#panel [data-target]');
relation.focus();document.body.dataset.relation=String(relation&&relation.tagName==='BUTTON'&&document.activeElement===relation);
relation.click();
const source=document.querySelector('#panel a.canonical');source.focus();document.body.dataset.source=String(source&&source.tagName==='A'&&source.tabIndex===0&&document.activeElement===source);
document.body.dataset.panel=String(document.querySelector('#panel').classList.contains('open'));
"""
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "index.html"
            content = self.render(output)
            dom = self.browser_dump(output, "", probe)
        graph = self.embedded(content, "GRAPH", "LEARNING_STATE")
        fallback = re.search(r'<div class="sr-only" id="concept-list">(.*?)</div>', dom, re.DOTALL)
        self.assertIsNotNone(fallback)
        self.assertEqual(fallback.group(1).count('data-accessible='), len(graph["nodes"]))
        for attribute in ("data-search-focus=\"true\"", "data-result=\"true\"", "data-relation=\"true\"", "data-source=\"true\"", "data-panel=\"true\""):
            self.assertIn(attribute, dom)

    def test_keyboard_evidence_path_and_complete_typed_fallback(self) -> None:
        probe = """
document.querySelector('.learning-card button').click();
document.querySelector('#evidence-mode').click();
const search=document.querySelector('#search');search.focus();search.value='Cooperating Sequential Processes';search.dispatchEvent(new Event('input',{bubbles:true}));
const result=document.querySelector('#results [role="option"]');
document.body.dataset.result=String(result&&result.tagName==='BUTTON'&&result.tabIndex===0);
result.click();
const source=document.querySelector('#panel a.canonical');
const reverse=document.querySelector('#panel button.relation');
document.body.dataset.source=String(source&&source.href.startsWith('https://www.cs.utexas.edu/')&&source.rel==='noopener noreferrer');
document.body.dataset.reverse=String(reverse&&reverse.tagName==='BUTTON'&&reverse.tabIndex===0);
reverse.focus();reverse.click();
document.body.dataset.milestone=String(document.querySelector('#panel').textContent.includes('dijkstra-ewd123-1965'));
document.body.dataset.program=String(document.querySelector('#panel').textContent.includes('Program'));
document.body.dataset.process=String(document.querySelector('#panel').textContent.includes('Process'));
document.body.dataset.service=String(document.querySelector('#panel').textContent.includes('Service'));
document.body.dataset.learning=String(document.querySelector('#learning-view').classList.contains('open'));
document.body.dataset.fallbackNodes=String(document.querySelectorAll('#evidence-list [data-accessible-evidence]').length);
document.body.dataset.fallbackEdges=String(document.querySelectorAll('#evidence-list [data-accessible-evidence-edge]').length);
const space=document.querySelector('#space').getBoundingClientRect();
const node=document.querySelector('.evidence-node').getBoundingClientRect();
document.body.dataset.visible=String(space.height>0&&node.width>0&&node.height>0&&node.bottom>space.top&&node.top<space.bottom);
"""
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "index.html"
            content = self.render(output)
            dom = self.browser_dump(output, "", probe)
        evidence = self.embedded(content, "EVIDENCE_GRAPH", "byId")
        self.assertIn('data-result="true"', dom)
        self.assertIn('data-source="true"', dom)
        self.assertIn('data-reverse="true"', dom)
        self.assertIn('data-milestone="true"', dom)
        self.assertIn('data-program="true"', dom)
        self.assertIn('data-process="true"', dom)
        self.assertIn('data-service="false"', dom)
        self.assertIn('data-learning="false"', dom)
        self.assertIn('data-visible="true"', dom)
        self.assertIn(f'data-fallback-nodes="{len(evidence["nodes"])}"', dom)
        self.assertIn(f'data-fallback-edges="{len(evidence["edges"])}"', dom)

    def test_320px_reduced_motion_keeps_controls_separate(self) -> None:
        probe = """
const app=document.querySelector('#app');app.style.width='320px';
const search=document.querySelector('.search').getBoundingClientRect(),card=document.querySelector('.learning-card').getBoundingClientRect();
const overlap=search.left<card.right&&search.right>card.left&&search.top<card.bottom&&search.bottom>card.top;
document.body.dataset.width=String(Math.round(app.getBoundingClientRect().width));
document.body.dataset.overlap=String(overlap);
document.body.dataset.reduced=String(matchMedia('(prefers-reduced-motion: reduce)').matches);
document.body.dataset.transition=getComputedStyle(document.querySelector('#panel')).transitionDuration;
"""
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "index.html"
            self.render(output)
            dom = self.browser_dump(output, "", probe, window_size="320,844", reduced_motion=True)
        self.assertIn('data-width="320"', dom)
        self.assertIn('data-overlap="false"', dom)
        self.assertIn('data-reduced="true"', dom)
        self.assertIn('data-transition="0s"', dom)

        evidence_probe = """
const app=document.querySelector('#app');app.style.width='320px';
const filters=document.querySelector('.filters').getBoundingClientRect();
const panel=document.querySelector('#panel').getBoundingClientRect();
const overlap=filters.left<panel.right&&filters.right>panel.left&&filters.top<panel.bottom&&filters.bottom>panel.top;
document.body.dataset.filterBottom=String(Math.round(filters.bottom));
document.body.dataset.panelTop=String(Math.round(panel.top));
document.body.dataset.overlap=String(overlap);
"""
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "index.html"
            self.render(output)
            evidence_dom = self.browser_dump(
                output,
                "#view=evidence&evidence=source-e69e9cccb6f79c4f",
                evidence_probe,
                window_size="320,844",
            )
        self.assertIn('data-overlap="false"', evidence_dom)


if __name__ == "__main__":
    unittest.main()

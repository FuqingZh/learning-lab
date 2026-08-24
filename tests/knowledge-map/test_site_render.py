#!/usr/bin/env python3
"""Semantic contracts for the rendered offline knowledge-map site.

This suite deliberately avoids browser implementation details. The frozen
frontend-contract suite owns the complete route and interaction baseline;
these checks protect renderer-entrypoint behavior and the history/terminology
semantics which must survive a frontend replacement.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY_ROOT / "scripts" / "render-knowledge-map-site.py"
CHROME = shutil.which("google-chrome") or shutil.which("chromium")
SPEC = importlib.util.spec_from_file_location("render_knowledge_map_site", SCRIPT)
assert SPEC and SPEC.loader
RENDERER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDERER)


def concept(identifier: str, title: str, summary: str = "Modern definition") -> dict[str, object]:
    return {
        "id": identifier, "title": title, "summary": summary, "kind": "foundation",
        "tracks": [], "case_labs": [], "lessons": [], "records": [],
        "path": f"concepts/{identifier}.md", "mastery": {"status": "not-started"},
        "relationships": {"prerequisites": [], "enables": [], "contrasts_with": [], "related": []},
        "extensions": {},
    }


def graph(*nodes: dict[str, object]) -> dict[str, object]:
    return {"schema_version": 1, "nodes": list(nodes), "edges": [], "tracks": [], "case_labs": []}


LEARNING_STATE = {"schema_version": 1, "concepts": [], "resume": None}


class TestKnowledgeMapSiteRender(unittest.TestCase):
    maxDiff = None

    def render(self, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT), "--root", str(REPOSITORY_ROOT), "--output", str(output)],
            check=False, text=True, capture_output=True,
        )

    def normalized(self, script: str) -> object:
        result = subprocess.run(
            ["python3", str(REPOSITORY_ROOT / "scripts" / script), "normalized-data", "--root", str(REPOSITORY_ROOT)],
            check=False, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def browser_dump(self, source: Path, fragment: str, probe: str = "") -> str:
        self.assertIsNotNone(CHROME, "Chrome or Chromium is required for renderer semantic checks")
        target = source
        if probe:
            target = source.with_name(f"{source.stem}-instrumented.html")
            target.write_text(
                source.read_text(encoding="utf-8").replace(
                    "</body>",
                    f"<script>window.addEventListener('load',()=>{{{probe}}});</script></body>",
                ),
                encoding="utf-8",
            )
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            environment = os.environ.copy()
            environment.update({"TMPDIR": str(temporary), "XDG_CONFIG_HOME": str(temporary / "config"), "XDG_CACHE_HOME": str(temporary / "cache")})
            result = subprocess.run(
                [str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-breakpad", "--disable-crash-reporter", f"--user-data-dir={temporary / 'profile'}", "--dump-dom", target.as_uri() + fragment],
                check=False, text=True, capture_output=True, timeout=25, env=environment,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def rendered_region(self, source: Path, fragment: str, selector: str) -> str:
        probe = (
            f"const target=document.querySelector({json.dumps(selector)});"
            "if(!target)throw new Error('missing rendered region');"
            "document.body.replaceChildren(target.cloneNode(true));"
        )
        return self.browser_dump(source, fragment, probe)

    @staticmethod
    def embedded(content: str, name: str, following: str) -> object:
        matched = re.search(rf"const {name}\s*=\s*(\{{.*?\}});\s*const {following}\s*=", content, flags=re.DOTALL)
        if matched is None:
            raise AssertionError(f"missing embedded {name} payload")
        return json.loads(matched.group(1))

    @unittest.skipUnless(CHROME, "Chrome or Chromium is not installed")
    def test_terminology_is_optional_escaped_and_limited_to_safe_https_sources(self) -> None:
        term = concept("term", "Term")
        term["extensions"] = {"terminology": {"preferred_english_term": "Term <script>unsafe()</script>", "checked_on": "2026-08-21", "sources": [{"url": "https://example.org/spec?a=1&b=2", "publisher": "Example <Org>", "kind": "standard"}, {"url": "javascript:alert(1)", "publisher": "Unsafe", "kind": "blog"}]}}
        without = concept("without-term", "Without terminology")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "terminology.html"
            output.write_text(RENDERER.render_html(graph(term, without), LEARNING_STATE), encoding="utf-8")
            term_dom = self.rendered_region(output, "#concept=term", "#panel")
            absent_dom = self.rendered_region(output, "#concept=without-term", "#panel")

        self.assertIn("术语来源", term_dom)
        self.assertIn("Term &lt;script&gt;unsafe()&lt;/script&gt;", term_dom)
        self.assertIn("Example &lt;Org&gt;", term_dom)
        self.assertIn('href="https://example.org/spec?a=1&amp;b=2"', term_dom)
        self.assertIn('target="_blank"', term_dom)
        self.assertIn('rel="noopener noreferrer"', term_dom)
        self.assertNotIn("javascript:alert", term_dom)
        self.assertNotIn("Unsafe", term_dom)
        self.assertNotIn("术语来源", absent_dom)

    @unittest.skipUnless(CHROME, "Chrome or Chromium is not installed")
    def test_history_semantics_cover_reverse_membership_recall_and_deep_links(self) -> None:
        primary = concept("idempotency", "Idempotency")
        missing = concept("without-history", "Without history")
        history = {"schema_version": 1, "dossiers": [
            {"id": "idempotency-history", "title": "History of idempotency", "summary": "Evidence-backed lineage", "path": "histories/idempotency.md", "concepts": ["idempotency"], "lessons": [], "tracks": [], "milestones": [
                {"id": "later", "year": 1997, "month": 11, "day": 1, "kind": "adoption", "claim": "Later claim", "actors": [], "sources": [{"url": "https://example.org/rfc", "title": "RFC", "role": "primary"}]},
                {"id": "earlier", "year": 1870, "month": None, "day": None, "kind": "terminology", "claim": "Earlier claim", "actors": [], "sources": [{"url": "http://unsafe.example", "title": "Unsafe", "role": "primary"}]},
            ]},
            {"id": "lesson-only-history", "title": "Lesson-only history", "summary": "Lesson-only evidence", "path": "histories/lesson-only.md", "concepts": [], "lessons": ["lessons/e-value.md"], "tracks": [], "milestones": [{"id": "lesson", "year": 1990, "month": 3, "day": None, "kind": "formalization", "claim": "Lesson claim", "actors": [], "sources": []}]},
        ]}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "history.html"
            output.write_text(RENDERER.render_html(graph(primary, missing), LEARNING_STATE, history), encoding="utf-8")
            overview = self.rendered_region(output, "#concept=idempotency&view=history", "#history-overlay")
            timeline = self.rendered_region(output, "#history=idempotency-history&view=history", "#history-overlay")
            recall = self.rendered_region(output, "#history=idempotency-history&view=history&recall=1", "#history-overlay")
            no_history = self.rendered_region(output, "#concept=without-history&view=history", "#history-overlay")
            lesson_only = self.rendered_region(output, "#history=lesson-only-history&view=history", "#history-overlay")
            invalid = self.browser_dump(
                output,
                "#history=missing&view=history",
                "const target=document.querySelector('#history-overlay');"
                "const route=document.createElement('output');"
                "route.dataset.route=location.hash;"
                "document.body.replaceChildren(target.cloneNode(true),route);",
            )

        self.assertIn("History of idempotency", overview)
        self.assertNotIn("Lesson-only history", overview)
        self.assertLess(timeline.index("1870"), timeline.index("1997"))
        self.assertIn("Earlier claim", timeline)
        self.assertIn("Later claim", timeline)
        self.assertIn('href="https://example.org/rfc"', timeline)
        self.assertIn('target="_blank"', timeline)
        self.assertIn('rel="noopener noreferrer"', timeline)
        self.assertNotIn("Unsafe", timeline)
        self.assertNotIn("http://unsafe.example", timeline)
        self.assertIn("这条记录解决、形式化或批评了什么？", recall)
        self.assertNotIn("Earlier claim", recall)
        self.assertNotIn("Later claim", recall)
        self.assertNotIn("Modern definition", recall)
        self.assertIn("尚无可核查的历史谱系", no_history)
        self.assertIn("Lesson-only history", lesson_only)
        self.assertIn("Lesson-only evidence", lesson_only)
        self.assertIn("lessons/e-value.md", lesson_only)
        self.assertIn("Lesson claim", lesson_only)
        self.assertIn("打开证据档案", lesson_only)
        self.assertIn("History of idempotency", invalid)
        self.assertIn('data-route="#view=history"', invalid)

    def test_wrapper_is_deterministic_self_contained_and_embeds_exact_canonical_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            first, second = temporary / "first.html", temporary / "second.html"
            first_result, second_result = self.render(first), self.render(second)
            self.assertEqual(first_result.returncode, 0, first_result.stderr)
            self.assertEqual(second_result.returncode, 0, second_result.stderr)
            content = first.read_text(encoding="utf-8")
            self.assertEqual(content, second.read_text(encoding="utf-8"))

        self.assertEqual(self.embedded(content, "GRAPH", "LEARNING_STATE"), self.normalized("build-knowledge-map.py"))
        self.assertEqual(self.embedded(content, "LEARNING_STATE", "HISTORY"), self.normalized("build-learning-state.py"))
        self.assertEqual(self.embedded(content, "HISTORY", "byId"), self.normalized("build-knowledge-history.py"))
        self.assertNotRegex(content, r"(?i)<script[^>]+\bsrc=")
        self.assertNotRegex(content, r"(?i)<link[^>]+\bhref=")
        self.assertNotRegex(content, r"\bfetch\s*\(")
        self.assertNotRegex(content, r"\bimport\s*\(")

    def test_wrapper_reports_the_node_22_and_npm_ci_recovery_contract(self) -> None:
        with mock.patch.object(RENDERER.shutil, "which", return_value=None):
            with self.assertRaises(RuntimeError) as missing:
                RENDERER.node_runtime()
        self.assertEqual(str(missing.exception), RENDERER.RUNTIME_DIAGNOSTIC)

        wrong_version = subprocess.CompletedProcess(
            ["node", "--version"],
            0,
            stdout="v21.7.3\n",
            stderr="",
        )
        with (
            mock.patch.object(RENDERER.shutil, "which", return_value="/fake/node"),
            mock.patch.object(RENDERER.subprocess, "run", return_value=wrong_version),
            self.assertRaises(RuntimeError) as wrong,
        ):
            RENDERER.node_runtime()
        self.assertEqual(str(wrong.exception), RENDERER.RUNTIME_DIAGNOSTIC)

        missing_dependencies = subprocess.CompletedProcess(
            ["node", "frontend/build.mjs"],
            1,
            stdout="",
            stderr=(
                "knowledge map frontend build failed: Learning Lab frontend "
                "dependencies are missing. Run npm ci with Node.js 22.x."
            ),
        )
        with (
            mock.patch.object(RENDERER, "node_runtime", return_value="/fake/node"),
            mock.patch.object(
                RENDERER.subprocess,
                "run",
                return_value=missing_dependencies,
            ),
            self.assertRaises(RuntimeError) as dependencies,
        ):
            RENDERER.run_frontend_build(REPOSITORY_ROOT, Path("ignored.html"))
        self.assertEqual(
            str(dependencies.exception),
            RENDERER.RUNTIME_DIAGNOSTIC,
        )

    @unittest.skipUnless(CHROME, "Chrome or Chromium is not installed")
    def test_rendered_site_reports_the_typescript_runtime_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "index.html"
            result = self.render(output)
            self.assertEqual(result.returncode, 0, result.stderr)
            dom = self.browser_dump(output, "#concept=idempotency")
        self.assertIn('data-learning-lab-frontend="typescript"', dom)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestKnowledgeMapSiteRender)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

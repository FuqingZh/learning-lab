#!/usr/bin/env python3
"""Static and deterministic contracts for the offline map projection."""

from __future__ import annotations

import json
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY_ROOT / "scripts" / "render-knowledge-map-site.py"
CHROME = shutil.which("google-chrome") or shutil.which("chromium")
SPEC = importlib.util.spec_from_file_location("render_knowledge_map_site", SCRIPT)
assert SPEC and SPEC.loader
RENDERER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RENDERER)


class TestKnowledgeMapSiteRender(unittest.TestCase):
    def test_optional_terminology_projection_is_escaped_and_omitted_when_absent(self) -> None:
        node = {
            "id": "term", "title": "Term", "summary": "A term", "kind": "foundation",
            "tracks": [], "case_labs": [], "lessons": [], "records": [], "path": "concepts/term.md",
            "mastery": {"status": "not-started"},
            "relationships": {"prerequisites": [], "enables": [], "contrasts_with": [], "related": []},
            "extensions": {"terminology": {"preferred_english_term": "Term", "checked_on": "2026-08-21", "sources": [
                {"url": "https://example.org/spec?a=1&b=2", "publisher": "Example <Org>", "kind": "standard"},
            ]}},
        }
        graph = {"schema_version": 1, "nodes": [node], "edges": [], "tracks": [], "case_labs": []}
        learning_state = {"schema_version": 1, "concepts": [], "resume": None}
        rendered = RENDERER.render_html(graph, learning_state)
        self.assertIn("术语来源", rendered)
        self.assertIn("Example \\u003cOrg\\u003e", rendered)
        self.assertIn('target="_blank" rel="noopener noreferrer"', rendered)
        self.assertIn('safeHttps(url)', rendered)

        node["extensions"] = {}
        without_terminology = RENDERER.render_html(graph, learning_state)
        self.assertNotIn('"terminology"', without_terminology)
    def render(self, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT), "--root", str(REPOSITORY_ROOT), "--output", str(output)],
            check=False,
            text=True,
            capture_output=True,
        )

    def test_render_is_deterministic_and_self_contained(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.html"
            second = Path(directory) / "second.html"
            first_result = self.render(first)
            second_result = self.render(second)
            self.assertEqual(first_result.returncode, 0, first_result.stderr)
            self.assertEqual(second_result.returncode, 0, second_result.stderr)
            content = first.read_text(encoding="utf-8")
            self.assertEqual(content, second.read_text(encoding="utf-8"))

        self.assertIn("const GRAPH =", content)
        self.assertIn("const LEARNING_STATE =", content)
        self.assertIn("const HISTORY =", content)
        self.assertIn("normalized-data", SCRIPT.read_text(encoding="utf-8"))
        self.assertIn('id="space"', content)
        self.assertIn('id="nodes"', content)
        self.assertIn('id="edges"', content)
        self.assertIn('id="chapter-rail"', content)
        self.assertIn('id="panel"', content)
        self.assertIn('id="search"', content)
        self.assertIn('id="today-open"', content)
        self.assertIn('id="continue-open"', content)
        self.assertIn('id="recall-toggle"', content)
        self.assertIn("function localToday()", content)
        self.assertIn("function dueConcepts()", content)
        self.assertIn('state={yaw:', content)
        self.assertIn('space.onpointermove', content)
        self.assertIn('state.zoom=Math.max', content)
        self.assertIn('location.hash.slice(1)', content)
        self.assertIn('python3 -m http.server 8000 --bind 127.0.0.1', content)
        self.assertIn('http://localhost:8000/site/', content)
        self.assertNotRegex(content, r"(?i)<script[^>]+\bsrc=")
        self.assertNotRegex(content, r"(?i)<link[^>]+\bhref=")
        self.assertNotRegex(content, r"\bfetch\s*\(")
        self.assertNotRegex(content, r"(?i)(?:src|href)=[\"']https?://")

    def test_rendered_data_has_canonical_paths_and_case_lab_projection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "index.html"
            result = self.render(output)
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output.read_text(encoding="utf-8")

        self.assertIn('"path":"concepts/idempotency.md"', content)
        self.assertIn('"path":"case-labs/seqevi.md"', content)
        self.assertIn('"direct_concepts"', content)
        self.assertIn('function canonical(path)', content)
        self.assertIn('没有匹配的知识点', content)
        script_bodies = re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", content, flags=re.DOTALL)
        self.assertIsNone(re.search(r"file://|localhost", "\n".join(script_bodies)))

        embedded_match = re.search(
            r"const GRAPH = (\{.*?\});\nconst LEARNING_STATE =",
            content,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(embedded_match)
        embedded = json.loads(embedded_match.group(1))
        normalized = subprocess.run(
            [
                "python3",
                str(REPOSITORY_ROOT / "scripts" / "build-knowledge-map.py"),
                "normalized-data",
                "--root",
                str(REPOSITORY_ROOT),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertEqual(embedded, json.loads(normalized.stdout))

        learning_match = re.search(
            r"const LEARNING_STATE = (\{.*?\});\nconst HISTORY =",
            content,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(learning_match)
        normalized_learning_state = subprocess.run(
            [
                "python3",
                str(REPOSITORY_ROOT / "scripts" / "build-learning-state.py"),
                "normalized-data",
                "--root",
                str(REPOSITORY_ROOT),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertEqual(json.loads(learning_match.group(1)), json.loads(normalized_learning_state.stdout))

        history_match = re.search(
            r"const HISTORY = (\{.*?\});\nconst byId=",
            content,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(history_match)
        normalized_history = subprocess.run(
            [
                "python3",
                str(REPOSITORY_ROOT / "scripts" / "build-knowledge-history.py"),
                "normalized-data",
                "--root",
                str(REPOSITORY_ROOT),
            ],
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertEqual(json.loads(history_match.group(1)), json.loads(normalized_history.stdout))

    def test_history_projection_preserves_membership_date_precision_and_safe_sources(self) -> None:
        graph = {"schema_version": 1, "nodes": [{
            "id": "idempotency", "title": "Idempotency", "summary": "Modern definition", "kind": "foundation",
            "tracks": [], "case_labs": [], "lessons": [], "records": [], "path": "concepts/idempotency.md",
            "mastery": {"status": "not-started"},
            "relationships": {"prerequisites": [], "enables": [], "contrasts_with": [], "related": []}, "extensions": {},
        }], "edges": [], "tracks": [], "case_labs": []}
        history = {"schema_version": 1, "dossiers": [{
            "id": "idempotency-history", "title": "History", "summary": "", "path": "histories/idempotency.md",
            "concepts": ["idempotency"], "lessons": [], "tracks": [], "milestones": [
                {"id": "http", "year": 1997, "month": 11, "day": None, "kind": "adoption", "actors": ["IETF"], "claim": "HTTP claim", "sources": [{"url": "https://example.org/rfc", "title": "RFC", "publisher": "IETF", "role": "primary", "kind": "standard"}]},
                {"id": "algebra", "year": 1870, "month": None, "day": None, "kind": "terminology", "actors": ["Peirce"], "claim": "Algebra claim", "sources": [{"url": "javascript:alert(1)", "title": "Unsafe", "publisher": "", "role": "scholarly-secondary", "kind": "monograph"}]},
            ],
        }]}
        rendered = RENDERER.render_html(graph, {"schema_version": 1, "concepts": [], "resume": None}, history)
        self.assertIn('id="history-mode"', rendered)
        self.assertIn("historyDossiers(id)", rendered)
        self.assertIn("dateLabel(m)", rendered)
        self.assertIn("a.year-b.year||(a.month||0)-(b.month||0)||(a.day||0)-(b.day||0)", rendered)
        self.assertIn('href="${esc(safeHttps(s.url))}"', rendered)
        self.assertIn("尚无可核查的历史谱系", rendered)
        self.assertIn("不展示现代定义或概念关系", rendered)
        self.assertIn("function updateGraphHash()", rendered)
        self.assertIn("打开证据档案", rendered)

    @unittest.skipUnless(CHROME, "Chrome or Chromium is not installed")
    def test_browser_history_timeline_recall_and_no_history_states(self) -> None:
        nodes = []
        for identifier, title in (("idempotency", "Idempotency"), ("without-history", "Without history")):
            nodes.append({"id": identifier, "title": title, "summary": "Modern definition", "kind": "foundation", "tracks": [], "case_labs": [], "lessons": [], "records": [], "path": f"concepts/{identifier}.md", "mastery": {"status": "not-started"}, "relationships": {"prerequisites": [], "enables": [], "contrasts_with": [], "related": []}, "extensions": {}})
        graph = {"schema_version": 1, "nodes": nodes, "edges": [], "tracks": [], "case_labs": []}
        history = {"schema_version": 1, "dossiers": [
            {"id": "idempotency-history", "title": "History", "summary": "", "path": "histories/idempotency.md", "concepts": ["idempotency"], "lessons": [], "tracks": [], "milestones": [{"id": "early", "year": 1870, "month": None, "day": None, "kind": "terminology", "actors": ["Peirce"], "claim": "Historical claim", "sources": [{"url": "https://example.org/source", "title": "Primary source", "publisher": "", "role": "primary", "kind": "monograph"}]}]},
            {"id": "e-value-history", "title": "History of E-value", "summary": "Lesson-only evidence", "path": "histories/e-value.md", "concepts": [], "lessons": ["lessons/e-value.md"], "tracks": [], "milestones": [{"id": "karlin", "year": 1990, "month": 3, "day": None, "kind": "formalization", "actors": ["Karlin"], "claim": "E-value claim", "sources": [{"url": "https://example.org/evalue", "title": "E-value source", "publisher": "", "role": "primary", "kind": "paper"}]}]},
        ]}
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            output = temporary / "history.html"
            rendered = RENDERER.render_html(graph, {"schema_version": 1, "concepts": [], "resume": None}, history)
            output.write_text(rendered, encoding="utf-8")
            interaction_output = temporary / "interaction.html"
            interaction_output.write_text(
                rendered.replace(
                    "</body>",
                    '<script>window.addEventListener("load",()=>{document.querySelector("#graph-mode").click();document.body.dataset.graphHash=location.hash;document.body.dataset.panelOpen=String(document.querySelector("#panel").classList.contains("open")&&!document.querySelector("#panel").hidden);document.body.dataset.introHidden=String(document.querySelector("#intro").hidden||document.querySelector("#intro").classList.contains("hidden"));document.querySelector("#history-mode").click();document.body.dataset.historyHash=location.hash})</script></body>',
                ),
                encoding="utf-8",
            )
            narrow_output = temporary / "narrow.html"
            narrow_output.write_text(
                rendered.replace(
                    "</body>",
                    '<script>window.addEventListener("load",()=>{const search=document.querySelector(".search").getBoundingClientRect(),card=document.querySelector(".learning-card").getBoundingClientRect();document.body.dataset.headerOverlap=String(search.bottom>card.top)})</script></body>',
                ),
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment.update({"TMPDIR": str(temporary), "XDG_CONFIG_HOME": str(temporary / "config"), "XDG_CACHE_HOME": str(temporary / "cache")})
            browser = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-breakpad", "--disable-crash-reporter", f"--user-data-dir={temporary / 'user'}", "--dump-dom", output.as_uri() + "#concept=idempotency&history=idempotency-history&view=history&recall=1"], check=False, text=True, capture_output=True, timeout=25, env=environment)
            self.assertEqual(browser.returncode, 0, browser.stderr)
            self.assertIn('id="history-overlay"', browser.stdout)
            self.assertIn("1870", browser.stdout)
            self.assertIn('class="source-role">primary</span> · Primary source ↗', browser.stdout)
            self.assertIn("这条记录解决、形式化或批评了什么？", browser.stdout)
            history_dom = browser.stdout.split('id="history-overlay"', 1)[1].split("</main>", 1)[0]
            self.assertNotIn("Modern definition", history_dom)
            self.assertIn('href="https://example.org/source"', browser.stdout)
            no_history = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-breakpad", "--disable-crash-reporter", f"--user-data-dir={temporary / 'no-history-user'}", "--dump-dom", output.as_uri() + "#concept=without-history&view=history"], check=False, text=True, capture_output=True, timeout=25, env=environment)
            self.assertEqual(no_history.returncode, 0, no_history.stderr)
            self.assertIn("尚无可核查的历史谱系", no_history.stdout)
            lesson_only = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-breakpad", "--disable-crash-reporter", f"--user-data-dir={temporary / 'lesson-only-user'}", "--dump-dom", output.as_uri() + "#history=e-value-history&view=history"], check=False, text=True, capture_output=True, timeout=25, env=environment)
            self.assertEqual(lesson_only.returncode, 0, lesson_only.stderr)
            self.assertIn("History of E-value", lesson_only.stdout)
            self.assertIn("Lesson-only evidence", lesson_only.stdout)
            self.assertIn("lessons/e-value.md", lesson_only.stdout)
            self.assertIn("E-value claim", lesson_only.stdout)
            self.assertIn("打开证据档案", lesson_only.stdout)
            overview = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-breakpad", "--disable-crash-reporter", f"--user-data-dir={temporary / 'overview-user'}", "--dump-dom", output.as_uri() + "#view=history"], check=False, text=True, capture_output=True, timeout=25, env=environment)
            self.assertEqual(overview.returncode, 0, overview.stderr)
            self.assertIn('data-history-id="e-value-history"', overview.stdout)
            self.assertIn('data-history-id="idempotency-history"', overview.stdout)
            invalid = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-breakpad", "--disable-crash-reporter", f"--user-data-dir={temporary / 'invalid-history-user'}", "--dump-dom", output.as_uri() + "#history=missing&view=history"], check=False, text=True, capture_output=True, timeout=25, env=environment)
            self.assertEqual(invalid.returncode, 0, invalid.stderr)
            self.assertIn('data-history-id="e-value-history"', invalid.stdout)
            self.assertNotIn("#history=missing", invalid.stdout)
            interaction = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-breakpad", "--disable-crash-reporter", f"--user-data-dir={temporary / 'interaction-user'}", "--dump-dom", interaction_output.as_uri() + "#concept=idempotency&view=history"], check=False, text=True, capture_output=True, timeout=25, env=environment)
            self.assertEqual(interaction.returncode, 0, interaction.stderr)
            self.assertIn('data-graph-hash="#concept=idempotency"', interaction.stdout)
            self.assertIn('data-panel-open="true"', interaction.stdout)
            self.assertIn('data-intro-hidden="true"', interaction.stdout)
            self.assertIn('data-history-hash="#view=history&amp;concept=idempotency"', interaction.stdout)
            narrow = subprocess.run([str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-breakpad", "--disable-crash-reporter", "--window-size=320,844", f"--user-data-dir={temporary / 'narrow-user'}", "--dump-dom", narrow_output.as_uri() + "#view=history"], check=False, text=True, capture_output=True, timeout=25, env=environment)
            self.assertEqual(narrow.returncode, 0, narrow.stderr)
            self.assertIn('data-header-overlap="false"', narrow.stdout)

    @unittest.skipUnless(CHROME, "Chrome or Chromium is not installed")
    def test_installed_browser_executes_graph_and_accessible_node_list(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            output = temporary / "site" / "index.html"
            result = self.render(output)
            self.assertEqual(result.returncode, 0, result.stderr)
            profile = temporary / "profile"
            runtime = temporary / "runtime"
            cache = temporary / "cache"
            profile.mkdir()
            runtime.mkdir()
            cache.mkdir()
            environment = os.environ.copy()
            environment.update(
                {
                    "TMPDIR": str(runtime),
                    "XDG_CONFIG_HOME": str(profile / "config"),
                    "XDG_CACHE_HOME": str(cache),
                }
            )
            browser = subprocess.run(
                [
                    str(CHROME),
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-breakpad",
                    "--disable-crash-reporter",
                    f"--user-data-dir={profile / 'user'}",
                    f"--disk-cache-dir={cache}",
                    "--dump-dom",
                    output.as_uri() + "#concept=idempotency&learning=today&recall=1",
                ],
                check=False,
                text=True,
                capture_output=True,
                timeout=25,
                env=environment,
            )
            self.assertEqual(browser.returncode, 0, browser.stderr)
            normalized_graph = subprocess.run(
                [
                    "python3",
                    str(REPOSITORY_ROOT / "scripts" / "build-knowledge-map.py"),
                    "normalized-data",
                    "--root",
                    str(REPOSITORY_ROOT),
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            expected_node_count = len(json.loads(normalized_graph.stdout)["nodes"])
            self.assertEqual(browser.stdout.count('class="concept '), expected_node_count)
            accessible = re.search(
                r'<div class="sr-only" id="concept-list">(.*?)</div>',
                browser.stdout,
                flags=re.DOTALL,
            )
            self.assertIsNotNone(accessible)
            self.assertEqual(
                accessible.group(1).count('data-accessible="'), expected_node_count
            )
            self.assertEqual(browser.stdout.count('class="edge '), 0)
            self.assertIn("Partial failure — not started", browser.stdout)
            self.assertIn('class="panel open"', browser.stdout)
            self.assertIn("打开源知识卡", browser.stdout)
            self.assertIn("能力与复习", browser.stdout)
            self.assertIn("三分钟，继续一小步。", browser.stdout)
            self.assertIn('class="learning-view open"', browser.stdout)
            self.assertIn("现在适合回忆的概念", browser.stdout)
            self.assertIn("答案已隐藏。", browser.stdout)
            self.assertNotIn('data-target="logical-operation"', browser.stdout)

            today = subprocess.run(
                [
                    str(CHROME),
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-breakpad",
                    "--disable-crash-reporter",
                    f"--user-data-dir={profile / 'today-user'}",
                    "--dump-dom",
                    output.as_uri() + "#learning=continue",
                ],
                check=False,
                text=True,
                capture_output=True,
                timeout=25,
                env=environment,
            )
            self.assertEqual(today.returncode, 0, today.stderr)
            self.assertIn('class="learning-view open"', today.stdout)
            self.assertIn("Continue", today.stdout)
            self.assertIn("Partial failure", today.stdout)

            term_node = {
                "id": "term", "title": "Term", "summary": "A term", "kind": "foundation",
                "tracks": [], "case_labs": [], "lessons": [], "records": [], "path": "concepts/term.md",
                "mastery": {"status": "not-started"},
                "relationships": {"prerequisites": [], "enables": [], "contrasts_with": [], "related": []},
                "extensions": {"terminology": {"preferred_english_term": "Term", "checked_on": "2026-08-21", "sources": [
                    {"url": "https://example.org/spec", "publisher": "Example Org", "kind": "standard"},
                ]}},
            }
            term_output = temporary / "terminology.html"
            term_output.write_text(
                RENDERER.render_html(
                    {"schema_version": 1, "nodes": [term_node], "edges": [], "tracks": [], "case_labs": []},
                    {"schema_version": 1, "concepts": [], "resume": None},
                ),
                encoding="utf-8",
            )
            terminology = subprocess.run(
                [
                    str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
                    "--disable-breakpad", "--disable-crash-reporter",
                    f"--user-data-dir={profile / 'terminology-user'}", "--dump-dom",
                    term_output.as_uri() + "#concept=term",
                ],
                check=False, text=True, capture_output=True, timeout=25, env=environment,
            )
            self.assertEqual(terminology.returncode, 0, terminology.stderr)
            self.assertIn("术语来源", terminology.stdout)
            self.assertIn("Example Org · standard", terminology.stdout)
            self.assertIn('href="https://example.org/spec"', terminology.stdout)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestKnowledgeMapSiteRender)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

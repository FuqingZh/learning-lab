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
        self.assertIsNone(re.search(r"file://|localhost", content.split("<script>", 1)[1]))

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
            r"const LEARNING_STATE = (\{.*?\});\nconst byId=",
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

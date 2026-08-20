#!/usr/bin/env python3
"""Static and deterministic contracts for the offline map projection."""

from __future__ import annotations

import json
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


class TestKnowledgeMapSiteRender(unittest.TestCase):
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
        self.assertIn("normalized-data", SCRIPT.read_text(encoding="utf-8"))
        self.assertIn('id="space"', content)
        self.assertIn('id="nodes"', content)
        self.assertIn('id="edges"', content)
        self.assertIn('id="chapter-rail"', content)
        self.assertIn('id="panel"', content)
        self.assertIn('id="search"', content)
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
            r"const GRAPH = (\{.*?\});\nconst byId=",
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
                    output.as_uri() + "#concept=idempotency",
                ],
                check=False,
                text=True,
                capture_output=True,
                timeout=25,
                env=environment,
            )
            self.assertEqual(browser.returncode, 0, browser.stderr)
            self.assertEqual(browser.stdout.count('class="concept '), 9)
            accessible = re.search(
                r'<div class="sr-only" id="concept-list">(.*?)</div>',
                browser.stdout,
                flags=re.DOTALL,
            )
            self.assertIsNotNone(accessible)
            self.assertEqual(accessible.group(1).count('data-accessible="'), 9)
            self.assertEqual(browser.stdout.count('class="edge '), 18)
            self.assertIn("Partial failure — not started", browser.stdout)
            self.assertIn('class="panel open"', browser.stdout)
            self.assertIn("打开源知识卡", browser.stdout)


def main() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestKnowledgeMapSiteRender)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Focused checks for deterministic, navigable generated Markdown maps."""

from __future__ import annotations

import re
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RENDERER = REPOSITORY_ROOT / "scripts" / "render-knowledge-map-markdown.py"
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def snapshot(directory: Path) -> dict[str, bytes]:
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*.md"))
    }


class TestKnowledgeMapMarkdownRender(unittest.TestCase):
    def render(self, output: Path) -> None:
        result = subprocess.run(
            [
                "python3",
                str(RENDERER),
                "--root",
                str(REPOSITORY_ROOT),
                "--output",
                str(output),
            ],
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_render_is_idempotent_and_all_local_links_resolve(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "maps"
            self.render(output)
            first = snapshot(output)
            self.render(output)
            self.assertEqual(first, snapshot(output))

            self.assertIn("README.md", first)
            self.assertIn("overview.md", first)
            self.assertIn("concepts/idempotency.md", first)
            self.assertIn("case-labs/seqevi.md", first)

            for document in sorted(output.rglob("*.md")):
                content = document.read_text(encoding="utf-8")
                for target in MARKDOWN_LINK.findall(content):
                    with self.subTest(document=document.relative_to(output), target=target):
                        self.assertFalse(target.startswith(("http://", "https://", "#")))
                        target_path = (document.parent / target).resolve()
                        self.assertTrue(target_path.is_file(), target_path)

            idempotency = (output / "concepts" / "idempotency.md").read_text(encoding="utf-8")
            self.assertIn("## Typed local graph", idempotency)
            self.assertIn("|prerequisite|", idempotency)
            self.assertIn("Reviewed capability: `unassessed`", idempotency)
            self.assertIn("Legacy filename label: `mastered`", idempotency)
            self.assertIn("Effective reviewed record: none", idempotency)
            self.assertIn("Prerequisite: [Partial failure]", idempotency)
            for retired in (
                "authoritative-readback.md",
                "logical-operation.md",
                "operation-scope.md",
                "response-equality.md",
                "retry-safe-operation.md",
            ):
                self.assertNotIn(f"concepts/{retired}", first)
            seqevi = (output / "case-labs" / "seqevi.md").read_text(encoding="utf-8")
            self.assertIn("## Strict membership", seqevi)
            self.assertIn("hub alone does not create membership", seqevi)


if __name__ == "__main__":
    unittest.main()

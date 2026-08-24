#!/usr/bin/env python3
"""Focused contract tests for scripts/build-knowledge-history.py."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY_ROOT / "scripts" / "build-knowledge-history.py"


def dossier_document(identifier: str = "alpha-history", **overrides: object) -> str:
    fields: dict[str, object] = {
        "schema_version": 1,
        "id": identifier,
        "title": "History of alpha",
        "summary": "How alpha entered current practice.",
        "concepts": ["alpha"],
        "lessons": [],
        "tracks": ["track-a"],
        "milestones": [
            {
                "id": "alpha-2000",
                "year": 2000,
                "month": None,
                "day": None,
                "kind": "terminology",
                "actors": ["Ada Example"],
                "claim": "A source documented alpha.",
                "evidence_basis": "primary-source",
                "sources": [
                    {
                        "url": "https://primary.example/alpha",
                        "title": "Alpha document",
                        "publisher": "Example Archive",
                        "role": "primary",
                        "kind": "archive",
                    }
                ],
            }
        ],
    }
    fields.update(overrides)
    return "---\n" + json.dumps(fields, ensure_ascii=False, indent=2) + "\n---\n\n" + "\n".join(
        f"## {heading}\n\nEvidence boundary."
        for heading in (
            "Historical setting",
            "What the sources establish",
            "What the sources do not establish",
            "Development",
            "Modern boundary",
        )
    )


class TestKnowledgeHistoryValidation(unittest.TestCase):
    def create_root(self) -> tempfile.TemporaryDirectory[str]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "concepts").mkdir()
        (root / "tracks" / "track-a").mkdir(parents=True)
        (root / "lessons" / "track-a").mkdir(parents=True)
        (root / "histories").mkdir()
        (root / "concepts" / "alpha.md").write_text("---\nid: alpha\n---\n", encoding="utf-8")
        (root / "concepts" / "beta.md").write_text("---\nid: beta\n---\n", encoding="utf-8")
        (root / "lessons" / "track-a" / "lesson.md").write_text("# lesson\n", encoding="utf-8")
        return temporary

    def write_dossier(self, root: Path, filename: str = "alpha-history.md", **overrides: object) -> Path:
        path = root / "histories" / filename
        path.write_text(dossier_document(**overrides), encoding="utf-8")
        return path

    def run_cli(self, root: Path, command: str = "validate") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT), command, "--root", str(root)],
            check=False, text=True, capture_output=True,
        )

    def assert_rejected(self, root: Path, expected: str) -> None:
        result = self.run_cli(root)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected, result.stderr)

    def test_normalized_history_is_deterministic_and_sorts_all_lists(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_dossier(
                root,
                concepts=["beta", "alpha"],
                lessons=["lessons/track-a/lesson.md"],
                milestones=[
                    {
                        "id": "later",
                        "year": 2001,
                        "month": 2,
                        "day": 3,
                        "kind": "popularization",
                        "actors": ["Zed", "Ada"],
                        "claim": "Later adoption.",
                        "evidence_basis": "mixed",
                        "sources": [
                            {"url": "https://secondary.example/later", "title": "Analysis", "publisher": "Journal", "role": "scholarly-secondary", "kind": "paper"},
                            {"url": "https://primary.example/later", "title": "Standard", "publisher": "Standards", "role": "primary", "kind": "standard"},
                        ],
                    },
                    {
                        "id": "earlier",
                        "year": 2000,
                        "month": None,
                        "day": None,
                        "kind": "terminology",
                        "actors": ["Ada"],
                        "claim": "Earlier terminology.",
                        "evidence_basis": "primary-source",
                        "sources": [{"url": "https://primary.example/earlier", "title": "Archive", "publisher": "Archive", "role": "primary", "kind": "archive"}],
                    },
                ],
            )
            first = self.run_cli(root, "normalized-data")
            second = self.run_cli(root, "normalized-data")
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(first.stdout, second.stdout)
            history = json.loads(first.stdout)
            dossier = history["dossiers"][0]
            self.assertEqual(dossier["path"], "histories/alpha-history.md")
            self.assertEqual(dossier["concepts"], ["alpha", "beta"])
            self.assertEqual([item["id"] for item in dossier["milestones"]], ["earlier", "later"])
            self.assertEqual(dossier["milestones"][1]["actors"], ["Ada", "Zed"])
            self.assertEqual(dossier["milestones"][1]["sources"][0]["url"], "https://primary.example/later")

    def test_rejects_duplicate_yaml_keys_and_contract_fields(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            path = self.write_dossier(root)
            path.write_text(path.read_text(encoding="utf-8").replace('"id": "alpha-history",', '"id": "alpha-history",\n  "id": "alpha-history",'), encoding="utf-8")
            self.assert_rejected(root, "duplicate key 'id'")

        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_dossier(root, reviewer_note="not a v1 field")
            self.assert_rejected(root, "dossier has unknown fields: reviewer_note")

        with self.create_root() as temporary:
            root = Path(temporary)
            path = self.write_dossier(root)
            path.write_text(path.read_text(encoding="utf-8").replace('"summary": "How alpha entered current practice.",\n', ""), encoding="utf-8")
            self.assert_rejected(root, "dossier missing required fields: summary")

        for invalid_version in ("true", "1.0"):
            with self.subTest(schema_version=invalid_version), self.create_root() as temporary:
                root = Path(temporary)
                path = self.write_dossier(root)
                path.write_text(
                    path.read_text(encoding="utf-8").replace('"schema_version": 1', f'"schema_version": {invalid_version}'),
                    encoding="utf-8",
                )
                self.assert_rejected(root, "schema_version must be 1")

    def test_rejects_identity_membership_and_reference_violations(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_dossier(root, filename="wrong-name.md")
            self.assert_rejected(root, "filename must equal dossier id")

        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_dossier(root, concepts=[], lessons=[])
            self.assert_rejected(root, "must link at least one concept or lesson")

        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_dossier(root, concepts=["missing"])
            self.assert_rejected(root, "unknown concept: missing")

        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_dossier(root, lessons=["../escape.md"])
            self.assert_rejected(root, "must not escape the repository")

        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_dossier(root, tracks=["missing-track"])
            self.assert_rejected(root, "unknown track: missing-track")

        with self.create_root() as temporary, tempfile.TemporaryDirectory() as external_directory:
            root = Path(temporary)
            dossier = self.write_dossier(root)
            external = Path(external_directory) / dossier.name
            external.write_text(dossier.read_text(encoding="utf-8"), encoding="utf-8")
            dossier.unlink()
            dossier.symlink_to(external)
            self.assert_rejected(root, "history dossier must not be a symbolic link")

    def test_rejects_calendar_enum_source_and_evidence_basis_violations(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            milestone = json.loads(dossier_document().split("---\n", 2)[1])["milestones"][0]
            milestone["day"] = 31
            milestone["month"] = 2
            self.write_dossier(root, milestones=[milestone])
            self.assert_rejected(root, "invalid calendar components")

        with self.create_root() as temporary:
            root = Path(temporary)
            milestone = json.loads(dossier_document().split("---\n", 2)[1])["milestones"][0]
            milestone["kind"] = "origin-story"
            self.write_dossier(root, milestones=[milestone])
            self.assert_rejected(root, "milestones[0].kind must be one of")

        with self.create_root() as temporary:
            root = Path(temporary)
            milestone = json.loads(dossier_document().split("---\n", 2)[1])["milestones"][0]
            milestone["sources"][0]["url"] = "http://insecure.example/alpha"
            self.write_dossier(root, milestones=[milestone])
            self.assert_rejected(root, "must be an HTTPS URL")

        with self.create_root() as temporary:
            root = Path(temporary)
            milestone = json.loads(dossier_document().split("---\n", 2)[1])["milestones"][0]
            milestone["sources"][0]["role"] = "blog"
            self.write_dossier(root, milestones=[milestone])
            self.assert_rejected(root, "sources[0].role must be one of")

        with self.create_root() as temporary:
            root = Path(temporary)
            milestone = json.loads(dossier_document().split("---\n", 2)[1])["milestones"][0]
            milestone["evidence_basis"] = "mixed"
            self.write_dossier(root, milestones=[milestone])
            self.assert_rejected(root, "mixed requires primary and scholarly secondary")

    def test_rejects_duplicate_source_urls_milestone_ids_and_missing_heading(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            milestone = json.loads(dossier_document().split("---\n", 2)[1])["milestones"][0]
            milestone["sources"].append(dict(milestone["sources"][0]))
            self.write_dossier(root, milestones=[milestone])
            self.assert_rejected(root, "sources URLs must be unique")

        with self.create_root() as temporary:
            root = Path(temporary)
            milestone = json.loads(dossier_document().split("---\n", 2)[1])["milestones"][0]
            other = dict(milestone)
            self.write_dossier(root, milestones=[milestone, other])
            self.assert_rejected(root, "milestone ids must be unique")

        with self.create_root() as temporary:
            root = Path(temporary)
            path = self.write_dossier(root)
            path.write_text(path.read_text(encoding="utf-8").replace("## Modern boundary", "## Present boundary"), encoding="utf-8")
            self.assert_rejected(root, "missing required Markdown headings: Modern boundary")


if __name__ == "__main__":
    unittest.main()

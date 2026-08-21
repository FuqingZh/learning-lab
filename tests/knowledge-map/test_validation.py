#!/usr/bin/env python3
"""Focused contract tests for scripts/build-knowledge-map.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY_ROOT / "scripts" / "build-knowledge-map.py"


def concept_document(identifier: str, **overrides: object) -> str:
    fields: dict[str, object] = {
        "id": identifier,
        "title": identifier.replace("-", " ").title(),
        "summary": f"A concise definition of {identifier}.",
        "kind": "foundation",
        "tracks": ["track-a"],
        "case_labs": [],
        "prerequisites": [],
        "enables": [],
        "contrasts_with": [],
        "related": [],
        "lessons": [],
        "records": [],
        "terminology": {
            "preferred_english_term": identifier.replace("-", " ").title(),
            "checked_on": "2026-08-21",
            "sources": [
                {
                    "url": "https://standards.example/term",
                    "publisher": "Standards Example",
                    "kind": "standard",
                },
                {
                    "url": "https://docs.example/term",
                    "publisher": "Documentation Example",
                    "kind": "professional-documentation",
                },
            ],
        },
    }
    fields.update(overrides)
    relationship_fields = {"prerequisites", "enables", "contrasts_with", "related"}
    lines = ["---"]
    for key, value in fields.items():
        if key == "terminology":
            assert isinstance(value, dict)
            lines.extend(
                [
                    "terminology:",
                    f"  preferred_english_term: {value['preferred_english_term']}",
                    f"  checked_on: \"{value['checked_on']}\"",
                    "  sources:",
                ]
            )
            for source in value["sources"]:
                lines.extend(
                    [
                        f"    - url: {source['url']}",
                        f"      publisher: {source['publisher']}",
                        f"      kind: {source['kind']}",
                    ]
                )
        elif isinstance(value, list):
            if value:
                lines.append(f"{key}:")
                for item in value:
                    rendered = f'"[[concepts/{item}]]"' if key in relationship_fields else item
                    lines.append(f"  - {rendered}")
            else:
                lines.append(f"{key}: []")
        else:
            lines.append(f"{key}: {value}")
    lines.extend(["---", "", f"# {fields['title']}", ""])
    return "\n".join(lines)


class TestKnowledgeMapValidation(unittest.TestCase):
    def create_root(self) -> tempfile.TemporaryDirectory[str]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "concepts").mkdir()
        (root / "case-labs").mkdir()
        (root / "tracks" / "track-a").mkdir(parents=True)
        return temporary

    def write_concept(self, root: Path, filename: str, identifier: str, **overrides: object) -> None:
        (root / "concepts" / filename).write_text(
            concept_document(identifier, **overrides), encoding="utf-8"
        )

    def run(self, root: Path, command: str = "validate") -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT), command, "--root", str(root)],
            check=False,
            text=True,
            capture_output=True,
        )

    def assert_rejected(self, root: Path, expected: str) -> None:
        result = self.run(root)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected, result.stderr)

    def test_valid_graph_is_deterministic_and_derives_mastery(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            record = "learning-records/track-a/20260820-alpha-mastered.md"
            record_path = root / record
            record_path.parent.mkdir(parents=True)
            record_path.write_text("# alpha evidence\n", encoding="utf-8")
            (root / "case-labs" / "case-a.md").write_text(
                "---\nid: case-a\ntitle: Case A\nsummary: A case laboratory.\n---\n",
                encoding="utf-8",
            )
            self.write_concept(
                root,
                "alpha.md",
                "alpha",
                case_labs=["case-a"],
                records=[record],
                reviewer_notes=["stable", "portable"],
            )
            self.write_concept(root, "beta.md", "beta", prerequisites=["alpha"])

            first = self.run(root, "normalized-data")
            second = self.run(root, "normalized-data")
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(first.stdout, second.stdout)
            graph = json.loads(first.stdout)
            alpha = next(node for node in graph["nodes"] if node["id"] == "alpha")
            self.assertEqual(alpha["mastery"], {"effective_record": record, "status": "mastered"})
            self.assertEqual(
                alpha["extensions"],
                {
                    "reviewer_notes": ["stable", "portable"],
                    "terminology": {
                        "checked_on": "2026-08-21",
                        "preferred_english_term": "Alpha",
                        "sources": [
                            {
                                "kind": "standard",
                                "publisher": "Standards Example",
                                "url": "https://standards.example/term",
                            },
                            {
                                "kind": "professional-documentation",
                                "publisher": "Documentation Example",
                                "url": "https://docs.example/term",
                            },
                        ],
                    },
                },
            )
            self.assertEqual(
                graph["edges"],
                [{"source": "beta", "target": "alpha", "type": "prerequisites"}],
            )
            self.assertEqual(
                graph["case_labs"],
                [
                    {
                        "direct_concepts": ["alpha"],
                        "id": "case-a",
                        "path": "case-labs/case-a.md",
                        "title": "Case A",
                    }
                ],
            )

    def test_rejects_duplicate_ids(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(root, "alpha.md", "alpha")
            self.write_concept(root, "beta.md", "alpha")
            self.assert_rejected(root, "duplicate concept ids")

    def test_rejects_basename_mismatch(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(root, "alpha.md", "beta")
            self.assert_rejected(root, "basename must equal id")

    def test_rejects_dangling_relationship(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(root, "alpha.md", "alpha", prerequisites=["missing"])
            self.assert_rejected(root, "dangling prerequisites target")

    def test_rejects_unknown_track(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(root, "alpha.md", "alpha", tracks=["missing-track"])
            self.assert_rejected(root, "unknown track")

    def test_rejects_unknown_case_lab(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(root, "alpha.md", "alpha", case_labs=["missing-case"])
            self.assert_rejected(root, "unknown case lab")

    def test_rejects_missing_evidence(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(
                root,
                "alpha.md",
                "alpha",
                records=["learning-records/track-a/20260820-alpha-mastered.md"],
            )
            self.assert_rejected(root, "records target does not exist")

    def test_rejects_invalid_kind(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(root, "alpha.md", "alpha", kind="unspecified")
            self.assert_rejected(root, "kind must be one of")

    def test_rejects_missing_terminology(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            document = concept_document("alpha").replace("terminology:\n", "provenance:\n")
            (root / "concepts" / "alpha.md").write_text(document, encoding="utf-8")
            self.assert_rejected(root, "terminology must be a mapping")

    def test_rejects_terminology_preferred_term_different_from_title(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(
                root,
                "alpha.md",
                "alpha",
                terminology={
                    "preferred_english_term": "Beta",
                    "checked_on": "2026-08-21",
                    "sources": [
                        {
                            "url": "https://standards.example/term",
                            "publisher": "Standards Example",
                            "kind": "standard",
                        },
                        {
                            "url": "https://docs.example/term",
                            "publisher": "Documentation Example",
                            "kind": "professional-documentation",
                        },
                    ],
                },
            )
            self.assert_rejected(root, "preferred_english_term must equal title")

    def test_rejects_terminology_sources_without_independent_publishers(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(
                root,
                "alpha.md",
                "alpha",
                terminology={
                    "preferred_english_term": "Alpha",
                    "checked_on": "2026-08-21",
                    "sources": [
                        {
                            "url": "https://standards.example/term",
                            "publisher": "Example Publisher",
                            "kind": "standard",
                        },
                        {
                            "url": "https://docs.example/term",
                            "publisher": " example  publisher ",
                            "kind": "professional-documentation",
                        },
                    ],
                },
            )
            self.assert_rejected(root, "publishers must be unique after normalization")

    def test_rejects_unquoted_terminology_date(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            document = concept_document("alpha").replace(
                'checked_on: "2026-08-21"', "checked_on: 2026-08-21"
            )
            (root / "concepts" / "alpha.md").write_text(document, encoding="utf-8")
            self.assert_rejected(root, "checked_on must be a quoted ISO date")

    def test_rejects_prerequisite_cycle(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(root, "alpha.md", "alpha", prerequisites=["beta"])
            self.write_concept(root, "beta.md", "beta", prerequisites=["alpha"])
            self.assert_rejected(root, "prerequisite cycle")

    def test_rejects_same_day_record_history_without_machine_metadata(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            records = [
                "learning-records/track-a/20260820-alpha-developing.md",
                "learning-records/track-a/20260820-alpha-mastered.md",
            ]
            for record in records:
                path = root / record
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# alpha evidence\n", encoding="utf-8")
            self.write_concept(root, "alpha.md", "alpha", records=records)
            self.assert_rejected(root, "multiple records are ambiguous")

    def test_machine_supersession_selects_one_effective_record(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            developing = "learning-records/track-a/20260819-alpha-developing.md"
            mastered = "learning-records/track-a/20260820-alpha-mastered.md"
            developing_path = root / developing
            developing_path.parent.mkdir(parents=True)
            developing_path.write_text("# developing\n", encoding="utf-8")
            (root / mastered).write_text(
                f"---\nsupersedes: {developing}\n---\n\n# mastered\n",
                encoding="utf-8",
            )
            self.write_concept(root, "alpha.md", "alpha", records=[developing, mastered])
            result = self.run(root, "normalized-data")
            self.assertEqual(result.returncode, 0, result.stderr)
            graph = json.loads(result.stdout)
            self.assertEqual(
                graph["nodes"][0]["mastery"],
                {"effective_record": mastered, "status": "mastered"},
            )

    def test_rejects_record_supersession_cycle_even_with_one_unsuperseded_record(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            first = "learning-records/track-a/20260818-alpha-developing.md"
            second = "learning-records/track-a/20260819-alpha-developing.md"
            mastered = "learning-records/track-a/20260820-alpha-mastered.md"
            for path, supersedes in (
                (first, second),
                (second, first),
                (mastered, first),
            ):
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    f"---\nsupersedes: {supersedes}\n---\n\n# evidence\n",
                    encoding="utf-8",
                )
            self.write_concept(root, "alpha.md", "alpha", records=[first, second, mastered])
            self.assert_rejected(root, "record supersession cycle")

    def test_rejects_different_day_record_history_without_machine_metadata(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            records = [
                "learning-records/track-a/20260819-alpha-developing.md",
                "learning-records/track-a/20260820-alpha-mastered.md",
            ]
            for record in records:
                path = root / record
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# alpha evidence\n", encoding="utf-8")
            self.write_concept(root, "alpha.md", "alpha", records=records)
            self.assert_rejected(root, "multiple records are ambiguous")

    def test_rejects_record_outside_learning_records_boundary(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            record = "evidence/20260820-alpha-mastered.md"
            path = root / record
            path.parent.mkdir(parents=True)
            path.write_text("# misplaced evidence\n", encoding="utf-8")
            self.write_concept(root, "alpha.md", "alpha", records=[record])
            self.assert_rejected(root, "must be under learning-records/<track>/")

    def test_rejects_mirrored_symmetric_relationship(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(root, "alpha.md", "alpha", related=["beta"])
            self.write_concept(root, "beta.md", "beta", related=["alpha"])
            self.assert_rejected(root, "duplicate mirrored related relationship")

    def test_rejects_redundant_enables_and_prerequisite_inverse(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(root, "alpha.md", "alpha", enables=["beta"])
            self.write_concept(root, "beta.md", "beta", prerequisites=["alpha"])
            self.assert_rejected(root, "redundant inverse relationship")

    def test_rejects_related_edge_over_an_existing_typed_relationship(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_concept(root, "alpha.md", "alpha", related=["beta"])
            self.write_concept(root, "beta.md", "beta", prerequisites=["alpha"])
            self.assert_rejected(root, "related must not duplicate a typed relationship")

    def test_rejects_non_json_extension_value(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            document = concept_document("alpha").replace(
                "\n---\n\n# Alpha",
                "\nreviewers: !!set\n  ? alice\n  ? bob\n---\n\n# Alpha",
            )
            (root / "concepts" / "alpha.md").write_text(document, encoding="utf-8")
            self.assert_rejected(root, "must be deterministic JSON-compatible data")

    def test_rejects_duplicate_records_key(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            document = concept_document("alpha").replace(
                "records: []\nterminology:",
                "records: []\nrecords: []\nterminology:",
            )
            (root / "concepts" / "alpha.md").write_text(document, encoding="utf-8")
            self.assert_rejected(root, "found duplicate key 'records'")

    def test_rejects_duplicate_relationship_key(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            document = concept_document("alpha").replace(
                "related: []\nlessons:",
                "related: []\nrelated: []\nlessons:",
            )
            (root / "concepts" / "alpha.md").write_text(document, encoding="utf-8")
            self.assert_rejected(root, "found duplicate key 'related'")


def main() -> int:
    test_names = unittest.defaultTestLoader.getTestCaseNames(TestKnowledgeMapValidation)
    for test_name in test_names:
        test = TestKnowledgeMapValidation(test_name)
        try:
            test.setUp()
            getattr(test, test_name)()
        except BaseException as error:
            print(f"{test_name}: FAIL: {error}", file=sys.stderr)
            return 1
        finally:
            test.tearDown()
    print(f"knowledge-map validation tests: {len(test_names)} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

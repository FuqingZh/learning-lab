#!/usr/bin/env python3
"""Focused contract tests for scripts/build-learning-state.py."""

from __future__ import annotations

import json
import datetime as dt
import math
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY_ROOT / "scripts" / "build-learning-state.py"
GRAPH_SCRIPT = REPOSITORY_ROOT / "scripts" / "build-knowledge-map.py"
RECORDS_SCRIPT = REPOSITORY_ROOT / "scripts" / "learning_records.py"


def concept_document(identifier: str) -> str:
    title = {"alpha": "Idempotency", "beta": "Side effect"}[identifier]
    return f"""---
id: {identifier}
title: {title}
summary: A transferable {identifier} concept.
kind: foundation
tracks:
  - track-a
case_labs: []
prerequisites: []
enables: []
contrasts_with: []
related: []
lessons: []
records: []
terminology:
  preferred_english_term: {title}
  checked_on: "2026-08-21"
  sources:
    - url: https://www.rfc-editor.org/rfc/rfc9110.html
      publisher: RFC Editor
      kind: standard
    - url: https://docs.oracle.com/javase/specs/jls/se24/html/jls-15.html
      publisher: Oracle
      kind: professional-documentation
---

# {identifier}
"""


def event_document(identifier: str, *, timestamp: str = "2026-08-01T12:00:00+08:00", evidence: str | None = None) -> str:
    evidence_block = "evidence: []" if evidence == "[]" else f"evidence:\n{evidence or '''  - concept: alpha
    check: exposure
    outcome: pass
    confidence: medium
    assisted: false'''}"
    return f"""schema_version: 1
id: {identifier}
started_at: {timestamp}
duration_minutes: 3
mode: contextual-review
track: track-a
resume:
  from: alpha
  next: beta
  summary: Continue from a precise recovery boundary.
{evidence_block}
"""


def v2_event_document(
    identifier: str, *, unit_kind: str = "concept", unit_ref: str = "beta", checkpoint: str = "transfer",
    evidence: str | None = "[]",
) -> str:
    evidence_block = "evidence: []" if evidence == "[]" else f"evidence:\n{evidence}"
    return f"""schema_version: 2
id: {identifier}
started_at: 2026-08-01T12:00:00+08:00
duration_minutes: 3
mode: contextual-review
track: track-a
resume:
  unit_kind: {unit_kind}
  unit_ref: {unit_ref}
  checkpoint: {checkpoint}
  summary: Continue from an explicit recovery boundary.
{evidence_block}
"""


class TestLearningState(unittest.TestCase):
    def test_audited_import_windows_match_records(self) -> None:
        audit_text = (REPOSITORY_ROOT / "docs/audits/20260831-session-timing-audit.md").read_text(encoding="utf-8")
        audit = yaml.safe_load(audit_text.split("---", 2)[1])
        self.assertEqual(len(audit["events"]), 6)
        previous_end = None
        for entry in audit["events"]:
            start = dt.datetime.fromisoformat(entry["source_start"])
            end = dt.datetime.fromisoformat(entry["source_end"])
            self.assertGreater(end, start)
            duration = math.ceil((end - start).total_seconds() / 60)
            if previous_end is not None:
                self.assertGreaterEqual(start, previous_end)
            previous_end = start + dt.timedelta(minutes=duration)
            path = REPOSITORY_ROOT / "learning-state/sessions" / (entry["corrected_id"] + ".yaml")
            event = yaml.safe_load(path.read_text(encoding="utf-8"))
            self.assertEqual(event["id"], entry["corrected_id"])
            self.assertEqual(event["started_at"], start)
            self.assertEqual(event["duration_minutes"], duration)
            self.assertEqual(entry["duration_minutes"], duration)
            self.assertFalse((path.parent / (entry["original_id"] + ".yaml")).exists())

    def create_root(self) -> tempfile.TemporaryDirectory[str]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        (root / "concepts").mkdir()
        (root / "case-labs").mkdir()
        (root / "tracks" / "track-a").mkdir(parents=True)
        (root / "lessons").mkdir()
        (root / "lessons" / "recovery.md").write_text("# Recovery\n", encoding="utf-8")
        (root / "learning-state" / "sessions").mkdir(parents=True)
        (root / "learning-records" / "track-a").mkdir(parents=True)
        (root / "scripts").mkdir()
        shutil.copy2(GRAPH_SCRIPT, root / "scripts" / "build-knowledge-map.py")
        shutil.copy2(SCRIPT, root / "scripts" / "build-learning-state.py")
        shutil.copy2(RECORDS_SCRIPT, root / "scripts" / "learning_records.py")
        (root / "concepts" / "alpha.md").write_text(concept_document("alpha"), encoding="utf-8")
        (root / "concepts" / "beta.md").write_text(concept_document("beta"), encoding="utf-8")
        return temporary

    def write_event(self, root: Path, identifier: str, **kwargs: object) -> Path:
        path = root / "learning-state" / "sessions" / f"{identifier}.yaml"
        path.write_text(event_document(identifier, **kwargs), encoding="utf-8")
        return path

    def run_cli(self, root: Path, command: str = "normalized-data", *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT), command, "--root", str(root), *arguments],
            check=False, text=True, capture_output=True,
        )

    def assert_rejected(self, root: Path, expected: str) -> None:
        result = self.run_cli(root, "validate")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected, result.stderr)

    def test_normalized_state_is_deterministic_and_legacy_records_do_not_promote_it(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(root, "20260801T120000+0800-alpha-exposure")
            first = self.run_cli(root)
            second = self.run_cli(root)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(first.stdout, second.stdout)
            state = json.loads(first.stdout)
            alpha = next(item for item in state["concepts"] if item["id"] == "alpha")
            beta = next(item for item in state["concepts"] if item["id"] == "beta")
            self.assertEqual(alpha["capability_state"], "encountered")
            self.assertEqual(alpha["next_review"], "2026-08-02")
            self.assertEqual(beta["capability_state"], "unassessed")
            self.assertIsNone(beta["next_review"])

    def test_rejects_duplicate_yaml_keys_and_duplicate_concept_evidence(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            path = self.write_event(root, "20260801T120000+0800-alpha-duplicate")
            path.write_text(path.read_text(encoding="utf-8") + "mode: guided-lesson\n", encoding="utf-8")
            self.assert_rejected(root, "duplicate key 'mode'")

        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(
                root, "20260801T120000+0800-alpha-two-evidence",
                evidence="""  - concept: alpha
    check: exposure
    outcome: pass
    confidence: medium
    assisted: false
  - concept: alpha
    check: explain-back
    outcome: pass
    confidence: high
    assisted: false""",
            )
            self.assert_rejected(root, "duplicate concept evidence: alpha")

    def test_rejects_invalid_schema_unknown_references_and_impossible_duration(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            path = self.write_event(root, "20260801T120000+0800-alpha-invalid")
            text = path.read_text(encoding="utf-8").replace("duration_minutes: 3", "duration_minutes: 0")
            path.write_text(text, encoding="utf-8")
            self.assert_rejected(root, "duration_minutes")

        with self.create_root() as temporary:
            root = Path(temporary)
            path = self.write_event(root, "20260801T120000+0800-alpha-unknown")
            text = path.read_text(encoding="utf-8").replace("concept: alpha", "concept: missing")
            path.write_text(text, encoding="utf-8")
            self.assert_rejected(root, "unknown evidence concept")

    def test_retained_requires_later_unassisted_transfer_after_seven_calendar_days(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(root, "20260801T120000+0800-alpha-exposure")
            self.write_event(
                root, "20260808T120000+0800-alpha-transfer",
                timestamp="2026-08-08T12:00:00+08:00",
                evidence="""  - concept: alpha
    check: fresh-case-transfer
    outcome: pass
    confidence: high
    assisted: false""",
            )
            state = json.loads(self.run_cli(root).stdout)
            alpha = next(item for item in state["concepts"] if item["id"] == "alpha")
            self.assertEqual(alpha["capability_state"], "retained")

        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(root, "20260801T120000+0800-alpha-exposure")
            self.write_event(
                root, "20260807T120000+0800-alpha-transfer",
                timestamp="2026-08-07T12:00:00+08:00",
                evidence="""  - concept: alpha
    check: fresh-case-transfer
    outcome: pass
    confidence: high
    assisted: false""",
            )
            state = json.loads(self.run_cli(root).stdout)
            alpha = next(item for item in state["concepts"] if item["id"] == "alpha")
            self.assertEqual(alpha["capability_state"], "usable")

    def test_list_due_uses_explicit_date_and_separates_outcome_from_overdue(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(root, "20260801T120000+0800-alpha-exposure")
            due = self.run_cli(root, "list-due", "--today", "2026-08-02")
            self.assertEqual(due.returncode, 0, due.stderr)
            self.assertEqual(json.loads(due.stdout)["due"][0]["due_state"], "due")
            lapsed = self.run_cli(root, "list-due", "--today", "2026-08-03")
            item = json.loads(lapsed.stdout)["due"][0]
            self.assertEqual(item["due_state"], "due")
            self.assertTrue(item["overdue"])

    def test_resume_only_event_updates_resume_without_creating_evidence(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(
                root,
                "20260801T120000+0800-resume-only",
                evidence="[]",
            )
            result = self.run_cli(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads(result.stdout)
            alpha = next(item for item in state["concepts"] if item["id"] == "alpha")
            self.assertEqual(alpha["evidence_count"], 0)
            self.assertEqual(alpha["capability_state"], "unassessed")
            self.assertIsNone(alpha["next_review"])
            self.assertEqual(state["resume"]["event_id"], "20260801T120000+0800-resume-only")
            self.assertEqual(state["resume"]["unit_kind"], "concept")
            self.assertEqual(state["resume"]["unit_ref"], "beta")
            self.assertIsNone(state["resume"]["checkpoint"])
            self.assertTrue(state["resume"]["legacy"])
            self.assertEqual(state["resume"]["from"], "alpha")
            self.assertEqual(state["resume"]["next"], "beta")

    def test_v2_resume_supports_concept_track_and_existing_lesson_references(self) -> None:
        for unit_kind, unit_ref in (("concept", "beta"), ("track", "track-a"), ("lesson", "lessons/recovery.md")):
            with self.subTest(unit_kind=unit_kind), self.create_root() as temporary:
                root = Path(temporary)
                identifier = f"20260801T120000+0800-v2-{unit_kind}"
                path = root / "learning-state" / "sessions" / f"{identifier}.yaml"
                path.write_text(v2_event_document(identifier, unit_kind=unit_kind, unit_ref=unit_ref), encoding="utf-8")
                result = self.run_cli(root)
                self.assertEqual(result.returncode, 0, result.stderr)
                resume = json.loads(result.stdout)["resume"]
                self.assertEqual(resume["unit_kind"], unit_kind)
                self.assertEqual(resume["unit_ref"], unit_ref)
                self.assertEqual(resume["checkpoint"], "transfer")
                self.assertFalse(resume["legacy"])

    def test_v2_resume_rejects_invalid_or_unsafe_references_and_empty_recovery_text(self) -> None:
        cases = (
            ("concept", "missing", "unknown resume concept"),
            ("track", "missing", "unknown resume track"),
            ("lesson", "lessons/missing.md", "unknown resume lesson"),
            ("lesson", "../lessons/recovery.md", "canonical lessons-relative"),
            ("lesson", "lessons/../lessons/recovery.md", "canonical lessons-relative"),
            ("lesson", "/tmp/recovery.md", "canonical lessons-relative"),
        )
        for unit_kind, unit_ref, expected in cases:
            with self.subTest(unit_kind=unit_kind, unit_ref=unit_ref), self.create_root() as temporary:
                root = Path(temporary)
                identifier = "20260801T120000+0800-v2-invalid"
                path = root / "learning-state" / "sessions" / f"{identifier}.yaml"
                path.write_text(v2_event_document(identifier, unit_kind=unit_kind, unit_ref=unit_ref), encoding="utf-8")
                self.assert_rejected(root, expected)

        with self.create_root() as temporary:
            root = Path(temporary)
            identifier = "20260801T120000+0800-v2-empty-checkpoint"
            path = root / "learning-state" / "sessions" / f"{identifier}.yaml"
            path.write_text(
                v2_event_document(identifier).replace("checkpoint: transfer", "checkpoint: ''"), encoding="utf-8"
            )
            self.assert_rejected(root, "resume.checkpoint must be a non-empty string")

        with self.create_root() as temporary:
            root = Path(temporary)
            identifier = "20260801T120000+0800-v2-empty-summary"
            path = root / "learning-state" / "sessions" / f"{identifier}.yaml"
            path.write_text(
                v2_event_document(identifier).replace(
                    "summary: Continue from an explicit recovery boundary.", "summary: ''"
                ),
                encoding="utf-8",
            )
            self.assert_rejected(root, "resume.summary must be a non-empty string")

    def test_assisted_evidence_cannot_promote_capability_or_lengthen_review_interval(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(
                root, "20260801T120000+0800-assisted-transfer",
                evidence="""  - concept: alpha
    check: fresh-case-transfer
    outcome: pass
    confidence: high
    assisted: true""",
            )
            state = json.loads(self.run_cli(root).stdout)
            alpha = next(item for item in state["concepts"] if item["id"] == "alpha")
            self.assertEqual(alpha["capability_state"], "unassessed")
            self.assertEqual(alpha["next_review"], "2026-08-02")

        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(root, "20260801T120000+0800-alpha-exposure")
            self.write_event(
                root, "20260808T120000+0800-assisted-transfer",
                timestamp="2026-08-08T12:00:00+08:00",
                evidence="""  - concept: alpha
    check: fresh-case-transfer
    outcome: pass
    confidence: high
    assisted: true""",
            )
            state = json.loads(self.run_cli(root).stdout)
            alpha = next(item for item in state["concepts"] if item["id"] == "alpha")
            self.assertEqual(alpha["capability_state"], "encountered")
            self.assertEqual(alpha["next_review"], "2026-08-09")

    def test_list_review_cues_matches_legacy_list_due_output(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(root, "20260801T120000+0800-alpha-exposure")
            due = self.run_cli(root, "list-due", "--today", "2026-08-02")
            cues = self.run_cli(root, "list-review-cues", "--today", "2026-08-02")
            self.assertEqual(due.returncode, 0, due.stderr)
            self.assertEqual(cues.returncode, 0, cues.stderr)
            self.assertEqual(cues.stdout, due.stdout)

    def test_same_day_passes_do_not_lengthen_review_interval(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(root, "20260801T120000+0800-first")
            self.write_event(root, "20260801T124900+0800-repeated",
                             timestamp="2026-08-01T12:49:00+08:00")
            state = json.loads(self.run_cli(root).stdout)
            alpha = next(item for item in state["concepts"] if item["id"] == "alpha")
            self.assertEqual(alpha["evidence_count"], 2)
            self.assertEqual(alpha["next_review"], "2026-08-02")
            self.write_event(root, "20260802T120000+0800-next-day",
                             timestamp="2026-08-02T12:00:00+08:00")
            state = json.loads(self.run_cli(root).stdout)
            alpha = next(item for item in state["concepts"] if item["id"] == "alpha")
            self.assertEqual(alpha["next_review"], "2026-08-09")

    def test_day_deduplication_uses_one_timezone(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(root, "20260801T230000+0000-first",
                             timestamp="2026-08-01T23:00:00+00:00")
            self.write_event(root, "20260802T003000+0100-same-utc-day",
                             timestamp="2026-08-02T00:30:00+01:00")
            result = self.run_cli(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads(result.stdout)
            alpha = next(item for item in state["concepts"] if item["id"] == "alpha")
            self.assertEqual(alpha["evidence_count"], 2)
            self.assertEqual(alpha["next_review"], "2026-08-03")

    def test_rejects_resume_only_event_without_a_complete_resume_block(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            path = self.write_event(
                root,
                "20260801T120000+0800-empty-resume",
                evidence="[]",
            )
            text = path.read_text(encoding="utf-8").replace(
                "summary: Continue from a precise recovery boundary.", "summary: ''"
            )
            path.write_text(text, encoding="utf-8")
            self.assert_rejected(root, "resume.summary must be a non-empty string")

        with self.create_root() as temporary:
            root = Path(temporary)
            path = self.write_event(
                root,
                "20260801T120000+0800-no-resume",
                evidence="[]",
            )
            text = path.read_text(encoding="utf-8")
            text = text.replace(
                "resume:\n  from: alpha\n  next: beta\n  summary: Continue from a precise recovery boundary.\n", ""
            )
            path.write_text(text, encoding="utf-8")
            self.assert_rejected(root, "event missing required fields: resume")

    def test_lapsed_projection_and_event_id_timestamp_contract(self) -> None:
        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(
                root,
                "20260801T120000+0800-alpha-partial",
                evidence="""  - concept: alpha
    check: explain-back
    outcome: partial
    confidence: low
    assisted: false""",
            )
            result = self.run_cli(root, "list-due", "--today", "2026-08-02")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["due"][0]["due_state"], "lapsed")

        with self.create_root() as temporary:
            root = Path(temporary)
            self.write_event(root, "20260802T120000+0800-alpha-wrong-time")
            self.assert_rejected(root, "id timestamp prefix must match started_at")


if __name__ == "__main__":
    unittest.main()

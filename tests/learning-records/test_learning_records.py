#!/usr/bin/env python3
"""Focused contract tests for evidence-backed learning records."""

from __future__ import annotations

import json
import datetime as dt
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import learning_records  # noqa: E402


CONCEPT = """---
id: idempotency
title: Idempotency
summary: Repeating an operation has the same intended effect.
kind: foundation
tracks:
  - scientific-ai-platforms
case_labs: []
prerequisites: []
enables: []
contrasts_with: []
related: []
lessons: []
records: []
terminology:
  preferred_english_term: Idempotency
  checked_on: "2026-08-27"
  sources:
    - url: https://www.rfc-editor.org/rfc/rfc9110
      publisher: RFC Editor
      kind: standard
    - url: https://docs.aws.amazon.com/ec2/latest/devguide/ec2-api-idempotency.html
      publisher: Amazon Web Services
      kind: professional-documentation
---
# Idempotency
"""


class LearningRecordsTest(unittest.TestCase):
    def make_root(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        for directory in (
            "concepts",
            "case-labs",
            "tracks/scientific-ai-platforms",
            "learning-state/sessions",
            "learning-records/scientific-ai-platforms",
            "scripts",
        ):
            (root / directory).mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "scripts/build-knowledge-map.py", root / "scripts/build-knowledge-map.py")
        shutil.copy2(ROOT / "scripts/build-learning-state.py", root / "scripts/build-learning-state.py")
        shutil.copy2(ROOT / "scripts/learning_records.py", root / "scripts/learning_records.py")
        (root / "concepts/idempotency.md").write_text(CONCEPT, encoding="utf-8")
        return root

    def write_event(self, root: Path, *, stamp: str, check: str = "fresh-case-transfer", assisted: bool = False, outcome: str = "pass") -> str:
        identifier = f"{stamp}-idempotency-check"
        timestamp = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}T{stamp[9:11]}:{stamp[11:13]}:{stamp[13:15]}+08:00"
        document = f"""schema_version: 2
id: {identifier}
started_at: \"{timestamp}\"
duration_minutes: 10
mode: guided-lesson
track: scientific-ai-platforms
resume:
  unit_kind: concept
  unit_ref: idempotency
  checkpoint: next
  summary: continue
evidence:
  - concept: idempotency
    check: {check}
    outcome: {outcome}
    confidence: high
    assisted: {str(assisted).lower()}
"""
        (root / "learning-state/sessions" / f"{identifier}.yaml").write_text(document, encoding="utf-8")
        return identifier

    def write_record(self, root: Path, *, name: str = "20260827-idempotency.md", body: str) -> Path:
        path = root / "learning-records/scientific-ai-platforms" / name
        path.write_text(body, encoding="utf-8")
        return path

    def structured(self, *, sessions: list[str], state: str = "usable", date: str = "2026-08-27", supersedes: list[str] | None = None, assisted: str = "false") -> str:
        listed_sessions = "".join(f"  - {item}\n" for item in sessions)
        listed_supersedes = "".join(f"  - {item}\n" for item in (supersedes or []))
        return f"""---
schema_version: 1
track: scientific-ai-platforms
concepts:
  - idempotency
capability_state: {state}
demonstrated_at: \"{date}\"
assisted: {assisted}
evidence_sessions:
{listed_sessions}supersedes:
{listed_supersedes or ' []\n'}---
# Evidence claim
"""

    def test_legacy_is_audited_but_never_inferred(self) -> None:
        root = self.make_root()
        self.write_record(root, name="old-mastered.md", body="# Historical prose\n")
        projection = learning_records.build_projection(root)
        self.assertEqual("unassessed", projection["capabilities"]["idempotency"]["state"])
        self.assertEqual(1, projection["audit"]["legacy_count"])
        self.assertIn("missing-schema-version", projection["audit"]["legacy"][0]["reasons"])
        self.assertIn("missing-evidence-session-links", projection["audit"]["legacy"][0]["reasons"])

    def test_legacy_status_is_audited_and_injected_graph_avoids_subprocess(self) -> None:
        root = self.make_root()
        self.write_record(
            root,
            name="old-status.md",
            body="---\nStatus: mastered\n---\n# Historical prose\n",
        )
        graph = {
            "schema_version": 1,
            "tracks": ["scientific-ai-platforms"],
            "nodes": [{"id": "idempotency", "tracks": ["scientific-ai-platforms"]}],
        }
        projection = learning_records.build_projection(root, graph=graph, events=[])
        self.assertEqual("unassessed", projection["capabilities"]["idempotency"]["state"])
        self.assertIn("legacy-status-frontmatter", projection["audit"]["legacy"][0]["reasons"])

    def test_usable_projection_is_deterministic(self) -> None:
        root = self.make_root()
        session = self.write_event(root, stamp="20260827T120000+0800")
        self.write_record(root, body=self.structured(sessions=[session]))
        first = learning_records.build_projection(root)
        second = learning_records.build_projection(root)
        self.assertEqual(
            json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True)
        )
        self.assertEqual("usable", first["capabilities"]["idempotency"]["state"])

    def test_duplicate_active_records_are_rejected(self) -> None:
        root = self.make_root()
        session = self.write_event(root, stamp="20260827T120000+0800")
        self.write_record(root, name="one.md", body=self.structured(sessions=[session]))
        self.write_record(root, name="two.md", body=self.structured(sessions=[session]))
        with self.assertRaisesRegex(learning_records.LearningRecordsError, "multiple active"):
            learning_records.build_projection(root)

    def test_invalid_session_reference_is_rejected(self) -> None:
        root = self.make_root()
        self.write_record(root, body=self.structured(sessions=["20260827T120000+0800-missing"]))
        with self.assertRaisesRegex(learning_records.LearningRecordsError, "unknown evidence session"):
            learning_records.build_projection(root)

    def test_assisted_transfer_cannot_support_usable(self) -> None:
        root = self.make_root()
        session = self.write_event(root, stamp="20260827T120000+0800", assisted=True)
        self.write_record(root, body=self.structured(sessions=[session]))
        with self.assertRaisesRegex(learning_records.LearningRecordsError, "usable requires an unassisted"):
            learning_records.build_projection(root)

    def test_assisted_or_failed_observation_cannot_support_encountered(self) -> None:
        root = self.make_root()
        session = self.write_event(root, stamp="20260827T120000+0800", check="exposure", assisted=True)
        self.write_record(root, body=self.structured(sessions=[session], state="encountered"))
        with self.assertRaisesRegex(learning_records.LearningRecordsError, "encountered requires an unassisted"):
            learning_records.build_projection(root)

    def test_cross_track_supersedes_is_rejected(self) -> None:
        root = self.make_root()
        (root / "tracks/bioinformatics-systems").mkdir()
        (root / "learning-records/bioinformatics-systems").mkdir()
        (root / "learning-records/bioinformatics-systems/legacy.md").write_text("# old\n", encoding="utf-8")
        session = self.write_event(root, stamp="20260827T120000+0800")
        self.write_record(
            root,
            body=self.structured(
                sessions=[session], supersedes=["learning-records/bioinformatics-systems/legacy.md"]
            ),
        )
        with self.assertRaisesRegex(learning_records.LearningRecordsError, "supersedes must stay within"):
            learning_records.build_projection(root)

    def test_multi_concept_record_requires_usable_evidence_for_each_concept(self) -> None:
        root = self.make_root()
        record = """---
schema_version: 1
track: scientific-ai-platforms
concepts:
  - idempotency
  - retries
capability_state: usable
demonstrated_at: "2026-08-27"
assisted: false
evidence_sessions:
  - 20260827T120000+0800-mixed-check
supersedes: []
---
# Mixed claim
"""
        self.write_record(root, body=record)
        graph = {
            "schema_version": 1,
            "tracks": ["scientific-ai-platforms"],
            "nodes": [
                {"id": "idempotency", "tracks": ["scientific-ai-platforms"]},
                {"id": "retries", "tracks": ["scientific-ai-platforms"]},
            ],
        }
        events = [{
            "id": "20260827T120000+0800-mixed-check",
            "started_at_value": dt.datetime(2026, 8, 27, 12, 0, tzinfo=dt.timezone(dt.timedelta(hours=8))),
            "evidence": [
                {"concept": "idempotency", "check": "fresh-case-transfer", "outcome": "pass", "confidence": "high", "assisted": False},
                {"concept": "retries", "check": "exposure", "outcome": "pass", "confidence": "high", "assisted": False},
            ],
        }]
        with self.assertRaisesRegex(learning_records.LearningRecordsError, "retries usable requires"):
            learning_records.build_projection(root, graph=graph, events=events)

    def test_legacy_superseded_by_structured_record_is_resolved_in_audit(self) -> None:
        root = self.make_root()
        legacy = "learning-records/scientific-ai-platforms/old.md"
        self.write_record(root, name="old.md", body="---\nStatus: mastered\n---\n# Old\n")
        session = self.write_event(root, stamp="20260827T120000+0800")
        self.write_record(root, body=self.structured(sessions=[session], supersedes=[legacy]))
        graph = {
            "schema_version": 1,
            "tracks": ["scientific-ai-platforms"],
            "nodes": [{"id": "idempotency", "tracks": ["scientific-ai-platforms"], "records": [legacy]}],
        }
        events = learning_records.learning_state.load_events(root, graph)
        audit = learning_records.build_projection(root, graph=graph, events=events)["audit"]
        self.assertEqual(1, audit["legacy_count"])
        self.assertEqual(0, audit["pending_legacy_count"])
        self.assertEqual(1, audit["resolved_legacy_count"])
        self.assertEqual(["learning-records/scientific-ai-platforms/20260827-idempotency.md"], audit["legacy"][0]["resolved_by"])

    def test_legacy_supersedes_requires_declared_concept_graph_link(self) -> None:
        root = self.make_root()
        legacy = "learning-records/scientific-ai-platforms/idempotency-legacy.md"
        self.write_record(root, name="idempotency-legacy.md", body="# Old idempotency record\n")
        record = """---
schema_version: 1
track: scientific-ai-platforms
concepts:
  - retries
capability_state: usable
demonstrated_at: "2026-08-27"
assisted: false
evidence_sessions:
  - 20260827T120000+0800-retries-check
supersedes:
  - learning-records/scientific-ai-platforms/idempotency-legacy.md
---
# Incorrect closure
"""
        self.write_record(root, body=record)
        graph = {
            "schema_version": 1,
            "tracks": ["scientific-ai-platforms"],
            "nodes": [
                {"id": "idempotency", "tracks": ["scientific-ai-platforms"], "records": [legacy]},
                {"id": "retries", "tracks": ["scientific-ai-platforms"], "records": []},
            ],
        }
        events = [{
            "id": "20260827T120000+0800-retries-check",
            "started_at_value": dt.datetime(2026, 8, 27, 12, 0, tzinfo=dt.timezone(dt.timedelta(hours=8))),
            "evidence": [{"concept": "retries", "check": "fresh-case-transfer", "outcome": "pass", "confidence": "high", "assisted": False}],
        }]
        with self.assertRaisesRegex(learning_records.LearningRecordsError, "legacy supersedes target must be linked"):
            learning_records.build_projection(root, graph=graph, events=events)

    def test_retained_requires_seven_day_boundary_and_latest_usable_check(self) -> None:
        root = self.make_root()
        first = self.write_event(root, stamp="20260820T120000+0800")
        second = self.write_event(root, stamp="20260827T120000+0800")
        record = self.structured(sessions=[first, second], state="retained", date="2026-08-27")
        self.write_record(root, body=record)
        projection = learning_records.build_projection(root)
        self.assertEqual("retained", projection["capabilities"]["idempotency"]["state"])

        root = self.make_root()
        first = self.write_event(root, stamp="20260821T120000+0800")
        second = self.write_event(root, stamp="20260827T120000+0800")
        self.write_record(root, body=self.structured(sessions=[first, second], state="retained", date="2026-08-27"))
        with self.assertRaisesRegex(learning_records.LearningRecordsError, "separated by at least 7 days"):
            learning_records.build_projection(root)


if __name__ == "__main__":
    unittest.main()

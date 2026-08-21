#!/usr/bin/env python3
"""Focused structural checks for the repository-local tutor skill."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".agents/skills/learning-lab-tutor/SKILL.md"


class LearningLabTutorSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = SKILL.read_text(encoding="utf-8")

    def test_has_discoverable_skill_metadata(self) -> None:
        self.assertTrue(SKILL.is_file())
        self.assertTrue(self.text.startswith("---\nname: learning-lab-tutor\n"))
        self.assertIn("description:", self.text)

    def test_uses_state_engine_as_the_scheduler_authority(self) -> None:
        self.assertIn("build-learning-state.py normalized-data", self.text)
        self.assertIn("build-learning-state.py list-due --today YYYY-MM-DD", self.text)
        self.assertIn("build-learning-state.py validate", self.text)
        self.assertIn("never duplicate", self.text)

    def test_selection_order_and_short_session_boundary_are_explicit(self) -> None:
        ordered = [
            "a due, important prior concept;",
            "a concept naturally triggered by the learner's current repository task;",
            "a blocking prerequisite on the active track;",
            "the next small step in the active track;",
            "a foundational node that remains unassessed.",
        ]
        positions = [self.text.index(item) for item in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("normally in **three", self.text)
        self.assertIn("Select exactly one increment", self.text)
        self.assertIn("at most one unaided retrieval or transfer prompt", self.text)

    def test_due_retrieval_and_interruption_protections_are_explicit(self) -> None:
        self.assertIn("never reveal the answer, definition", self.text)
        self.assertIn("adjacent relationships before that attempt", self.text)
        self.assertIn("A learner can stop at any point", self.text)
        self.assertIn("do not invent a pass, partial, miss,\nconfidence, or retention", self.text)
        self.assertIn("write `evidence: []`", self.text)
        self.assertIn("changes no capability or\nschedule", self.text)
        self.assertIn("fail closed: do not write an event", self.text)

    def test_append_only_event_protocol_has_stable_name_and_required_fields(self) -> None:
        self.assertIn("learning-state/sessions/<id>.yaml", self.text)
        self.assertIn("`YYYYMMDDTHHMMSS+ZZZZ-<concept-id>-<check>`", self.text)
        for field in (
            "schema_version:",
            "started_at:",
            "duration_minutes:",
            "mode:",
            "track:",
            "resume:",
            "evidence:",
            "assisted:",
        ):
            self.assertRegex(self.text, re.escape(field))


if __name__ == "__main__":
    unittest.main()

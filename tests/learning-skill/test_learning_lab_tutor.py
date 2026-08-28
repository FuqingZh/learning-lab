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

    def test_uses_state_engine_for_review_cues_without_granting_curriculum_authority(self) -> None:
        self.assertIn("build-learning-state.py normalized-data", self.text)
        self.assertIn("build-learning-state.py list-review-cues --today YYYY-MM-DD", self.text)
        self.assertIn("build-learning-state.py validate", self.text)
        self.assertIn("authority for review-cue derivation", self.text)
        self.assertIn("Review cues do not decide curriculum progression", self.text)
        self.assertIn("`list-review-cues` is the preferred tutor command", self.text)
        self.assertIn("`list-due` remains a\ncompatibility alias and returns the exact same JSON output", self.text)
        self.assertIn("Learning records are the authority for\nreviewed demonstrated capability", self.text)
        self.assertIn("Session events are append-only raw\nobservations", self.text)
        self.assertIn("never duplicate", self.text)

    def test_learner_contract_is_read_before_mission_led_selection(self) -> None:
        required_contract_sources = [
            "`.teach-workspace.yaml`",
            "`MISSION.md`",
            "`NOTES.md`",
            "root `RESOURCES.md`",
            "the active track's `README.md`, `CURRICULUM.md`, and `RESOURCES.md`",
            "recent relevant `learning-records/<track>/` inventory",
        ]
        positions = [self.text.index(item) for item in required_contract_sources]
        selection_position = self.text.index("## Choose the lesson unit")
        self.assertTrue(all(position < selection_position for position in positions))

        ordered = [
            "the mission and its constraints, plus `NOTES.md` teaching preferences;",
            "demonstrated capability in relevant learning records;",
            "the active track curriculum and trusted resources;",
            "the latest durable `resume`;",
            "relevant review cues and concept relationships;",
            "the learner's current request or repository case.",
        ]
        positions = [self.text.index(item) for item in ordered]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("When `MISSION.md` requires Chinese, teach in Chinese unless", self.text)
        self.assertIn("state exactly one mission-linked lesson win and its stopping", self.text)
        self.assertIn("A due cue must not displace a viable current-track", self.text)
        self.assertIn("There is no default timebox", self.text)
        self.assertIn("One lesson unit may include several connected concepts", self.text)
        self.assertIn("Begin with an advance organizer", self.text)
        self.assertIn("Do not interrupt every term or paragraph", self.text)
        self.assertNotIn("normally in **three", self.text)
        self.assertNotIn("Select exactly one increment", self.text)

    def test_history_is_optional_and_evidence_bounded(self) -> None:
        self.assertIn("Use a historical increment only when it materially supports the selected lesson", self.text)
        self.assertIn("complete matching dossier in `histories/`", self.text)
        self.assertIn("read that dossier and its linked source before teaching", self.text)
        self.assertIn("fail closed for the historical increment", self.text)
        self.assertIn("Continue\nwithout a historical claim", self.text)

    def test_due_retrieval_and_interruption_protections_are_explicit(self) -> None:
        self.assertIn("never reveal the answer, definition", self.text)
        self.assertIn("adjacent relationships before\n", self.text)
        self.assertIn("the learner's first retrieval attempt", self.text)
        self.assertIn("A learner can stop at any point", self.text)
        self.assertIn("do not invent a pass, partial, miss,\nconfidence, or retention", self.text)
        self.assertIn("write `evidence: []`", self.text)
        self.assertIn("An empty-evidence event is neutral", self.text)
        self.assertIn("creates no capability evidence or review cue", self.text)
        self.assertIn("Do not fall back to v1 merely because", self.text)
        self.assertIn("fail\nclosed: do not write an event", self.text)

    def test_new_events_use_v2_neutral_ids_and_structured_resume(self) -> None:
        self.assertIn("learning-state/sessions/<id>.yaml", self.text)
        self.assertIn("New production events use the documented v2 YAML schema", self.text)
        self.assertIn("Write\nv1 only for compatibility fixtures or byte-preserved historical examples", self.text)
        self.assertIn("`YYYYMMDDTHHMMSS+ZZZZ-<track-id>-session`", self.text)
        self.assertIn("not a parser-mandated suffix", self.text)
        self.assertIn("schema_version: 2", self.text)
        for field in (
            "id:",
            "started_at:",
            "duration_minutes:",
            "mode:",
            "track:",
            "unit_kind:",
            "unit_ref:",
            "checkpoint:",
            "summary:",
            "evidence:",
            "assisted:",
        ):
            self.assertRegex(self.text, re.escape(field))
        self.assertIn("Every v2 `resume` has exactly `unit_kind`,\n`unit_ref`, `checkpoint`, and `summary`", self.text)


if __name__ == "__main__":
    unittest.main()

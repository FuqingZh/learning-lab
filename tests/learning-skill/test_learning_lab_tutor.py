#!/usr/bin/env python3
"""Structural routing and executable event-example checks, not teaching assessment."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".agents/skills/learning-lab-tutor/SKILL.md"


class LearningLabTutorSkillTests(unittest.TestCase):
    def test_metadata_and_reference_routes_resolve(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        metadata = yaml.safe_load(text.split("---", 2)[1])
        self.assertEqual(metadata["name"], "learning-lab-tutor")
        self.assertIsInstance(metadata["description"], str)
        references = re.findall(r"\]\((references/[^)]+)\)", text)
        self.assertEqual(set(references), {
            "references/route-and-lesson.md", "references/teaching.md",
            "references/navigation.md", "references/recording.md",
        })
        for reference in references:
            path = (SKILL.parent / reference).resolve()
            self.assertIn(SKILL.parent.resolve(), path.parents)
            self.assertTrue(path.is_file())
            self.assertTrue(path.read_text(encoding="utf-8").strip())

    def test_recording_example_is_accepted_by_production_parser(self) -> None:
        text = (SKILL.parent / "references/recording.md").read_text(encoding="utf-8")
        match = re.search(r"```yaml\n(.*?)\n```", text, re.S)
        self.assertIsNotNone(match)
        event_text = match.group(1)
        event = yaml.safe_load(event_text)
        spec = importlib.util.spec_from_file_location("tutor_state", ROOT / "scripts/build-learning-state.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / (event["id"] + ".yaml")
            path.write_text(event_text, encoding="utf-8")
            parsed = module.parse_event(path, root=ROOT, concepts=set(),
                                        tracks={"scientific-ai-platforms"})
        self.assertEqual(parsed["evidence"], [])
        self.assertEqual(parsed["resume"]["unit_kind"], "lesson")

    def test_repository_references_exist(self) -> None:
        for relative in (
            "docs/evaluations/20260830-coherent-tutoring-cases.md",
            "learning-state/navigation/README.md",
            "scripts/check-teaching-navigation.py",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()

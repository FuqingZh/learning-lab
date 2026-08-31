#!/usr/bin/env python3
"""Synthetic navigation replay and lesson execution; no model or learner scoring."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/check-teaching-navigation.py"


def module_at(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


NAV = module_at("teaching_navigation", SCRIPT)
EVALUATION = module_at("navigation_evaluation", ROOT / "scripts/run-tutor-evaluation.py")


def snapshot():
    return {
        "schema_version": 1, "track": "track-a", "updated_at": "2026-08-31T09:00:00+08:00",
        "source": {"enabled": True, "locator": None, "coverage": "missing",
                   "verified_range": None, "gaps": ["Synthetic test, no original conversation."]},
        "main": {"unit_ref": "lessons/recovery.md", "checkpoint": "Explain the whole display problem."},
        "active_branch": None, "branches": [],
    }


def branch(identifier, parent=None):
    return {"id": identifier, "parent": parent, "unit_ref": "lessons/recovery.md",
            "question": "What does this call mean?", "purpose": "Explain a prerequisite.",
            "status": "open", "return_to": {"node": parent or "main", "checkpoint": "Resume the example."},
            "conclusion": None, "unresolved": []}


class NavigationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = EVALUATION.build_isolated_root(yaml.safe_dump({
            "schema_version": 2, "id": "20260830T120000+0800-track-a-session",
            "started_at": "2026-08-30T12:00:00+08:00", "duration_minutes": 10,
            "mode": "guided-lesson", "track": "track-a",
            "resume": {"unit_kind": "lesson", "unit_ref": "lessons/recovery.md",
                       "checkpoint": "Legacy checkpoint.", "summary": "Legacy summary."},
            "evidence": [],
        }))
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.directory = self.root / "learning-state/navigation"
        self.directory.mkdir()
        self.path = self.directory / "track-a.yaml"
        (self.root / "lessons/other.md").write_text("# Other\n", encoding="utf-8")
        self.data = snapshot()

    def save(self):
        self.path.write_text(yaml.safe_dump(self.data), encoding="utf-8")

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args, "--root", str(self.root)],
                              capture_output=True, text=True, check=False)

    def test_nested_return_and_new_direction_preserve_session_bytes(self):
        sessions = self.root / "learning-state/sessions"
        before = {p.name: p.read_bytes() for p in sessions.iterdir()}
        self.data["branches"] = [branch("library"), branch("call", "library")]
        self.data["active_branch"] = "call"
        self.save()
        output = NAV.resolve(self.root, "track-a")
        self.assertEqual(output["breadcrumb"], ["library", "call"])
        self.assertEqual(output["active_branch"]["return_to"]["node"], "library")
        self.data["branches"][1].update(status="resolved", conclusion="A call supplies inputs.")
        self.data["active_branch"] = "library"
        self.save()
        self.assertEqual(NAV.resolve(self.root, "track-a")["breadcrumb"], ["library"])
        self.data["branches"][0].update(status="parked", unresolved=["Learner changed direction."])
        self.data["active_branch"] = None
        self.data["main"]["unit_ref"] = "lessons/other.md"
        self.save()
        self.assertEqual(NAV.resolve(self.root, "track-a")["breadcrumb"], [])
        self.assertEqual(before, {p.name: p.read_bytes() for p in sessions.iterdir()})

    def test_missing_navigation_uses_real_legacy_producer_only_for_matching_track(self):
        result = self.cli("resolve", "--track", "track-a")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["source"], "legacy-resume")
        (self.root / "tracks/track-b").mkdir()
        (self.root / "learning-records/track-b").mkdir()
        result = self.cli("resolve", "--track", "track-b")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["source"], "none")

    def test_invalid_existing_navigation_does_not_fall_back(self):
        self.data["main"]["checkpoint"] = ""
        self.save()
        result = self.cli("resolve", "--track", "track-a")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("checkpoint", result.stderr)

    def test_structural_negative_controls(self):
        base = snapshot()
        base["branches"] = [branch("library"), branch("call", "library")]
        base["active_branch"] = "call"
        cases = []

        def reject(label, change):
            data = deepcopy(base)
            change(data)
            cases.append((label, data))

        reject("duplicate", lambda d: d["branches"].append(deepcopy(d["branches"][0])))
        reject("orphan", lambda d: d["branches"][1].update(parent="absent", return_to={"node": "absent", "checkpoint": "Return."}))
        reject("cycle", lambda d: d["branches"][0].update(parent="call", return_to={"node": "call", "checkpoint": "Return."}))
        reject("wrong return", lambda d: d["branches"][1]["return_to"].update(node="main"))
        reject("resolved active", lambda d: d["branches"][1].update(status="resolved", conclusion="Done."))
        reject("unrelated open", lambda d: d["branches"].append(branch("other")))
        reject("wrong lesson", lambda d: d["branches"][1].update(unit_ref="lessons/other.md"))
        reject("resolved no conclusion", lambda d: d["branches"][1].update(status="resolved"))
        reject("parked no reason", lambda d: d["branches"][1].update(status="parked"))
        reject("mastery injection", lambda d: d.update(mastery="pass"))
        reject("boolean schema", lambda d: d.update(schema_version=True))
        reject("naive date", lambda d: d.update(updated_at="2026-08-31T09:00:00"))
        reject("invalid date", lambda d: d.update(updated_at="yesterday"))
        reject("complete with gaps", lambda d: d["source"].update(coverage="complete", locator="test:one", verified_range="one"))
        reject("complete without range", lambda d: d["source"].update(coverage="complete", locator="test:one", gaps=[]))
        reject("not enabled", lambda d: d["source"].update(enabled=False))
        reject("path traversal", lambda d: d["main"].update(unit_ref="lessons/../lessons/recovery.md"))
        reject("empty path parts", lambda d: d["main"].update(unit_ref="."))
        reject("unknown track", lambda d: d.update(track="absent"))
        for label, data in cases:
            with self.subTest(label=label), self.assertRaises(NAV.NavigationError):
                NAV.validate(data, self.root)

    def test_partial_and_complete_are_declarations_only(self):
        self.data["source"].update(coverage="partial", locator="test:one", verified_range="turn 1")
        NAV.validate(self.data, self.root)
        self.data["source"].update(coverage="complete", gaps=[])
        NAV.validate(self.data, self.root)

    def test_filename_and_symlink_escape_fail(self):
        self.save()
        other = self.directory / "wrong.yaml"
        self.path.rename(other)
        with self.assertRaises(NAV.NavigationError):
            NAV.load(other, self.root)
        with tempfile.TemporaryDirectory() as external:
            self.path.symlink_to(Path(external) / "absent.yaml")
            self.assertNotEqual(self.cli("resolve", "--track", "track-a").returncode, 0)

    def test_duplicate_yaml_keys_fail_instead_of_last_wins(self):
        self.save()
        self.path.write_text(self.path.read_text(encoding="utf-8") + "active_branch: null\n",
                             encoding="utf-8")
        result = self.cli("resolve", "--track", "track-a")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate", result.stderr)


class LessonExampleTests(unittest.TestCase):
    def run_node(self, script):
        result = subprocess.run(["node", "--input-type=module", "-e", script],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_actual_markdown_example(self):
        text = (ROOT / "lessons/scientific-ai-platforms/react-from-document-updates.md").read_text(encoding="utf-8")
        match = re.search(r"<!-- executable-example: summary -->\s*```js\n(.*?)\n```", text, re.S)
        self.assertIsNotNone(match)
        self.run_node('import assert from "node:assert/strict";\n' + match.group(1) + '\n'
                      'assert.equal(firstText, "样本数：3");\n'
                      'assert.equal(secondText, "样本数：5");\n'
                      'assert.equal(summaryText({sampleCount: 0}), "样本数：0");')

    def test_html_script_with_document_test_double_not_browser(self):
        text = (ROOT / "lessons/scientific-ai-platforms/react-from-document-updates.html").read_text(encoding="utf-8")
        script = re.search(r"<script>(.*?)</script>", text, re.S).group(1)
        self.assertIn('id="summary"', text)
        self.run_node('import assert from "node:assert/strict";\n'
                      'const writes = [];\n'
                      'const document = { querySelector(selector) {\n'
                      'assert.equal(selector, "#summary");\n'
                      'return {set textContent(value) { writes.push(value); }}; }};\n'
                      + script + '\nassert.deepEqual(writes, ["样本数：3", "样本数：5"]);')


if __name__ == "__main__":
    unittest.main()

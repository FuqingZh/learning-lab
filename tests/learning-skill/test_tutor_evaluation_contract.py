#!/usr/bin/env python3
"""Contract tests for the static tutor evaluation suite."""

from __future__ import annotations

import json
import hashlib
import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "run-tutor-evaluation.py"
FIXTURES = ROOT / "tests" / "tutor-evaluation" / "cases.yaml"


def load_evaluation_module() -> object:
    specification = importlib.util.spec_from_file_location("tutor_evaluation", SCRIPT)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


class TutorEvaluationContractTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["python3", str(SCRIPT), *arguments], check=False, text=True, capture_output=True)

    def valid_combined_scorecard(self, attempts: int = 3) -> dict[str, object]:
        cases = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))["cases"]
        return {
            "schema_version": 1,
            "fixture_hash": hashlib.sha256(FIXTURES.read_bytes()).hexdigest(),
            "runner": {
                "provider": "example", "model": "example-2026-08-27", "immutable_digest": "sha256:abc",
                "runner_name": "manual", "runner_version": "1", "reasoning_effort": "documented",
                "tool_policy": "no-tools", "sandbox": "isolated",
            },
            "split": "combined",
            "aggregate": "pass",
            "limitations": ["Synthetic fixture contract only."],
            "case_results": [
                {
                    "case_id": case["id"], "attempt_index": attempt, "status": "pass",
                    "observable_criteria": {criterion: True for criterion in case["observable_criteria"]},
                    "critical_flags": {flag: True for flag in case["critical_flags"]},
                }
                for case in cases for attempt in range(1, attempts + 1)
            ],
        }

    def test_six_cases_cover_authoring_and_holdout_contracts(self) -> None:
        fixtures = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
        cases = {case["id"]: case for case in fixtures["cases"]}
        self.assertEqual(set(cases), {
            "due-vs-resume", "due-retrieval-no-disclosure", "stop-with-v2-resume",
            "assisted-review-cue", "noncanonical-bio-lesson", "chinese-source-and-check",
        })
        self.assertEqual(cases["chinese-source-and-check"]["split"], "holdout")
        self.assertTrue(all(cases[case_id]["split"] == "authoring" for case_id in cases if case_id != "chinese-source-and-check"))
        for case in cases.values():
            self.assertTrue(case["allowed_sources"])
            self.assertTrue(case["learner_turns"])
            self.assertTrue(case["observable_criteria"])
            self.assertTrue(case["critical_flags"])

    def test_fixture_validation_rejects_missing_observable_contract(self) -> None:
        fixtures = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
        fixtures["cases"][0].pop("observable_criteria")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "broken.yaml"
            path.write_text(yaml.safe_dump(fixtures, allow_unicode=True), encoding="utf-8")
            result = self.run_cli("validate-fixtures", "--fixtures", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("case fields mismatch", result.stderr)

    def test_fixture_validation_rejects_nonexistent_repository_source(self) -> None:
        fixtures = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
        fixtures["cases"][0]["allowed_sources"][0] = "lessons/not-a-real-unit.md"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "broken-source.yaml"
            path.write_text(yaml.safe_dump(fixtures, allow_unicode=True), encoding="utf-8")
            result = self.run_cli("validate-fixtures", "--fixtures", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a repository file", result.stderr)

    def test_static_verification_is_deterministic_and_replays_state_cases(self) -> None:
        first = self.run_cli("verify-static")
        second = self.run_cli("verify-static")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertIn("static verification passed", first.stdout)

    def test_synthetic_event_identifier_cannot_escape_isolated_root(self) -> None:
        module = load_evaluation_module()
        with tempfile.TemporaryDirectory() as temporary:
            outside = Path(temporary) / "outside.yaml"
            for identifier in ("../../outside", str(outside)):
                event = f"schema_version: 2\nid: {identifier}\n"
                with self.assertRaisesRegex(ValueError, "timestamped stable-id"):
                    module.build_isolated_root(event)
            self.assertFalse(outside.exists())

    def test_scorecard_rejects_wrong_fixture_hash_and_unknown_result_fields(self) -> None:
        scorecard = {
            "schema_version": 1,
            "fixture_hash": "0" * 64,
            "runner": {
                "provider": "example", "model": "example-2026-08-27", "immutable_digest": "sha256:abc",
                "runner_name": "manual", "runner_version": "1", "reasoning_effort": "documented",
                "tool_policy": "no-tools", "sandbox": "isolated",
            },
            "split": "holdout",
            "aggregate": "incomplete",
            "limitations": ["Synthetic fixture contract only."],
            "case_results": [{
                "case_id": "chinese-source-and-check", "status": "not-run",
                "attempt_index": 1,
                "observable_criteria": {"Chinese-first": False}, "critical_flags": {"no invention": True},
                "unexpected": True,
            }],
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "scorecard.json"
            path.write_text(json.dumps(scorecard), encoding="utf-8")
            result = self.run_cli("validate-scorecard", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fixture_hash", result.stderr)

        scorecard["fixture_hash"] = hashlib.sha256(FIXTURES.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "scorecard.json"
            path.write_text(json.dumps(scorecard), encoding="utf-8")
            result = self.run_cli("validate-scorecard", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid fields", result.stderr)

    def test_scorecard_requires_frozen_runner_context_and_attempt_index(self) -> None:
        scorecard = {
            "schema_version": 1,
            "fixture_hash": hashlib.sha256(FIXTURES.read_bytes()).hexdigest(),
            "runner": {"provider": "example"},
            "split": "holdout",
            "aggregate": "incomplete",
            "limitations": ["Synthetic fixture contract only."],
            "case_results": [{
                "case_id": "chinese-source-and-check", "attempt_index": 0, "status": "not-run",
                "observable_criteria": {"Chinese-first": False}, "critical_flags": {"no invention": True},
            }],
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "scorecard.json"
            path.write_text(json.dumps(scorecard), encoding="utf-8")
            result = self.run_cli("validate-scorecard", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("frozen provider", result.stderr)

        scorecard["runner"] = {
            "provider": "example", "model": "example-2026-08-27", "immutable_digest": "sha256:abc",
            "runner_name": "manual", "runner_version": "1", "reasoning_effort": "documented",
            "tool_policy": "no-tools", "sandbox": "isolated",
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "scorecard.json"
            path.write_text(json.dumps(scorecard), encoding="utf-8")
            result = self.run_cli("validate-scorecard", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("attempt_index", result.stderr)

    def test_scorecard_binds_boolean_keys_and_aggregate_to_fixture_results(self) -> None:
        scorecard = self.valid_combined_scorecard()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "scorecard.json"
            path.write_text(json.dumps(scorecard), encoding="utf-8")
            result = self.run_cli("validate-scorecard", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)

        scorecard["case_results"][0]["observable_criteria"] = {"unrelated": True}  # type: ignore[index]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "scorecard.json"
            path.write_text(json.dumps(scorecard), encoding="utf-8")
            result = self.run_cli("validate-scorecard", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("keys must exactly match", result.stderr)

        scorecard = self.valid_combined_scorecard()
        scorecard["aggregate"] = "mixed"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "scorecard.json"
            path.write_text(json.dumps(scorecard), encoding="utf-8")
            result = self.run_cli("validate-scorecard", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fully passing", result.stderr)

        scorecard = self.valid_combined_scorecard()
        scorecard["case_results"][0]["status"] = "not-run"  # type: ignore[index]
        scorecard["aggregate"] = "pass"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "scorecard.json"
            path.write_text(json.dumps(scorecard), encoding="utf-8")
            result = self.run_cli("validate-scorecard", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("aggregate incomplete", result.stderr)

    def test_pass_requires_combined_three_attempts_and_existing_file_facts(self) -> None:
        scorecard = self.valid_combined_scorecard(attempts=1)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "scorecard.json"
            path.write_text(json.dumps(scorecard), encoding="utf-8")
            result = self.run_cli("validate-scorecard", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fewer-than-three-attempt", result.stderr)

        scorecard = self.valid_combined_scorecard()
        scorecard["split"] = "holdout"
        scorecard["case_results"] = [result for result in scorecard["case_results"] if result["case_id"] == "chinese-source-and-check"]  # type: ignore[index]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "scorecard.json"
            path.write_text(json.dumps(scorecard), encoding="utf-8")
            result = self.run_cli("validate-scorecard", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("non-combined", result.stderr)

        fixtures = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
        state_case = next(case for case in fixtures["cases"] if case["id"] == "stop-with-v2-resume")
        state_case["expected_file_facts"] = ["learning-state/sessions/not-the-event.yaml"]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "wrong-file-fact.yaml"
            path.write_text(yaml.safe_dump(fixtures, allow_unicode=True), encoding="utf-8")
            result = self.run_cli("verify-static", "--fixtures", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expected file fact", result.stderr)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Validate static tutor-evaluation fixtures and scorecard contracts.

Examples:
  python3 scripts/run-tutor-evaluation.py validate-fixtures
  python3 scripts/run-tutor-evaluation.py verify-static
  python3 scripts/run-tutor-evaluation.py validate-scorecard result.json

This CLI does not invoke a model.  ``verify-static`` checks the privacy-safe
fixtures and replays the two state-engine cases in isolated temporary roots.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
import re

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURES = ROOT / "tests" / "tutor-evaluation" / "cases.yaml"
SCORECARD_SCHEMA = ROOT / "tests" / "tutor-evaluation" / "scorecard.schema.json"
REQUIRED_CASE_IDS = {
    "due-vs-resume", "due-retrieval-no-disclosure", "stop-with-v2-resume",
    "assisted-review-cue", "noncanonical-bio-lesson", "chinese-source-and-check",
}
REQUIRED_CASE_FIELDS = {
    "id", "split", "purpose", "allowed_sources", "learner_turns", "state_facts",
    "observable_criteria", "critical_flags", "expected_file_facts",
}
RUNNER_FIELDS = {
    "provider", "model", "immutable_digest", "runner_name", "runner_version",
    "reasoning_effort", "tool_policy", "sandbox",
}
SCORECARD_FIELDS = {"schema_version", "fixture_hash", "runner", "split", "aggregate", "limitations", "case_results"}
CASE_RESULT_FIELDS = {"case_id", "attempt_index", "status", "observable_criteria", "critical_flags"}
EVENT_ID = re.compile(r"^[0-9]{8}T[0-9]{6}(?:Z|[+-][0-9]{4})-[a-z0-9]+(?:-[a-z0-9]+)*$")


class EvaluationContractError(ValueError):
    """Raised when an evaluation fixture or scorecard violates its contract."""


def load_fixtures(path: Path) -> dict[str, Any]:
    """Load and validate the versioned, privacy-safe case fixture document."""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise EvaluationContractError(f"invalid fixture YAML: {error}") from error
    if not isinstance(data, dict) or set(data) != {"schema_version", "suite", "cases"}:
        raise EvaluationContractError("fixtures must contain only schema_version, suite, and cases")
    if data["schema_version"] != 1 or not isinstance(data["suite"], str) or not data["suite"].strip():
        raise EvaluationContractError("fixtures require schema_version 1 and a non-empty suite")
    cases = data["cases"]
    if not isinstance(cases, list) or len(cases) != len(REQUIRED_CASE_IDS):
        raise EvaluationContractError("fixtures must contain exactly six cases")
    identifiers: set[str] = set()
    splits: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise EvaluationContractError("each case must be a mapping")
        unknown = set(case) - (REQUIRED_CASE_FIELDS | {"event_yaml", "expected_state"})
        missing = REQUIRED_CASE_FIELDS - set(case)
        if missing or unknown:
            raise EvaluationContractError(f"case fields mismatch: missing={sorted(missing)}, unknown={sorted(unknown)}")
        identifier = case["id"]
        if not isinstance(identifier, str) or not identifier:
            raise EvaluationContractError("case id must be a non-empty string")
        identifiers.add(identifier)
        split = case["split"]
        if split not in {"authoring", "holdout"}:
            raise EvaluationContractError(f"{identifier}: split must be authoring or holdout")
        splits.add(split)
        for field in ("allowed_sources", "learner_turns", "observable_criteria", "critical_flags"):
            value = case[field]
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
                raise EvaluationContractError(f"{identifier}: {field} must be a non-empty list of strings")
        for source in case["allowed_sources"]:
            if source.startswith("synthetic://"):
                continue
            candidate = (ROOT / source).resolve()
            if Path(source).is_absolute() or ROOT not in candidate.parents or not candidate.is_file():
                raise EvaluationContractError(f"{identifier}: allowed source is not a repository file: {source}")
        expected_files = case["expected_file_facts"]
        if not isinstance(expected_files, list) or not all(isinstance(item, str) and item.strip() for item in expected_files):
            raise EvaluationContractError(f"{identifier}: expected_file_facts must be a list of strings")
        if not isinstance(case["state_facts"], dict):
            raise EvaluationContractError(f"{identifier}: state_facts must be a mapping")
        if not isinstance(case["purpose"], str) or not case["purpose"].strip():
            raise EvaluationContractError(f"{identifier}: purpose must be a non-empty string")
        if not case["critical_flags"]:
            raise EvaluationContractError(f"{identifier}: at least one critical flag is required")
        has_event = "event_yaml" in case
        has_expected_state = "expected_state" in case
        if has_event != has_expected_state:
            raise EvaluationContractError(f"{identifier}: event_yaml and expected_state must occur together")
        resume = case["state_facts"].get("resume")
        if resume is not None:
            if not isinstance(resume, dict) or resume.get("unit_kind") != "lesson" or not isinstance(resume.get("unit_ref"), str):
                raise EvaluationContractError(f"{identifier}: state resume must identify a lesson unit")
            unit = (ROOT / resume["unit_ref"]).resolve()
            if unit.suffix != ".md" or ROOT not in unit.parents or not unit.is_file():
                raise EvaluationContractError(f"{identifier}: state resume lesson is not a repository file")
    if identifiers != REQUIRED_CASE_IDS:
        raise EvaluationContractError(f"fixture case ids must equal {sorted(REQUIRED_CASE_IDS)}")
    if splits != {"authoring", "holdout"}:
        raise EvaluationContractError("fixtures must include authoring and holdout cases")
    return data


def fixture_hash(path: Path) -> str:
    """Return the SHA-256 of the exact fixture bytes for result provenance."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def minimal_concept(identifier: str, title: str) -> str:
    return f"""---
id: {identifier}
title: {title}
summary: Synthetic evaluation concept.
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
  checked_on: '2026-08-21'
  sources:
    - url: https://www.rfc-editor.org/rfc/rfc9110.html
      publisher: RFC Editor
      kind: standard
    - url: https://docs.oracle.com/javase/specs/jls/se24/html/jls-15.html
      publisher: Oracle
      kind: professional-documentation
---

# {title}
"""


def build_isolated_root(event_yaml: str) -> tempfile.TemporaryDirectory[str]:
    """Build the smallest valid repository root for a state-engine replay."""
    try:
        event = yaml.safe_load(event_yaml)
    except yaml.YAMLError as error:
        raise EvaluationContractError(f"invalid synthetic event YAML: {error}") from error
    if not isinstance(event, dict) or not isinstance(event.get("id"), str) or EVENT_ID.fullmatch(event["id"]) is None:
        raise EvaluationContractError("synthetic event id must use production timestamped stable-id syntax")
    identifier = event["id"]
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    for directory in (
        "concepts", "case-labs", "lessons", "learning-state/sessions", "learning-records/track-a",
        "scripts", "tracks/track-a",
    ):
        (root / directory).mkdir(parents=True, exist_ok=True)
    (root / "concepts" / "alpha.md").write_text(minimal_concept("alpha", "Idempotency"), encoding="utf-8")
    (root / "concepts" / "beta.md").write_text(minimal_concept("beta", "Side effect"), encoding="utf-8")
    (root / "lessons" / "recovery.md").write_text("# Recovery\n", encoding="utf-8")
    for script_name in ("build-knowledge-map.py", "build-learning-state.py", "learning_records.py"):
        shutil.copy2(ROOT / "scripts" / script_name, root / "scripts" / script_name)
    (root / "learning-state" / "sessions" / f"{identifier}.yaml").write_text(event_yaml, encoding="utf-8")
    return temporary


def run_state(root: Path, command: str, *arguments: str) -> dict[str, Any]:
    """Run the production state CLI against an isolated fixture root."""
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build-learning-state.py"), command, "--root", str(root), *arguments],
        check=False, text=True, capture_output=True,
    )
    if result.returncode:
        raise EvaluationContractError(f"state replay failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def verify_state_case(case: dict[str, Any]) -> None:
    """Replay a fixture event and compare only the declared observable state facts."""
    with build_isolated_root(case["event_yaml"]) as temporary:
        root = Path(temporary)
        expected_files: set[Path] = set()
        for reference in case["expected_file_facts"]:
            candidate = Path(reference)
            resolved = (root / candidate).resolve()
            if candidate.is_absolute() or candidate.as_posix() != reference or root not in resolved.parents or not resolved.is_file():
                raise EvaluationContractError(f"{case['id']}: expected file fact is not a canonical existing isolated-root path: {reference}")
            expected_files.add(candidate)
        session_root = root / "learning-state" / "sessions"
        inventory = {path.relative_to(root) for path in session_root.glob("*.yaml")}
        if inventory != expected_files:
            raise EvaluationContractError(f"{case['id']}: expected file facts must exactly match the synthetic session inventory")
        state = run_state(root, "normalized-data")
        expected = case["expected_state"]
        concept = next(item for item in state["concepts"] if item["id"] == expected["concept"])
        for field in ("capability_state", "evidence_count", "next_review"):
            if concept[field] != expected[field]:
                raise EvaluationContractError(f"{case['id']}: expected {field}={expected[field]!r}, got {concept[field]!r}")
        for field, value in expected.get("resume", {}).items():
            if state["resume"][field] != value:
                raise EvaluationContractError(f"{case['id']}: expected resume.{field}={value!r}")
        review_day = expected.get("review_cue_today")
        if review_day:
            cue = run_state(root, "list-review-cues", "--today", review_day)
            if [item["id"] for item in cue["due"]] != [expected["concept"]]:
                raise EvaluationContractError(f"{case['id']}: expected exactly one review cue for {expected['concept']}")


def validate_scorecard(path: Path, fixtures_path: Path) -> None:
    """Validate portable scorecard structure without interpreting a model result."""
    try:
        scorecard = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvaluationContractError(f"invalid scorecard JSON: {error}") from error
    schema = json.loads(SCORECARD_SCHEMA.read_text(encoding="utf-8"))
    required = set(schema["required"])
    if not isinstance(scorecard, dict) or set(scorecard) != required or required != SCORECARD_FIELDS:
        raise EvaluationContractError("scorecard fields must exactly match the published schema")
    if scorecard["schema_version"] != 1:
        raise EvaluationContractError("scorecard schema_version must be 1")
    if scorecard["fixture_hash"] != fixture_hash(fixtures_path):
        raise EvaluationContractError("scorecard fixture_hash does not match the fixture bytes")
    runner = scorecard["runner"]
    if not isinstance(runner, dict) or set(runner) != RUNNER_FIELDS or not all(isinstance(value, str) and value.strip() for value in runner.values()):
        raise EvaluationContractError("scorecard runner must contain frozen provider, model, digest, runner, reasoning, tool, and sandbox fields")
    if scorecard["split"] not in {"authoring", "holdout", "combined"}:
        raise EvaluationContractError("scorecard split is invalid")
    if scorecard["aggregate"] not in {"pass", "fail", "mixed", "incomplete"}:
        raise EvaluationContractError("scorecard aggregate is invalid")
    if not isinstance(scorecard["limitations"], list) or not scorecard["limitations"] or not all(isinstance(item, str) and item.strip() for item in scorecard["limitations"]):
        raise EvaluationContractError("scorecard limitations must be a non-empty list of strings")
    if not isinstance(scorecard["case_results"], list) or not scorecard["case_results"]:
        raise EvaluationContractError("scorecard case_results must be non-empty")
    fixtures = load_fixtures(fixtures_path)
    cases_by_id = {case["id"]: case for case in fixtures["cases"]}
    selected_cases = {
        identifier for identifier, case in cases_by_id.items()
        if scorecard["split"] == "combined" or case["split"] == scorecard["split"]
    }
    attempts: set[tuple[str, int]] = set()
    covered_cases: set[str] = set()
    has_not_run = False
    all_passed_and_true = True
    for result in scorecard["case_results"]:
        if not isinstance(result, dict) or set(result) != CASE_RESULT_FIELDS:
            raise EvaluationContractError("each scorecard result has invalid fields")
        if result["case_id"] not in REQUIRED_CASE_IDS or result["status"] not in {"pass", "fail", "not-run"}:
            raise EvaluationContractError("scorecard result has invalid case_id or status")
        if result["case_id"] not in selected_cases:
            raise EvaluationContractError("scorecard result does not belong to its declared split")
        if isinstance(result["attempt_index"], bool) or not isinstance(result["attempt_index"], int) or result["attempt_index"] < 1:
            raise EvaluationContractError("scorecard result attempt_index must be a positive integer")
        attempt = (result["case_id"], result["attempt_index"])
        if attempt in attempts:
            raise EvaluationContractError("scorecard result repeats a case attempt")
        attempts.add(attempt)
        covered_cases.add(result["case_id"])
        for field in ("observable_criteria", "critical_flags"):
            if not isinstance(result[field], dict) or not result[field] or not all(isinstance(key, str) and isinstance(value, bool) for key, value in result[field].items()):
                raise EvaluationContractError(f"scorecard {field} must be a non-empty boolean map")
            expected_keys = set(cases_by_id[result["case_id"]][field])
            if set(result[field]) != expected_keys:
                raise EvaluationContractError(f"scorecard {field} keys must exactly match fixture {result['case_id']}")
        if result["status"] == "not-run":
            has_not_run = True
        if result["status"] != "pass" or not all(result["observable_criteria"].values()) or not all(result["critical_flags"].values()):
            all_passed_and_true = False
    attempt_counts = {identifier: 0 for identifier in REQUIRED_CASE_IDS}
    for identifier, _ in attempts:
        attempt_counts[identifier] += 1
    completion_incomplete = (
        scorecard["split"] != "combined"
        or covered_cases != REQUIRED_CASE_IDS
        or has_not_run
        or any(attempt_counts[identifier] < 3 for identifier in REQUIRED_CASE_IDS)
    )
    if completion_incomplete:
        if scorecard["aggregate"] != "incomplete":
            raise EvaluationContractError("partial, not-run, non-combined, or fewer-than-three-attempt scorecards must use aggregate incomplete")
    elif all_passed_and_true:
        if scorecard["aggregate"] != "pass":
            raise EvaluationContractError("fully passing three-attempt combined scorecards must use aggregate pass")
    elif scorecard["aggregate"] not in {"fail", "mixed"}:
        raise EvaluationContractError("complete observed failures must use aggregate fail or mixed")


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate-fixtures", "verify-static", "validate-scorecard"))
    parser.add_argument("scorecard", nargs="?", type=Path)
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parsed = parser.parse_args(arguments)
    if parsed.command == "validate-scorecard" and parsed.scorecard is None:
        parser.error("validate-scorecard requires a scorecard JSON path")
    if parsed.command != "validate-scorecard" and parsed.scorecard is not None:
        parser.error("a scorecard path is valid only with validate-scorecard")
    return parsed


def main(arguments: list[str] | None = None) -> int:
    """Execute a deterministic structural check; never invoke an external model."""
    parsed = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    try:
        fixtures = load_fixtures(parsed.fixtures)
        if parsed.command == "verify-static":
            for case in fixtures["cases"]:
                if "event_yaml" in case:
                    verify_state_case(case)
            print(f"tutor evaluation: static verification passed ({len(fixtures['cases'])} fixtures, sha256={fixture_hash(parsed.fixtures)})")
        elif parsed.command == "validate-scorecard":
            validate_scorecard(parsed.scorecard, parsed.fixtures)
            print("tutor evaluation: scorecard valid")
        else:
            print(f"tutor evaluation: fixtures valid ({len(fixtures['cases'])} cases, sha256={fixture_hash(parsed.fixtures)})")
    except EvaluationContractError as error:
        print(f"tutor evaluation validation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate append-only learning events and derive deterministic learning state."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml
from yaml.constructor import ConstructorError
from yaml.resolver import BaseResolver


SCHEMA_VERSION = 1
EVENT_SCHEMA_VERSIONS = frozenset({1, 2})
SCHEDULER = {"id": "fixed-v2-distinct-days", "pass_intervals_days": [1, 7, 21, 60],
             "success_unit": "utc-calendar-day"}
MODES = frozenset(
    {"guided-lesson", "contextual-review", "real-work-application", "consolidation"}
)
CHECKS = frozenset(
    {"exposure", "explain-back", "boundary-decision", "fresh-case-transfer", "real-work-application"}
)
OUTCOMES = frozenset({"pass", "partial", "miss"})
CONFIDENCES = frozenset({"low", "medium", "high"})
STABLE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EVENT_ID = re.compile(
    r"^(?P<timestamp>[0-9]{8}T[0-9]{6}(?:Z|[+-][0-9]{4}))-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)$"
)
EVENT_FIELDS = frozenset(
    {"schema_version", "id", "started_at", "duration_minutes", "mode", "track", "resume", "evidence"}
)
V1_RESUME_FIELDS = frozenset({"from", "next", "summary"})
V2_RESUME_FIELDS = frozenset({"unit_kind", "unit_ref", "checkpoint", "summary"})
RESUME_UNIT_KINDS = frozenset({"concept", "track", "lesson"})
EVIDENCE_FIELDS = frozenset({"concept", "check", "outcome", "confidence", "assisted"})
MAX_DURATION_MINUTES = 24 * 60


class LearningStateError(ValueError):
    """Raised when a learning-state source contract is invalid."""


class UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys at every depth."""


def construct_unique_mapping(
    loader: UniqueKeySafeLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as error:
            raise ConstructorError(
                "while constructing a mapping", node.start_mark,
                "found an unhashable mapping key", key_node.start_mark,
            ) from error
        if duplicate:
            raise ConstructorError(
                "while constructing a mapping", node.start_mark,
                f"found duplicate key {key!r}", key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping)


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=("validate", "normalized-data", "list-due", "list-review-cues")
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--today", help="ISO calendar date used only by list-due")
    parsed = parser.parse_args(arguments)
    due_commands = {"list-due", "list-review-cues"}
    if parsed.command in due_commands and parsed.today is None:
        parser.error(f"{parsed.command} requires --today YYYY-MM-DD")
    if parsed.command not in due_commands and parsed.today is not None:
        parser.error("--today is only valid with list-due or list-review-cues")
    return parsed


def require_string(value: Any, *, field: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LearningStateError(f"{path}: {field} must be a non-empty string")
    return value.strip()


def require_exact_fields(value: Any, *, fields: frozenset[str], label: str, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise LearningStateError(f"{path}: {label} must be a mapping with string keys")
    missing = sorted(fields - set(value))
    unknown = sorted(set(value) - fields)
    if missing:
        raise LearningStateError(f"{path}: {label} missing required fields: {', '.join(missing)}")
    if unknown:
        raise LearningStateError(f"{path}: {label} has unknown fields: {', '.join(unknown)}")
    return value


def parse_timestamp(value: Any, *, path: Path) -> tuple[dt.datetime, str]:
    if isinstance(value, dt.datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise LearningStateError(f"{path}: started_at must include a UTC offset")
        return value, value.strftime("%Y%m%dT%H%M%S%z")
    timestamp = require_string(value, field="started_at", path=path)
    try:
        parsed = dt.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as error:
        raise LearningStateError(f"{path}: started_at must be a valid ISO-8601 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LearningStateError(f"{path}: started_at must include a UTC offset")
    suffix = "Z" if timestamp.endswith("Z") else parsed.strftime("%z")
    return parsed, parsed.strftime("%Y%m%dT%H%M%S") + suffix


def read_yaml(path: Path) -> dict[str, Any]:
    try:
        parsed = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeySafeLoader)
    except (OSError, yaml.YAMLError) as error:
        raise LearningStateError(f"{path}: invalid YAML: {error}") from error
    if parsed is None:
        raise LearningStateError(f"{path}: event must be a mapping")
    return require_exact_fields(parsed, fields=EVENT_FIELDS, label="event", path=path)


def parse_v2_resume(
    resume: Any, *, path: Path, root: Path, concepts: set[str], tracks: set[str]
) -> dict[str, Any]:
    """Validate a v2 recovery cue without coupling it to the event's track."""
    resume = require_exact_fields(resume, fields=V2_RESUME_FIELDS, label="resume", path=path)
    unit_kind = require_string(resume["unit_kind"], field="resume.unit_kind", path=path)
    if unit_kind not in RESUME_UNIT_KINDS:
        raise LearningStateError(
            f"{path}: resume.unit_kind must be one of {', '.join(sorted(RESUME_UNIT_KINDS))}"
        )
    unit_ref = require_string(resume["unit_ref"], field="resume.unit_ref", path=path)
    if unit_kind == "concept":
        if unit_ref not in concepts:
            raise LearningStateError(f"{path}: unknown resume concept: {unit_ref}")
    elif unit_kind == "track":
        if unit_ref not in tracks:
            raise LearningStateError(f"{path}: unknown resume track: {unit_ref}")
    else:
        lesson_root = (root / "lessons").resolve()
        candidate = Path(unit_ref)
        if (
            candidate.is_absolute()
            or candidate.suffix != ".md"
            or candidate.as_posix() != unit_ref
            or not candidate.parts
            or candidate.parts[0] != "lessons"
            or ".." in candidate.parts
        ):
            raise LearningStateError(f"{path}: resume lesson must be a canonical lessons-relative .md path")
        resolved = (root / candidate).resolve()
        if lesson_root not in resolved.parents or not resolved.is_file():
            raise LearningStateError(f"{path}: unknown resume lesson: {unit_ref}")
    return {
        "unit_kind": unit_kind,
        "unit_ref": unit_ref,
        "checkpoint": require_string(resume["checkpoint"], field="resume.checkpoint", path=path),
        "summary": require_string(resume["summary"], field="resume.summary", path=path),
        "legacy": False,
    }


def parse_event(path: Path, *, root: Path, concepts: set[str], tracks: set[str]) -> dict[str, Any]:
    raw = read_yaml(path)
    event_schema_version = raw["schema_version"]
    if isinstance(event_schema_version, bool) or event_schema_version not in EVENT_SCHEMA_VERSIONS:
        raise LearningStateError(f"{path}: schema_version must be 1 or 2")
    identifier = require_string(raw["id"], field="id", path=path)
    event_id = EVENT_ID.fullmatch(identifier)
    if event_id is None:
        raise LearningStateError(f"{path}: id must use timestamped stable-id syntax")
    if path.name != f"{identifier}.yaml":
        raise LearningStateError(f"{path}: filename must equal event id plus .yaml")
    started_at, id_timestamp = parse_timestamp(raw["started_at"], path=path)
    if event_id.group("timestamp") != id_timestamp:
        raise LearningStateError(f"{path}: id timestamp prefix must match started_at")
    duration = raw["duration_minutes"]
    if isinstance(duration, bool) or not isinstance(duration, int) or not 1 <= duration <= MAX_DURATION_MINUTES:
        raise LearningStateError(f"{path}: duration_minutes must be an integer from 1 to {MAX_DURATION_MINUTES}")
    mode = require_string(raw["mode"], field="mode", path=path)
    if mode not in MODES:
        raise LearningStateError(f"{path}: mode must be one of {', '.join(sorted(MODES))}")
    track = require_string(raw["track"], field="track", path=path)
    if track not in tracks:
        raise LearningStateError(f"{path}: unknown track: {track}")

    if event_schema_version == 1:
        legacy_resume = require_exact_fields(raw["resume"], fields=V1_RESUME_FIELDS, label="resume", path=path)
        for field in ("from", "next"):
            value = require_string(legacy_resume[field], field=f"resume.{field}", path=path)
            if value not in concepts:
                raise LearningStateError(f"{path}: unknown resume concept: {value}")
        resume = {
            "unit_kind": "concept",
            "unit_ref": legacy_resume["next"].strip(),
            "checkpoint": None,
            "summary": require_string(legacy_resume["summary"], field="resume.summary", path=path),
            "legacy": True,
            "from": legacy_resume["from"].strip(),
            "next": legacy_resume["next"].strip(),
        }
    else:
        resume = parse_v2_resume(raw["resume"], path=path, root=root, concepts=concepts, tracks=tracks)

    if not isinstance(raw["evidence"], list):
        raise LearningStateError(f"{path}: evidence must be a list")
    evidence: list[dict[str, Any]] = []
    seen_concepts: set[str] = set()
    for index, item in enumerate(raw["evidence"]):
        item = require_exact_fields(item, fields=EVIDENCE_FIELDS, label=f"evidence[{index}]", path=path)
        concept = require_string(item["concept"], field=f"evidence[{index}].concept", path=path)
        if concept not in concepts:
            raise LearningStateError(f"{path}: unknown evidence concept: {concept}")
        if concept in seen_concepts:
            raise LearningStateError(f"{path}: duplicate concept evidence: {concept}")
        seen_concepts.add(concept)
        check = require_string(item["check"], field=f"evidence[{index}].check", path=path)
        outcome = require_string(item["outcome"], field=f"evidence[{index}].outcome", path=path)
        confidence = require_string(item["confidence"], field=f"evidence[{index}].confidence", path=path)
        if check not in CHECKS:
            raise LearningStateError(f"{path}: invalid evidence check: {check}")
        if outcome not in OUTCOMES:
            raise LearningStateError(f"{path}: invalid evidence outcome: {outcome}")
        if confidence not in CONFIDENCES:
            raise LearningStateError(f"{path}: invalid evidence confidence: {confidence}")
        if not isinstance(item["assisted"], bool):
            raise LearningStateError(f"{path}: evidence[{index}].assisted must be boolean")
        evidence.append({
            "concept": concept, "check": check, "outcome": outcome,
            "confidence": confidence, "assisted": item["assisted"],
        })

    return {
        "id": identifier,
        "started_at": started_at.isoformat(),
        "started_at_value": started_at,
        "duration_minutes": duration,
        "mode": mode,
        "track": track,
        "resume": resume,
        "evidence": evidence,
    }


def load_graph(root: Path) -> dict[str, Any]:
    command = [sys.executable, str(root / "scripts" / "build-knowledge-map.py"), "normalized-data", "--root", str(root)]
    result = subprocess.run(command, check=False, text=True, capture_output=True)
    if result.returncode:
        raise LearningStateError(f"knowledge graph validation failed: {result.stderr.strip()}")
    try:
        graph = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise LearningStateError("knowledge graph normalized-data was not JSON") from error
    if graph.get("schema_version") != SCHEMA_VERSION:
        raise LearningStateError("knowledge graph schema_version is unsupported")
    return graph


def load_events(root: Path, graph: dict[str, Any]) -> list[dict[str, Any]]:
    directory = root / "learning-state" / "sessions"
    if not directory.is_dir():
        raise LearningStateError(f"missing session directory: {directory}")
    concepts = {node["id"] for node in graph["nodes"]}
    tracks = set(graph["tracks"])
    events = [
        parse_event(path, root=root, concepts=concepts, tracks=tracks)
        for path in sorted(directory.glob("*.yaml"))
    ]
    identifiers = [event["id"] for event in events]
    if len(set(identifiers)) != len(identifiers):
        raise LearningStateError("duplicate event ids")
    return sorted(events, key=lambda event: (event["started_at_value"], event["id"]))


def capability_state(history: list[dict[str, Any]]) -> str:
    passing = [item for item in history if item["outcome"] == "pass" and not item["assisted"]]
    if not passing:
        return "unassessed"
    result = "encountered" if any(item["check"] == "exposure" for item in passing) else "unassessed"
    if any(item["check"] in {"explain-back", "boundary-decision"} for item in passing):
        result = "familiar"
    transfer = [item for item in passing if item["check"] in {"fresh-case-transfer", "real-work-application"}]
    if transfer:
        result = "usable"
    for candidate in transfer:
        if any(
            earlier["started_at_value"].date() <= candidate["started_at_value"].date() - dt.timedelta(days=7)
            for earlier in passing
            if earlier is not candidate
        ):
            return "retained"
    return result


def next_review(history: list[dict[str, Any]]) -> str | None:
    if not history:
        return None
    latest = history[-1]
    if latest["assisted"] or latest["outcome"] in {"partial", "miss"}:
        interval = 1
    else:
        # Repeated checks in one day are observations, not spaced successes.
        # Normalize offsets before bucketing; raw evidence and capability stay intact.
        successes = len({item["started_at_value"].astimezone(dt.timezone.utc).date()
                         for item in history if item["outcome"] == "pass" and not item["assisted"]})
        interval = SCHEDULER["pass_intervals_days"][min(successes, 4) - 1]
    return (latest["started_at_value"].date() + dt.timedelta(days=interval)).isoformat()


def build_state(root: Path) -> dict[str, Any]:
    graph = load_graph(root)
    events = load_events(root, graph)
    histories: dict[str, list[dict[str, Any]]] = {node["id"]: [] for node in graph["nodes"]}
    for event in events:
        for item in event["evidence"]:
            histories[item["concept"]].append({**item, "started_at_value": event["started_at_value"]})
    concepts = []
    for identifier in sorted(histories):
        history = histories[identifier]
        latest = history[-1] if history else None
        upcoming = next_review(history)
        concepts.append({
            "id": identifier,
            "capability_state": capability_state(history),
            "review_state": "scheduled" if upcoming else "unassessed",
            "last_reviewed": latest["started_at_value"].isoformat() if latest else None,
            "next_review": upcoming,
            "evidence_count": len(history),
            "latest_outcome": latest["outcome"] if latest else None,
        })
    resume = None
    if events:
        latest_event = events[-1]
        resume = {"event_id": latest_event["id"], "track": latest_event["track"], **latest_event["resume"]}
    return {"schema_version": SCHEMA_VERSION, "scheduler": SCHEDULER, "concepts": concepts, "resume": resume}


def due_projection(state: dict[str, Any], today: dt.date) -> dict[str, Any]:
    due = []
    for concept in state["concepts"]:
        if concept["next_review"] is None:
            continue
        next_date = dt.date.fromisoformat(concept["next_review"])
        if next_date <= today:
            due.append({
                **concept,
                "due_state": "lapsed" if concept["latest_outcome"] in {"partial", "miss"} else "due",
                "overdue": next_date < today,
            })
    return {"schema_version": SCHEMA_VERSION, "today": today.isoformat(), "due": due}


def main(arguments: list[str] | None = None) -> int:
    parsed = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    try:
        state = build_state(parsed.root.resolve())
        if parsed.command == "validate":
            print(f"learning state: valid ({sum(item['evidence_count'] for item in state['concepts'])} evidence entries)")
        elif parsed.command == "normalized-data":
            print(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            try:
                today = dt.date.fromisoformat(parsed.today)
            except ValueError as error:
                raise LearningStateError("--today must use YYYY-MM-DD") from error
            print(json.dumps(due_projection(state, today), ensure_ascii=False, indent=2, sort_keys=True))
    except LearningStateError as error:
        print(f"learning state validation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Validate evidence-backed learning records and build their capability projection.

The public :func:`build_projection` API is deliberately separate from the
knowledge graph.  It makes records a learner-owned capability claim instead of
using record filenames or graph links as a proxy for learning.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from yaml.constructor import ConstructorError
from yaml.resolver import BaseResolver


_STATE_SPEC = importlib.util.spec_from_file_location(
    "learning_lab_build_learning_state", Path(__file__).with_name("build-learning-state.py")
)
if _STATE_SPEC is None or _STATE_SPEC.loader is None:  # pragma: no cover - installation failure
    raise RuntimeError("cannot load build-learning-state.py")
learning_state = importlib.util.module_from_spec(_STATE_SPEC)
sys.modules[_STATE_SPEC.name] = learning_state
_STATE_SPEC.loader.exec_module(learning_state)


SCHEMA_VERSION = 1
RECORD_FIELDS = frozenset(
    {
        "schema_version",
        "track",
        "concepts",
        "capability_state",
        "demonstrated_at",
        "assisted",
        "evidence_sessions",
        "supersedes",
    }
)
CAPABILITY_STATES = frozenset({"encountered", "familiar", "usable", "retained"})
RECALL_OR_APPLICATION = frozenset(
    {"explain-back", "boundary-decision", "fresh-case-transfer", "real-work-application"}
)
USABLE_CHECKS = frozenset({"fresh-case-transfer", "real-work-application"})
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class LearningRecordsError(ValueError):
    """Raised when a learning-record source contract is invalid."""


class UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe frontmatter loader that rejects duplicate mapping keys."""


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
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from error
        if duplicate:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping)


def _require_string(value: Any, *, field: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LearningRecordsError(f"{path}: {field} must be a non-empty string")
    return value.strip()


def _load_frontmatter(path: Path) -> dict[str, Any]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    except OSError as error:
        raise LearningRecordsError(f"cannot read {path}: {error}") from error
    if not lines or lines[0].strip() != "---":
        return {}
    closing = next((index for index, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if closing is None:
        raise LearningRecordsError(f"{path}: unterminated YAML frontmatter")
    try:
        metadata = yaml.load("".join(lines[1:closing]), Loader=UniqueKeySafeLoader)
    except yaml.YAMLError as error:
        raise LearningRecordsError(f"{path}: invalid YAML frontmatter: {error}") from error
    if metadata is None:
        return {}
    if not isinstance(metadata, dict) or not all(isinstance(key, str) for key in metadata):
        raise LearningRecordsError(f"{path}: YAML frontmatter must be a mapping with string keys")
    return metadata


def _relative_path(root: Path, value: Any, *, path: Path, field: str) -> str:
    reference = _require_string(value, field=field, path=path)
    candidate = Path(reference)
    if candidate.is_absolute() or candidate.as_posix() != reference or candidate.suffix != ".md":
        raise LearningRecordsError(f"{path}: {field} must be a canonical repository-relative .md path")
    resolved_root = root.resolve()
    target = (resolved_root / candidate).resolve()
    if resolved_root not in target.parents or not target.is_file():
        raise LearningRecordsError(f"{path}: {field} must name an existing repository file: {reference}")
    relative = target.relative_to(resolved_root).as_posix()
    if not relative.startswith("learning-records/"):
        raise LearningRecordsError(f"{path}: {field} must name a learning-records path")
    return relative


def _parse_date(value: Any, *, path: Path) -> str:
    if not isinstance(value, str) or not ISO_DATE.fullmatch(value):
        raise LearningRecordsError(f"{path}: demonstrated_at must be a quoted ISO calendar date")
    try:
        dt.date.fromisoformat(value)
    except ValueError as error:
        raise LearningRecordsError(f"{path}: demonstrated_at must be a valid ISO calendar date") from error
    return value


def _parse_structured_record(
    root: Path,
    path: Path,
    metadata: dict[str, Any],
    *,
    known_concepts: dict[str, set[str]],
    graph_record_links: dict[str, set[str]],
    tracks: set[str],
    events: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if set(metadata) != RECORD_FIELDS:
        missing = sorted(RECORD_FIELDS - set(metadata))
        unknown = sorted(set(metadata) - RECORD_FIELDS)
        parts = []
        if missing:
            parts.append("missing fields: " + ", ".join(missing))
        if unknown:
            parts.append("unknown fields: " + ", ".join(unknown))
        raise LearningRecordsError(f"{path}: structured record must use exact schema ({'; '.join(parts)})")
    if metadata["schema_version"] != SCHEMA_VERSION or isinstance(metadata["schema_version"], bool):
        raise LearningRecordsError(f"{path}: schema_version must be {SCHEMA_VERSION}")
    track = _require_string(metadata["track"], field="track", path=path)
    if track not in tracks:
        raise LearningRecordsError(f"{path}: unknown track: {track}")
    if path.parent.name != track:
        raise LearningRecordsError(f"{path}: record directory must match track {track}")
    raw_concepts = metadata["concepts"]
    if not isinstance(raw_concepts, list) or not raw_concepts:
        raise LearningRecordsError(f"{path}: concepts must be a non-empty list")
    concepts = [_require_string(item, field="concepts", path=path) for item in raw_concepts]
    if len(set(concepts)) != len(concepts):
        raise LearningRecordsError(f"{path}: concepts must not contain duplicates")
    for concept in concepts:
        if concept not in known_concepts:
            raise LearningRecordsError(f"{path}: unknown concept: {concept}")
        if track not in known_concepts[concept]:
            raise LearningRecordsError(f"{path}: concept {concept} is not covered by track {track}")
    capability_state = _require_string(metadata["capability_state"], field="capability_state", path=path)
    if capability_state not in CAPABILITY_STATES:
        raise LearningRecordsError(f"{path}: capability_state must be one of {', '.join(sorted(CAPABILITY_STATES))}")
    demonstrated_at = _parse_date(metadata["demonstrated_at"], path=path)
    if metadata["assisted"] is not False:
        raise LearningRecordsError(f"{path}: assisted must be false")
    raw_sessions = metadata["evidence_sessions"]
    if not isinstance(raw_sessions, list) or not raw_sessions:
        raise LearningRecordsError(f"{path}: evidence_sessions must be a non-empty list")
    sessions = [_require_string(item, field="evidence_sessions", path=path) for item in raw_sessions]
    if len(set(sessions)) != len(sessions):
        raise LearningRecordsError(f"{path}: evidence_sessions must not contain duplicates")
    missing_sessions = sorted(set(sessions) - set(events))
    if missing_sessions:
        raise LearningRecordsError(f"{path}: unknown evidence session(s): {', '.join(missing_sessions)}")
    raw_supersedes = metadata["supersedes"]
    if not isinstance(raw_supersedes, list):
        raise LearningRecordsError(f"{path}: supersedes must be a list")
    supersedes = [_relative_path(root, item, path=path, field="supersedes") for item in raw_supersedes]
    if len(set(supersedes)) != len(supersedes):
        raise LearningRecordsError(f"{path}: supersedes must not contain duplicates")
    expected_parent = Path("learning-records") / track
    for previous in supersedes:
        if Path(previous).parent != expected_parent:
            raise LearningRecordsError(f"{path}: supersedes must stay within learning-records/{track}/")
        target_metadata = _load_frontmatter(root / previous)
        if "schema_version" not in target_metadata and not any(
            previous in graph_record_links[concept] for concept in concepts
        ):
            raise LearningRecordsError(
                f"{path}: legacy supersedes target must be linked by a declared concept: {previous}"
            )
    relative = path.relative_to(root.resolve()).as_posix()
    if relative in supersedes:
        raise LearningRecordsError(f"{path}: record cannot supersede itself")

    observations_by_concept = {
        concept: [
            {**evidence, "session_id": session_id, "started_at": events[session_id]["started_at_value"]}
            for session_id in sessions
            for evidence in events[session_id]["evidence"]
            if evidence["concept"] == concept
        ]
        for concept in concepts
    }
    if not any(observations_by_concept.values()):
        raise LearningRecordsError(f"{path}: evidence sessions contain no observations for its concepts")
    if any(not observations for observations in observations_by_concept.values()):
        raise LearningRecordsError(f"{path}: evidence sessions must observe every declared concept")
    for concept, observations in observations_by_concept.items():
        _validate_capability_evidence(
            path, capability_state, observations, demonstrated_at, concept=concept
        )
    return {
        "path": relative,
        "status": "structured",
        "track": track,
        "concepts": sorted(concepts),
        "capability_state": capability_state,
        "demonstrated_at": demonstrated_at,
        "assisted": False,
        "evidence_sessions": sorted(sessions),
        "supersedes": sorted(supersedes),
    }


def _validate_capability_evidence(
    path: Path,
    state: str,
    observations: list[dict[str, Any]],
    demonstrated_at: str,
    *,
    concept: str,
) -> None:
    unassisted_passes = [
        observation
        for observation in observations
        if observation["outcome"] == "pass" and not observation["assisted"]
    ]
    familiar_passes = [item for item in unassisted_passes if item["check"] in RECALL_OR_APPLICATION]
    usable_passes = [item for item in unassisted_passes if item["check"] in USABLE_CHECKS]
    if state == "encountered":
        if not unassisted_passes:
            raise LearningRecordsError(f"{path}: {concept} encountered requires an unassisted passing observation")
        relevant = unassisted_passes
    elif state == "familiar":
        if not familiar_passes:
            raise LearningRecordsError(f"{path}: {concept} familiar requires an unassisted recall, transfer, or real-work pass")
        relevant = familiar_passes
    elif state == "usable":
        if not usable_passes:
            raise LearningRecordsError(f"{path}: {concept} usable requires an unassisted transfer or real-work pass")
        relevant = usable_passes
    else:  # retained
        if len(unassisted_passes) < 2:
            raise LearningRecordsError(f"{path}: {concept} retained requires at least two unassisted passing observations")
        dates = sorted(item["started_at"].date() for item in unassisted_passes)
        if not any(later - earlier >= dt.timedelta(days=7) for index, earlier in enumerate(dates) for later in dates[index + 1:]):
            raise LearningRecordsError(f"{path}: {concept} retained requires unassisted passes separated by at least 7 days")
        latest_pass = max(unassisted_passes, key=lambda item: (item["started_at"], item["session_id"]))
        if latest_pass["check"] not in USABLE_CHECKS:
            raise LearningRecordsError(f"{path}: {concept} retained requires its latest unassisted pass to be transfer or real-work")
        relevant = unassisted_passes
    latest = max(relevant, key=lambda item: (item["started_at"], item["session_id"]))
    if demonstrated_at != latest["started_at"].date().isoformat():
        raise LearningRecordsError(
            f"{path}: demonstrated_at must equal {concept}'s latest relevant observation local date"
        )


def _load_records(root: Path, graph: dict[str, Any], events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    directory = root / "learning-records"
    if not directory.is_dir():
        raise LearningRecordsError(f"missing learning records directory: {directory}")
    tracks = set(graph["tracks"])
    for track in sorted(tracks):
        if not (directory / track).is_dir():
            raise LearningRecordsError(f"missing learning-records track directory: {directory / track}")
    known_concepts = {node["id"]: set(node["tracks"]) for node in graph["nodes"]}
    graph_record_links = {
        node["id"]: set(node.get("records", [])) for node in graph["nodes"]
    }
    by_event = {event["id"]: event for event in events}
    records: list[dict[str, Any]] = []
    for track_dir in sorted(path for path in directory.iterdir() if path.is_dir()):
        if track_dir.name not in tracks:
            raise LearningRecordsError(f"unknown learning-records track directory: {track_dir}")
        for path in sorted(track_dir.glob("*.md")):
            metadata = _load_frontmatter(path)
            relative = path.relative_to(root.resolve()).as_posix()
            if "schema_version" not in metadata:
                reasons = ["missing-schema-version"]
                if "Status" in metadata:
                    reasons.append("legacy-status-frontmatter")
                reasons.extend(
                    ["missing-structured-capability-review", "missing-evidence-session-links"]
                )
                records.append(
                    {
                        "path": relative,
                        "status": "legacy",
                        "track": track_dir.name,
                        "concepts": [],
                        "reasons": reasons,
                    }
                )
                continue
            records.append(
                _parse_structured_record(
                    root, path, metadata, known_concepts=known_concepts, tracks=tracks, events=by_event
                    , graph_record_links=graph_record_links
                )
            )
    return records


def _resolve_capabilities(
    records: list[dict[str, Any]], concept_ids: list[str]
) -> dict[str, dict[str, Any]]:
    structured = [record for record in records if record["status"] == "structured"]
    by_path = {record["path"]: record for record in structured}
    active_paths: set[str] = set()
    complete_paths: set[str] = set()

    def visit(record_path: str, trail: list[str]) -> None:
        if record_path in complete_paths:
            return
        if record_path in active_paths:
            cycle = trail[trail.index(record_path):]
            raise LearningRecordsError("structured record supersession cycle: " + " -> ".join(cycle))
        active_paths.add(record_path)
        for previous in by_path[record_path]["supersedes"]:
            if previous in by_path:
                visit(previous, trail + [previous])
        active_paths.remove(record_path)
        complete_paths.add(record_path)

    for record_path in sorted(by_path):
        visit(record_path, [record_path])
    for record in structured:
        for previous in record["supersedes"]:
            target = by_path.get(previous)
            if target is not None and not set(record["concepts"]) & set(target["concepts"]):
                raise LearningRecordsError(
                    f"{record['path']}: superseded structured record must share at least one concept: {previous}"
                )
    capabilities: dict[str, dict[str, Any]] = {}
    for concept in sorted(concept_ids):
        candidates = [record for record in structured if concept in record["concepts"]]
        superseded = {
            previous
            for record in candidates
            for previous in record["supersedes"]
            if previous in {candidate["path"] for candidate in candidates}
        }
        active = [record for record in candidates if record["path"] not in superseded]
        if len(active) > 1:
            raise LearningRecordsError(
                f"{concept}: multiple active structured learning records: "
                + ", ".join(record["path"] for record in active)
            )
        if not active:
            capabilities[concept] = {
                "state": "unassessed",
                "effective_record": None,
                "demonstrated_at": None,
                "evidence_sessions": [],
            }
            continue
        effective = active[0]
        capabilities[concept] = {
            "state": effective["capability_state"],
            "effective_record": effective["path"],
            "demonstrated_at": effective["demonstrated_at"],
            "evidence_sessions": effective["evidence_sessions"],
        }
    return capabilities


def build_projection(
    root: Path,
    *,
    graph: dict[str, Any] | None = None,
    events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return the deterministic learning-record capability projection for ``root``.

    Example: ``build_projection(Path("."))["capabilities"]["idempotency"]``.
    A graph producer may inject its already-built ``graph`` and parsed ``events``
    to avoid a recursive subprocess dependency.
    Legacy Markdown records remain in ``records`` and ``audit`` but never
    produce a capability state.
    """

    root = root.resolve()
    try:
        if graph is None:
            graph = learning_state.load_graph(root)
        if events is None:
            events = learning_state.load_events(root, graph)
    except learning_state.LearningStateError as error:
        raise LearningRecordsError(str(error)) from error
    records = _load_records(root, graph, events)
    capabilities = _resolve_capabilities(records, [node["id"] for node in graph["nodes"]])
    structured_supersession = {
        legacy_path: sorted(
            record["path"]
            for record in records
            if record["status"] == "structured" and legacy_path in record["supersedes"]
        )
        for legacy_path in (record["path"] for record in records if record["status"] == "legacy")
    }
    audit_legacy = [
        {
            "path": record["path"],
            "reasons": record["reasons"],
            "resolved_by": structured_supersession[record["path"]],
        }
        for record in records
        if record["status"] == "legacy"
    ]
    resolved_legacy_count = sum(bool(record["resolved_by"]) for record in audit_legacy)
    audit = {
        "schema_version": SCHEMA_VERSION,
        "legacy": audit_legacy,
        "legacy_count": len(audit_legacy),
        "pending_legacy_count": len(audit_legacy) - resolved_legacy_count,
        "resolved_legacy_count": resolved_legacy_count,
        "structured_count": len(records) - len(audit_legacy),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "capabilities": capabilities,
        "records": records,
        "audit": audit,
    }

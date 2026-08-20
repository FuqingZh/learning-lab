#!/usr/bin/env python3
"""Validate Learning Lab concepts and emit a stable normalized graph.

This command intentionally stops at the normalized-data boundary. Markdown and
browser projections are separate consumers of the data emitted by
``normalized-data``.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from yaml.constructor import ConstructorError
from yaml.resolver import BaseResolver


SCHEMA_VERSION = 1
KNOWN_KINDS = frozenset({"orientation", "foundation", "mechanism", "pattern", "boundary"})
REQUIRED_SCALARS = ("id", "title", "summary", "kind")
LIST_FIELDS = (
    "tracks",
    "case_labs",
    "prerequisites",
    "enables",
    "contrasts_with",
    "related",
    "lessons",
    "records",
)
RELATIONSHIP_FIELDS = ("prerequisites", "enables", "contrasts_with", "related")
STABLE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RECORD_STATE = re.compile(r"-(developing|mastered)\.md$")
OBSIDIAN_CONCEPT_LINK = re.compile(
    r"^\[\[concepts/([a-z0-9]+(?:-[a-z0-9]+)*)\]\]$"
)


class KnowledgeMapError(ValueError):
    """Raised when a source-of-truth knowledge-map contract is invalid."""


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


UniqueKeySafeLoader.add_constructor(
    BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


@dataclass(frozen=True)
class RecordCandidate:
    path: str
    state: str
    supersedes: tuple[str, ...]


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("validate", "normalized-data"),
        help="validate source data or print the normalized graph JSON",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Learning Lab repository root (default: current directory)",
    )
    return parser.parse_args(arguments)


def load_frontmatter(path: Path, *, required: bool) -> dict[str, Any]:
    """Read a shallow YAML frontmatter mapping from a Markdown file."""

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise KnowledgeMapError(f"cannot read {path}: {error}") from error

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        if required:
            raise KnowledgeMapError(f"{path}: missing YAML frontmatter")
        return {}

    closing_index = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if closing_index is None:
        raise KnowledgeMapError(f"{path}: unterminated YAML frontmatter")

    source = "".join(lines[1:closing_index])
    try:
        parsed = yaml.load(source, Loader=UniqueKeySafeLoader)
    except yaml.YAMLError as error:
        raise KnowledgeMapError(f"{path}: invalid YAML frontmatter: {error}") from error
    if parsed is None:
        parsed = {}
    if not isinstance(parsed, dict):
        raise KnowledgeMapError(f"{path}: YAML frontmatter must be a mapping")
    if not all(isinstance(key, str) for key in parsed):
        raise KnowledgeMapError(f"{path}: YAML frontmatter keys must be strings")
    return parsed


def require_nonempty_string(value: Any, *, field: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeMapError(f"{path}: {field} must be a non-empty string")
    return value.strip()


def require_stable_id(value: Any, *, field: str, path: Path) -> str:
    identifier = require_nonempty_string(value, field=field, path=path)
    if not STABLE_ID.fullmatch(identifier):
        raise KnowledgeMapError(
            f"{path}: {field} must use lowercase hyphenated stable-id syntax"
        )
    return identifier


def require_unique_strings(value: Any, *, field: str, path: Path, ids: bool) -> list[str]:
    if not isinstance(value, list):
        raise KnowledgeMapError(f"{path}: {field} must be a list")

    validated: list[str] = []
    for item in value:
        if ids:
            validated.append(require_stable_id(item, field=field, path=path))
        else:
            validated.append(require_nonempty_string(item, field=field, path=path))
    if len(set(validated)) != len(validated):
        raise KnowledgeMapError(f"{path}: {field} must not contain duplicates")
    return sorted(validated)


def require_unique_concept_links(value: Any, *, field: str, path: Path) -> list[str]:
    """Validate Obsidian-readable concept links and normalize them to stable IDs."""

    if not isinstance(value, list):
        raise KnowledgeMapError(f"{path}: {field} must be a list")
    identifiers: list[str] = []
    for item in value:
        link = require_nonempty_string(item, field=field, path=path)
        match = OBSIDIAN_CONCEPT_LINK.fullmatch(link)
        if match is None:
            raise KnowledgeMapError(
                f"{path}: {field} entries must use quoted [[concepts/<stable-id>]] links"
            )
        identifiers.append(match.group(1))
    if len(set(identifiers)) != len(identifiers):
        raise KnowledgeMapError(f"{path}: {field} must not contain duplicates")
    return sorted(identifiers)


def resolve_repository_path(root: Path, reference: str, *, source: Path, field: str) -> Path:
    candidate = Path(reference)
    if candidate.is_absolute():
        raise KnowledgeMapError(f"{source}: {field} must be a repository-relative path")
    resolved_root = root.resolve()
    resolved = (resolved_root / candidate).resolve()
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise KnowledgeMapError(f"{source}: {field} must not escape the repository")
    if resolved == resolved_root:
        raise KnowledgeMapError(f"{source}: {field} must name a file")
    return resolved


def read_record_candidate(root: Path, reference: str, *, source: Path) -> RecordCandidate:
    target = resolve_repository_path(root, reference, source=source, field="records")
    if not target.is_file():
        raise KnowledgeMapError(f"{source}: records target does not exist: {reference}")
    relative_target = target.relative_to(root.resolve())
    if len(relative_target.parts) < 3 or relative_target.parts[0] != "learning-records":
        raise KnowledgeMapError(
            f"{source}: records target must be under learning-records/<track>/: {reference}"
        )

    state_match = RECORD_STATE.search(target.name)
    if state_match is None:
        raise KnowledgeMapError(
            f"{source}: records target has no recognized state suffix: {reference}"
        )

    metadata = load_frontmatter(target, required=False)
    raw_supersedes = metadata.get("supersedes", [])
    if isinstance(raw_supersedes, str):
        raw_supersedes = [raw_supersedes]
    if not isinstance(raw_supersedes, list) or not all(
        isinstance(item, str) and item.strip() for item in raw_supersedes
    ):
        raise KnowledgeMapError(f"{target}: supersedes must be a path or list of paths")

    supersedes = tuple(sorted(item.strip() for item in raw_supersedes))
    if len(set(supersedes)) != len(supersedes):
        raise KnowledgeMapError(f"{target}: supersedes must not contain duplicates")
    return RecordCandidate(
        path=reference,
        state=state_match.group(1),
        supersedes=supersedes,
    )


def resolve_mastery(root: Path, record_paths: list[str], *, source: Path) -> dict[str, str | None]:
    """Derive one status without guessing across ambiguous record histories."""

    if not record_paths:
        return {"status": "not-started", "effective_record": None}

    candidates = [read_record_candidate(root, path, source=source) for path in record_paths]
    candidate_paths = {candidate.path for candidate in candidates}
    superseded: set[str] = set()
    has_machine_supersession = False
    for candidate in candidates:
        for previous in candidate.supersedes:
            has_machine_supersession = True
            if previous not in candidate_paths:
                raise KnowledgeMapError(
                    f"{source}: {candidate.path} supersedes an unlinked record: {previous}"
                )
            if previous == candidate.path:
                raise KnowledgeMapError(f"{source}: record cannot supersede itself: {previous}")
            superseded.add(previous)

    supersession_edges = {
        candidate.path: candidate.supersedes for candidate in candidates
    }
    active: set[str] = set()
    complete: set[str] = set()

    def visit(record_path: str, trail: list[str]) -> None:
        if record_path in complete:
            return
        if record_path in active:
            start = trail.index(record_path)
            cycle = trail[start:]
            raise KnowledgeMapError(
                f"{source}: record supersession cycle: " + " -> ".join(cycle)
            )
        active.add(record_path)
        for previous in supersession_edges[record_path]:
            visit(previous, trail + [previous])
        active.remove(record_path)
        complete.add(record_path)

    for record_path in sorted(supersession_edges):
        visit(record_path, [record_path])

    if has_machine_supersession:
        effective = [candidate for candidate in candidates if candidate.path not in superseded]
        if len(effective) != 1:
            raise KnowledgeMapError(
                f"{source}: record supersession must leave exactly one effective record"
            )
        chosen = effective[0]
    elif len(candidates) == 1:
        chosen = candidates[0]
    else:
        raise KnowledgeMapError(
            f"{source}: multiple records are ambiguous; add machine-readable supersedes metadata"
        )

    return {"status": chosen.state, "effective_record": chosen.path}


def normalize_extension_value(value: Any, *, field: str, path: Path) -> Any:
    """Accept only values with one stable, lossless normalized JSON form."""

    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise KnowledgeMapError(f"{path}: extension {field} must use a finite number")
        return value
    if isinstance(value, list):
        return [
            normalize_extension_value(item, field=field, path=path) for item in value
        ]
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise KnowledgeMapError(
                f"{path}: extension {field} mapping keys must be strings"
            )
        return {
            key: normalize_extension_value(value[key], field=field, path=path)
            for key in sorted(value)
        }
    raise KnowledgeMapError(
        f"{path}: extension {field} must be deterministic JSON-compatible data"
    )


def normalize_extensions(raw: dict[str, Any], *, path: Path) -> dict[str, Any]:
    """Keep deterministic unknown YAML keys available without interpreting them."""

    standard_fields = set(REQUIRED_SCALARS) | set(LIST_FIELDS)
    return {
        key: normalize_extension_value(raw[key], field=key, path=path)
        for key in sorted(raw)
        if key not in standard_fields
    }


def parse_concept(root: Path, path: Path) -> dict[str, Any]:
    raw = load_frontmatter(path, required=True)
    for field in REQUIRED_SCALARS + LIST_FIELDS:
        if field not in raw:
            raise KnowledgeMapError(f"{path}: missing required field: {field}")

    identifier = require_stable_id(raw["id"], field="id", path=path)

    kind = require_nonempty_string(raw["kind"], field="kind", path=path)
    if kind not in KNOWN_KINDS:
        raise KnowledgeMapError(
            f"{path}: kind must be one of {', '.join(sorted(KNOWN_KINDS))}"
        )

    node = {
        "id": identifier,
        "title": require_nonempty_string(raw["title"], field="title", path=path),
        "summary": require_nonempty_string(raw["summary"], field="summary", path=path),
        "kind": kind,
        "tracks": require_unique_strings(raw["tracks"], field="tracks", path=path, ids=True),
        "case_labs": require_unique_strings(raw["case_labs"], field="case_labs", path=path, ids=True),
        "relationships": {
            field: require_unique_concept_links(raw[field], field=field, path=path)
            for field in RELATIONSHIP_FIELDS
        },
        "lessons": require_unique_strings(raw["lessons"], field="lessons", path=path, ids=False),
        "records": require_unique_strings(raw["records"], field="records", path=path, ids=False),
        "path": path.relative_to(root).as_posix(),
        "extensions": normalize_extensions(raw, path=path),
    }
    node["mastery"] = resolve_mastery(root, node["records"], source=path)
    return node


def validate_references(root: Path, concepts: list[dict[str, Any]], case_labs: set[str]) -> None:
    known_ids = {concept["id"] for concept in concepts}
    for concept in concepts:
        source = root / concept["path"]
        for track in concept["tracks"]:
            if not (root / "tracks" / track).is_dir():
                raise KnowledgeMapError(f"{source}: unknown track: {track}")
        for case_lab in concept["case_labs"]:
            if case_lab not in case_labs:
                raise KnowledgeMapError(f"{source}: unknown case lab: {case_lab}")
        for field, targets in concept["relationships"].items():
            for target in targets:
                if target not in known_ids:
                    raise KnowledgeMapError(f"{source}: dangling {field} target: {target}")
                if target == concept["id"]:
                    raise KnowledgeMapError(f"{source}: {field} must not reference itself")
        for lesson in concept["lessons"]:
            target = resolve_repository_path(root, lesson, source=source, field="lessons")
            if not target.is_file():
                raise KnowledgeMapError(f"{source}: lessons target does not exist: {lesson}")


def validate_relationship_redundancy(concepts: list[dict[str, Any]]) -> None:
    """Keep one authoritative edge when another declaration already implies it."""

    by_id = {concept["id"]: concept for concept in concepts}
    for concept in concepts:
        source = concept["id"]
        for relationship_type in ("contrasts_with", "related"):
            for target in concept["relationships"][relationship_type]:
                reverse = by_id[target]["relationships"][relationship_type]
                if source in reverse:
                    pair = " <-> ".join(sorted((source, target)))
                    raise KnowledgeMapError(
                        f"duplicate mirrored {relationship_type} relationship: {pair}"
                    )
        for target in concept["relationships"]["related"]:
            other_relationships = ("prerequisites", "enables", "contrasts_with")
            if any(
                target in concept["relationships"][relationship_type]
                or source in by_id[target]["relationships"][relationship_type]
                for relationship_type in other_relationships
            ):
                pair = " <-> ".join(sorted((source, target)))
                raise KnowledgeMapError(
                    f"related must not duplicate a typed relationship: {pair}"
                )
        for target in concept["relationships"]["enables"]:
            if source in by_id[target]["relationships"]["prerequisites"]:
                raise KnowledgeMapError(
                    "redundant inverse relationship: "
                    f"{source} enables {target}, which already lists {source} as a prerequisite"
                )


def validate_prerequisite_acyclic(concepts: list[dict[str, Any]]) -> None:
    relationships = {
        concept["id"]: concept["relationships"]["prerequisites"] for concept in concepts
    }
    active: set[str] = set()
    completed: set[str] = set()

    def visit(identifier: str, trail: list[str]) -> None:
        if identifier in completed:
            return
        if identifier in active:
            cycle_start = trail.index(identifier)
            cycle = trail[cycle_start:]
            raise KnowledgeMapError("prerequisite cycle: " + " -> ".join(cycle))
        active.add(identifier)
        for prerequisite in relationships[identifier]:
            visit(prerequisite, trail + [prerequisite])
        active.remove(identifier)
        completed.add(identifier)

    for identifier in sorted(relationships):
        visit(identifier, [identifier])


def scan_case_labs(root: Path) -> list[dict[str, Any]]:
    directory = root / "case-labs"
    if not directory.is_dir():
        raise KnowledgeMapError(f"missing case-labs directory: {directory}")
    hubs: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.md")):
        identifier = path.stem
        if not STABLE_ID.fullmatch(identifier):
            raise KnowledgeMapError(f"{path}: case-lab basename must be a stable id")
        metadata = load_frontmatter(path, required=True)
        declared_id = require_stable_id(metadata.get("id"), field="id", path=path)
        if declared_id != identifier:
            raise KnowledgeMapError(f"{path}: basename must equal id {declared_id!r}")
        hubs.append(
            {
                "id": identifier,
                "title": require_nonempty_string(
                    metadata.get("title"), field="title", path=path
                ),
                "path": path.relative_to(root).as_posix(),
                "direct_concepts": [],
            }
        )
    return hubs


def load_knowledge_graph(root: Path) -> dict[str, Any]:
    """Read, validate, and normalize all knowledge-map source files."""

    root = root.resolve()
    concept_directory = root / "concepts"
    if not concept_directory.is_dir():
        raise KnowledgeMapError(f"missing concepts directory: {concept_directory}")
    if not (root / "tracks").is_dir():
        raise KnowledgeMapError(f"missing tracks directory: {root / 'tracks'}")

    concepts = [parse_concept(root, path) for path in sorted(concept_directory.glob("*.md"))]
    identifiers = [concept["id"] for concept in concepts]
    duplicates = sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1})
    if duplicates:
        raise KnowledgeMapError("duplicate concept ids: " + ", ".join(duplicates))
    for concept in concepts:
        source = root / concept["path"]
        if source.stem != concept["id"]:
            raise KnowledgeMapError(
                f"{source}: basename must equal id {concept['id']!r}"
            )

    hubs = scan_case_labs(root)
    case_lab_ids = {hub["id"] for hub in hubs}
    validate_references(root, concepts, case_lab_ids)
    validate_prerequisite_acyclic(concepts)
    validate_relationship_redundancy(concepts)

    for hub in hubs:
        hub["direct_concepts"] = sorted(
            concept["id"]
            for concept in concepts
            if hub["id"] in concept["case_labs"]
        )

    edges = [
        {"source": concept["id"], "target": target, "type": relationship_type}
        for concept in concepts
        for relationship_type, targets in concept["relationships"].items()
        for target in targets
    ]
    edges.sort(key=lambda edge: (edge["source"], edge["type"], edge["target"]))
    tracks = sorted(path.name for path in (root / "tracks").iterdir() if path.is_dir())
    return {
        "schema_version": SCHEMA_VERSION,
        "tracks": tracks,
        "case_labs": hubs,
        "nodes": sorted(concepts, key=lambda concept: concept["id"]),
        "edges": edges,
    }


def validate_knowledge_graph(root: Path) -> dict[str, Any]:
    """Validate source files and return their normalized graph for callers."""

    return load_knowledge_graph(root)


def main(arguments: list[str] | None = None) -> int:
    parsed = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    try:
        graph = validate_knowledge_graph(parsed.root)
    except KnowledgeMapError as error:
        print(f"knowledge map validation failed: {error}", file=sys.stderr)
        return 1

    if parsed.command == "validate":
        print(
            "knowledge map: valid "
            f"({len(graph['nodes'])} concepts, {len(graph['case_labs'])} case labs)"
        )
    else:
        print(json.dumps(graph, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

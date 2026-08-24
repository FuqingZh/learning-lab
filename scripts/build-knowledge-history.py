#!/usr/bin/env python3
"""Validate evidence-backed history dossiers and emit normalized history v1."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from yaml.constructor import ConstructorError
from yaml.resolver import BaseResolver


SCHEMA_VERSION = 1
STABLE_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DOSSIER_FIELDS = frozenset(
    {"schema_version", "id", "title", "summary", "concepts", "lessons", "tracks", "milestones"}
)
MILESTONE_FIELDS = frozenset(
    {"id", "year", "month", "day", "kind", "actors", "claim", "evidence_basis", "sources"}
)
SOURCE_FIELDS = frozenset({"url", "title", "publisher", "role", "kind"})
MILESTONE_KINDS = frozenset(
    {"terminology", "problem", "formalization", "adoption", "popularization", "revision", "critique"}
)
SOURCE_ROLES = frozenset({"primary", "scholarly-secondary"})
SOURCE_KINDS = frozenset({"monograph", "paper", "standard", "archive", "professional-documentation"})
EVIDENCE_BASES = frozenset({"primary-source", "scholarly-secondary", "mixed"})
REQUIRED_HEADINGS = (
    "Historical setting",
    "What the sources establish",
    "What the sources do not establish",
    "Development",
    "Modern boundary",
)


class KnowledgeHistoryError(ValueError):
    """Raised when an evidence-backed history source contract is invalid."""


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
    parser.add_argument("command", choices=("validate", "normalized-data"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser.parse_args(arguments)


def require_string(value: Any, *, field: str, path: Path) -> str:
    if not isinstance(value, str) or not value.strip():
        raise KnowledgeHistoryError(f"{path}: {field} must be a non-empty string")
    return value.strip()


def require_stable_id(value: Any, *, field: str, path: Path) -> str:
    identifier = require_string(value, field=field, path=path)
    if not STABLE_ID.fullmatch(identifier):
        raise KnowledgeHistoryError(f"{path}: {field} must use lowercase hyphenated stable-id syntax")
    return identifier


def require_exact_fields(value: Any, *, fields: frozenset[str], label: str, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise KnowledgeHistoryError(f"{path}: {label} must be a mapping with string keys")
    missing = sorted(fields - set(value))
    unknown = sorted(set(value) - fields)
    if missing:
        raise KnowledgeHistoryError(f"{path}: {label} missing required fields: {', '.join(missing)}")
    if unknown:
        raise KnowledgeHistoryError(f"{path}: {label} has unknown fields: {', '.join(unknown)}")
    return value


def split_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    except OSError as error:
        raise KnowledgeHistoryError(f"cannot read {path}: {error}") from error
    if not lines or lines[0].strip() != "---":
        raise KnowledgeHistoryError(f"{path}: missing YAML frontmatter")
    closing = next((index for index, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if closing is None:
        raise KnowledgeHistoryError(f"{path}: unterminated YAML frontmatter")
    try:
        metadata = yaml.load("".join(lines[1:closing]), Loader=UniqueKeySafeLoader)
    except yaml.YAMLError as error:
        raise KnowledgeHistoryError(f"{path}: invalid YAML frontmatter: {error}") from error
    if not isinstance(metadata, dict):
        raise KnowledgeHistoryError(f"{path}: YAML frontmatter must be a mapping")
    return metadata, "".join(lines[closing + 1:])


def require_unique_strings(value: Any, *, field: str, path: Path, stable_ids: bool) -> list[str]:
    if not isinstance(value, list):
        raise KnowledgeHistoryError(f"{path}: {field} must be a list")
    values = [
        require_stable_id(item, field=field, path=path) if stable_ids else require_string(item, field=field, path=path)
        for item in value
    ]
    if len(set(values)) != len(values):
        raise KnowledgeHistoryError(f"{path}: {field} must not contain duplicates")
    return sorted(values)


def resolve_reference(root: Path, reference: str, *, source: Path, field: str, prefix: str) -> Path:
    candidate = Path(reference)
    if candidate.is_absolute():
        raise KnowledgeHistoryError(f"{source}: {field} must be a repository-relative path")
    resolved_root = root.resolve()
    target = (resolved_root / candidate).resolve()
    if target == resolved_root or resolved_root not in target.parents:
        raise KnowledgeHistoryError(f"{source}: {field} must not escape the repository")
    relative = target.relative_to(resolved_root)
    if not relative.parts or relative.parts[0] != prefix:
        raise KnowledgeHistoryError(f"{source}: {field} must be under {prefix}/")
    return target


def read_concept_ids(root: Path) -> set[str]:
    directory = root / "concepts"
    if not directory.is_dir():
        raise KnowledgeHistoryError(f"missing concepts directory: {directory}")
    identifiers: set[str] = set()
    for path in sorted(directory.glob("*.md")):
        require_repository_source(root, path, label="concept source")
        metadata, _ = split_frontmatter(path)
        identifier = require_stable_id(metadata.get("id"), field="concept id", path=path)
        if path.stem != identifier:
            raise KnowledgeHistoryError(f"{path}: basename must equal concept id {identifier!r}")
        if identifier in identifiers:
            raise KnowledgeHistoryError(f"duplicate concept ids: {identifier}")
        identifiers.add(identifier)
    return identifiers


def require_repository_source(root: Path, path: Path, *, label: str) -> None:
    """Reject source indirection so projected paths name real repository files."""
    if path.is_symlink():
        raise KnowledgeHistoryError(f"{path}: {label} must not be a symbolic link")
    resolved_root = root.resolve()
    resolved = path.resolve()
    if resolved_root not in resolved.parents or not resolved.is_file():
        raise KnowledgeHistoryError(f"{path}: {label} must be a regular file inside the repository")


def validate_headings(body: str, *, path: Path) -> None:
    headings = {match.group(1).strip() for match in re.finditer(r"(?m)^##[ \t]+(.+?)[ \t]*$", body)}
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in headings]
    if missing:
        raise KnowledgeHistoryError(f"{path}: missing required Markdown headings: {', '.join(missing)}")


def require_calendar_component(value: Any, *, field: str, path: Path, lower: int, upper: int) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
        raise KnowledgeHistoryError(f"{path}: {field} must be an integer from {lower} to {upper}, or null")
    return value


def parse_source(value: Any, *, path: Path, label: str) -> dict[str, str]:
    source = require_exact_fields(value, fields=SOURCE_FIELDS, label=label, path=path)
    url = require_string(source["url"], field=f"{label}.url", path=path)
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise KnowledgeHistoryError(f"{path}: {label}.url must be an HTTPS URL")
    role = require_string(source["role"], field=f"{label}.role", path=path)
    if role not in SOURCE_ROLES:
        raise KnowledgeHistoryError(f"{path}: {label}.role must be one of {', '.join(sorted(SOURCE_ROLES))}")
    kind = require_string(source["kind"], field=f"{label}.kind", path=path)
    if kind not in SOURCE_KINDS:
        raise KnowledgeHistoryError(f"{path}: {label}.kind must be one of {', '.join(sorted(SOURCE_KINDS))}")
    return {
        "url": url,
        "title": require_string(source["title"], field=f"{label}.title", path=path),
        "publisher": require_string(source["publisher"], field=f"{label}.publisher", path=path),
        "role": role,
        "kind": kind,
    }


def parse_milestone(value: Any, *, path: Path, index: int) -> dict[str, Any]:
    label = f"milestones[{index}]"
    milestone = require_exact_fields(value, fields=MILESTONE_FIELDS, label=label, path=path)
    identifier = require_stable_id(milestone["id"], field=f"{label}.id", path=path)
    year = require_calendar_component(milestone["year"], field=f"{label}.year", path=path, lower=1, upper=9999)
    if year is None:
        raise KnowledgeHistoryError(f"{path}: {label}.year is required")
    month = require_calendar_component(milestone["month"], field=f"{label}.month", path=path, lower=1, upper=12)
    day = require_calendar_component(milestone["day"], field=f"{label}.day", path=path, lower=1, upper=31)
    if day is not None and month is None:
        raise KnowledgeHistoryError(f"{path}: {label}.day requires month")
    if day is not None:
        try:
            dt.date(year, month, day)
        except ValueError as error:
            raise KnowledgeHistoryError(f"{path}: {label} has invalid calendar components") from error
    kind = require_string(milestone["kind"], field=f"{label}.kind", path=path)
    if kind not in MILESTONE_KINDS:
        raise KnowledgeHistoryError(f"{path}: {label}.kind must be one of {', '.join(sorted(MILESTONE_KINDS))}")
    evidence_basis = require_string(milestone["evidence_basis"], field=f"{label}.evidence_basis", path=path)
    if evidence_basis not in EVIDENCE_BASES:
        raise KnowledgeHistoryError(f"{path}: {label}.evidence_basis must be one of {', '.join(sorted(EVIDENCE_BASES))}")
    actors = require_unique_strings(milestone["actors"], field=f"{label}.actors", path=path, stable_ids=False)
    if not actors:
        raise KnowledgeHistoryError(f"{path}: {label}.actors must not be empty")
    sources_value = milestone["sources"]
    if not isinstance(sources_value, list) or not sources_value:
        raise KnowledgeHistoryError(f"{path}: {label}.sources must be a non-empty list")
    sources = [parse_source(source, path=path, label=f"{label}.sources[{source_index}]") for source_index, source in enumerate(sources_value)]
    urls = [source["url"] for source in sources]
    if len(set(urls)) != len(urls):
        raise KnowledgeHistoryError(f"{path}: {label}.sources URLs must be unique")
    roles = {source["role"] for source in sources}
    if evidence_basis == "primary-source" and "primary" not in roles:
        raise KnowledgeHistoryError(f"{path}: {label}.evidence_basis primary-source requires a primary source")
    if evidence_basis == "scholarly-secondary" and "scholarly-secondary" not in roles:
        raise KnowledgeHistoryError(f"{path}: {label}.evidence_basis scholarly-secondary requires a scholarly secondary source")
    if evidence_basis == "mixed" and roles != SOURCE_ROLES:
        raise KnowledgeHistoryError(f"{path}: {label}.evidence_basis mixed requires primary and scholarly secondary sources")
    return {
        "id": identifier,
        "year": year,
        "month": month,
        "day": day,
        "kind": kind,
        "actors": actors,
        "claim": require_string(milestone["claim"], field=f"{label}.claim", path=path),
        "evidence_basis": evidence_basis,
        "sources": sorted(sources, key=lambda source: (source["url"], source["title"], source["publisher"])),
    }


def parse_dossier(root: Path, path: Path, *, concept_ids: set[str], track_ids: set[str]) -> dict[str, Any]:
    raw, body = split_frontmatter(path)
    dossier = require_exact_fields(raw, fields=DOSSIER_FIELDS, label="dossier", path=path)
    schema_version = dossier["schema_version"]
    if isinstance(schema_version, bool) or not isinstance(schema_version, int) or schema_version != SCHEMA_VERSION:
        raise KnowledgeHistoryError(f"{path}: schema_version must be {SCHEMA_VERSION}")
    identifier = require_stable_id(dossier["id"], field="id", path=path)
    if path.name != f"{identifier}.md":
        raise KnowledgeHistoryError(f"{path}: filename must equal dossier id plus .md")
    concepts = require_unique_strings(dossier["concepts"], field="concepts", path=path, stable_ids=True)
    lessons = require_unique_strings(dossier["lessons"], field="lessons", path=path, stable_ids=False)
    tracks = require_unique_strings(dossier["tracks"], field="tracks", path=path, stable_ids=True)
    if not concepts and not lessons:
        raise KnowledgeHistoryError(f"{path}: dossier must link at least one concept or lesson")
    for concept in concepts:
        if concept not in concept_ids:
            raise KnowledgeHistoryError(f"{path}: unknown concept: {concept}")
    for lesson in lessons:
        target = resolve_reference(root, lesson, source=path, field="lessons", prefix="lessons")
        if not target.is_file() or target.suffix != ".md":
            raise KnowledgeHistoryError(f"{path}: lessons target does not exist: {lesson}")
    for track in tracks:
        if track not in track_ids:
            raise KnowledgeHistoryError(f"{path}: unknown track: {track}")
    milestones_value = dossier["milestones"]
    if not isinstance(milestones_value, list) or not milestones_value:
        raise KnowledgeHistoryError(f"{path}: milestones must be a non-empty list")
    milestones = [parse_milestone(item, path=path, index=index) for index, item in enumerate(milestones_value)]
    milestone_ids = [milestone["id"] for milestone in milestones]
    if len(set(milestone_ids)) != len(milestone_ids):
        raise KnowledgeHistoryError(f"{path}: milestone ids must be unique")
    source_urls = [source["url"] for milestone in milestones for source in milestone["sources"]]
    if len(set(source_urls)) != len(source_urls):
        raise KnowledgeHistoryError(f"{path}: source URLs must be unique within a dossier")
    validate_headings(body, path=path)
    return {
        "id": identifier,
        "title": require_string(dossier["title"], field="title", path=path),
        "summary": require_string(dossier["summary"], field="summary", path=path),
        "path": path.relative_to(root).as_posix(),
        "concepts": concepts,
        "lessons": lessons,
        "tracks": tracks,
        "milestones": sorted(milestones, key=lambda item: (item["year"], item["month"] or 0, item["day"] or 0, item["id"])),
    }


def load_history(root: Path) -> dict[str, Any]:
    root = root.resolve()
    directory = root / "histories"
    if not directory.is_dir():
        raise KnowledgeHistoryError(f"missing histories directory: {directory}")
    if directory.is_symlink() or directory.resolve() != directory:
        raise KnowledgeHistoryError(f"{directory}: histories directory must not be a symbolic link")
    concept_ids = read_concept_ids(root)
    tracks_directory = root / "tracks"
    if not tracks_directory.is_dir():
        raise KnowledgeHistoryError(f"missing tracks directory: {tracks_directory}")
    track_ids = {path.name for path in tracks_directory.iterdir() if path.is_dir()}
    dossiers = []
    for path in sorted(directory.glob("*.md")):
        if path.name == "README.md":
            continue
        require_repository_source(root, path, label="history dossier")
        dossiers.append(parse_dossier(root, path, concept_ids=concept_ids, track_ids=track_ids))
    identifiers = [dossier["id"] for dossier in dossiers]
    if len(set(identifiers)) != len(identifiers):
        duplicates = sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1})
        raise KnowledgeHistoryError("duplicate dossier ids: " + ", ".join(duplicates))
    return {"schema_version": SCHEMA_VERSION, "dossiers": sorted(dossiers, key=lambda dossier: dossier["id"])}


def main(arguments: list[str] | None = None) -> int:
    parsed = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    try:
        history = load_history(parsed.root)
    except KnowledgeHistoryError as error:
        print(f"knowledge history validation failed: {error}", file=sys.stderr)
        return 1
    if parsed.command == "validate":
        print(f"knowledge history: valid ({len(history['dossiers'])} dossiers)")
    else:
        print(json.dumps(history, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

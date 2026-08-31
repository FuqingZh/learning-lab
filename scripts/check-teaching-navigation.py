#!/usr/bin/env python3
"""Read-only validation and resume resolution for small discussion snapshots.

This does not collect transcripts, schedule lessons, or infer learning mastery.
Missing navigation may use the existing session producer; invalid data fails.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class NavigationError(ValueError):
    """A snapshot is unsafe to use as a discussion return point."""


class SnapshotLoader(yaml.SafeLoader):
    """Reject ambiguous duplicate declarations instead of taking the last one."""

    def construct_mapping(self, node, deep=False):
        result = super().construct_mapping(node, deep=deep)
        if len(result) != len(node.value):
            raise NavigationError("duplicate navigation mapping key")
        return result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise NavigationError(message)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def fields(value: Any, names: str, label: str) -> None:
    require(isinstance(value, dict) and set(value) == set(names.split()),
            f"{label}: unexpected or missing fields")


def strings(value: Any, label: str) -> None:
    require(isinstance(value, list) and all(nonempty(item) for item in value),
            f"{label}: expected list of nonempty strings")


def track_path(root: Path, track: Any) -> Path:
    require(isinstance(track, str) and IDENTIFIER.fullmatch(track) is not None,
            "invalid track identifier")
    path = (root / "tracks" / track).resolve()
    require(path.is_dir() and root in path.parents and (root / "tracks").resolve() in path.parents,
            "unknown or escaped track")
    return root / "learning-state" / "navigation" / f"{track}.yaml"


def lesson_path(root: Path, reference: Any) -> None:
    require(nonempty(reference), "lesson reference is empty")
    relative = Path(reference)
    path = (root / relative).resolve()
    require(not relative.is_absolute() and relative.as_posix() == reference
            and bool(relative.parts) and ".." not in relative.parts and relative.parts[0] == "lessons"
            and root in path.parents and path.is_file()
            and path.suffix == ".md" and (root / "lessons").resolve() in path.parents,
            "lesson reference must be an existing in-repository lesson")


def validate(data: Any, root: Path) -> dict[str, Any]:
    """Validate structural declarations, not transcript truth or comprehension."""
    fields(data, "schema_version track updated_at source main active_branch branches", "snapshot")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1,
            "unsupported navigation schema")
    track_path(root, data["track"])
    require(nonempty(data["updated_at"]), "updated_at must be a quoted timestamp")
    try:
        stamp = datetime.fromisoformat(data["updated_at"])
    except ValueError as error:
        raise NavigationError("invalid updated_at timestamp") from error
    require(stamp.tzinfo is not None, "updated_at requires timezone")
    source = data["source"]
    fields(source, "enabled locator coverage verified_range gaps", "source")
    require(source["enabled"] is True, "snapshot requires explicit source opt-in")
    require(source["locator"] is None or nonempty(source["locator"]), "invalid source locator")
    strings(source["gaps"], "source gaps")
    coverage = source["coverage"]
    require(coverage in ("missing", "partial", "complete"), "invalid coverage")
    if coverage == "missing":
        require(source["verified_range"] is None and bool(source["gaps"]),
                "missing source needs gaps and no verified range")
    else:
        require(nonempty(source["locator"]) and nonempty(source["verified_range"]),
                "available source needs locator and verified range")
        require(bool(source["gaps"]) == (coverage == "partial"),
                "partial source needs gaps; complete source cannot have gaps")
    main = data["main"]
    fields(main, "unit_ref checkpoint", "main")
    lesson_path(root, main["unit_ref"])
    require(nonempty(main["checkpoint"]), "main checkpoint is empty")
    require(isinstance(data["branches"], list), "branches must be a list")
    nodes: dict[str, dict[str, Any]] = {}
    for node in data["branches"]:
        fields(node, "id parent unit_ref question purpose status return_to conclusion unresolved", "branch")
        identifier = node["id"]
        require(isinstance(identifier, str) and IDENTIFIER.fullmatch(identifier) is not None
                and identifier != "main" and identifier not in nodes,
                "invalid, duplicate or reserved branch id")
        require(node["parent"] is None or nonempty(node["parent"]), "invalid parent")
        lesson_path(root, node["unit_ref"])
        require(nonempty(node["question"]) and nonempty(node["purpose"]), "empty branch purpose/question")
        require(node["status"] in ("open", "parked", "resolved"), "invalid branch status")
        fields(node["return_to"], "node checkpoint", "return_to")
        require(node["return_to"]["node"] == (node["parent"] or "main")
                and nonempty(node["return_to"]["checkpoint"]), "return point does not match parent")
        strings(node["unresolved"], "unresolved")
        require(node["conclusion"] is None or nonempty(node["conclusion"]), "invalid conclusion")
        if node["status"] == "resolved":
            require(nonempty(node["conclusion"]) and not node["unresolved"],
                    "resolved branch needs conclusion and no unresolved questions")
        if node["status"] == "parked":
            require(bool(node["unresolved"]), "parked branch needs unresolved reason")
        nodes[identifier] = node
    for node in nodes.values():
        parent = node["parent"]
        require(parent is None or parent in nodes, "orphan branch")
        if parent is not None:
            require(node["unit_ref"] == nodes[parent]["unit_ref"], "parent/child lesson mismatch")
            require(nodes[parent]["status"] != "resolved" or node["status"] == "resolved",
                    "unresolved child of resolved parent")
        visited: set[str] = set()
        current: str | None = node["id"]
        while current is not None:
            require(current not in visited, "branch cycle")
            require(current in nodes, "orphan branch")
            visited.add(current)
            current = nodes[current]["parent"]
    active = data["active_branch"]
    require(active is None or (isinstance(active, str) and active in nodes), "unknown active branch")
    chain: set[str] = set()
    while active is not None:
        node = nodes[active]
        require(node["status"] == "open" and node["unit_ref"] == main["unit_ref"],
                "active branch chain must be open in the current lesson")
        chain.add(active)
        active = node["parent"]
    require(chain == {key for key, node in nodes.items() if node["status"] == "open"},
            "open branches must form the active ancestor chain")
    return data


def load(path: Path, root: Path) -> dict[str, Any]:
    require(root in path.resolve().parents, "navigation file escapes repository")
    try:
        data = yaml.load(path.read_text(encoding="utf-8"), Loader=SnapshotLoader)
    except (OSError, yaml.YAMLError) as error:
        raise NavigationError(f"cannot read navigation: {error}") from error
    data = validate(data, root)
    require(path.name == f"{data['track']}.yaml", "snapshot filename/track mismatch")
    return data


def resolve(root: Path, track: str) -> dict[str, Any]:
    """Return a position without reading raw conversations or modifying state."""
    path = track_path(root, track)
    if not path.exists() and not path.is_symlink():
        result = subprocess.run(
            [sys.executable, str(root / "scripts" / "build-learning-state.py"),
             "normalized-data", "--root", str(root)],
            capture_output=True, text=True, check=False,
        )
        require(result.returncode == 0, "legacy state read failed: " + result.stderr.strip())
        legacy = json.loads(result.stdout)
        # The existing producer is authoritative for its own resume projection.
        resume = legacy.get("resume")
        if resume is not None and resume.get("track") != track:
            resume = None
        return {"source": "legacy-resume" if resume else "none", "track": track,
                "resume": resume}
    data = load(path, root)
    nodes = {node["id"]: node for node in data["branches"]}
    current = data["active_branch"]
    chain = []
    while current is not None:
        chain.append(current)
        current = nodes[current]["parent"]
    chain.reverse()
    active = nodes.get(data["active_branch"])
    return {"source": "navigation", "track": track, "main": data["main"],
            "active_branch": active, "breadcrumb": chain,
            "capture": data["source"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "resolve"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--track")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == "resolve" and not args.track:
        parser.error("resolve requires --track")
    try:
        if args.command == "resolve":
            print(json.dumps(resolve(root, args.track), ensure_ascii=False, sort_keys=True))
        else:
            paths = ([track_path(root, args.track)] if args.track else
                     sorted((root / "learning-state" / "navigation").glob("*.yaml")))
            for path in paths:
                load(path, root)
            print(f"teaching navigation: valid ({len(paths)} snapshots; coverage declarations only)")
    except (NavigationError, OSError, ValueError) as error:
        print(f"teaching navigation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

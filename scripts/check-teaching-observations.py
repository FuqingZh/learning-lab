#!/usr/bin/env python3
"""Check bounded classroom observation records; never run or grade a model."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def strings(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and bool(item.strip()) for item in value)


def validate(root: Path) -> tuple[int, int]:
    """Check case alignment and evidence declarations without assessing truth.

    Examples:
        ``validate(root)`` returns the case and observation-file counts. A
        record calling itself a strict scorecard or lacking a criterion result
        raises ValueError; missing runtime identity is allowed with limitations.

    Notes:
        This tier cannot produce aggregate pass or promote capability. Actual
        teaching and source review remain human/teacher responsibilities.
    """
    directory = root / "docs/evaluations"
    protocol = yaml.safe_load((directory / "continuity-observation-cases.yaml").read_text())
    require(protocol["schema_version"] == 1, "unsupported protocol")
    cases = {}
    for case in protocol["cases"]:
        require(case["id"] not in cases, "duplicate case")
        require(isinstance(case["context"], str) and bool(case["context"].strip()), "missing context")
        require(strings(case["turns"]) and len(case["turns"]) >= 2, "case must be multi-turn")
        require(strings(case["criteria"]), "missing observable criteria")
        cases[case["id"]] = case
    require(bool(cases), "missing cases")
    paths = sorted(directory.glob("*-classroom-observation.yaml"))
    for path in paths:
        data = yaml.safe_load(path.read_text())
        require(set(data) == {"schema_version", "kind", "date", "source", "runtime",
                              "materials", "reviewer", "observations", "limitations"},
                "unexpected observation fields; strict scores belong to the strict contract")
        require(type(data["schema_version"]) is int and data["schema_version"] == 1, "unsupported observation")
        require(data["kind"] in ("retrospective-classroom-observation", "synthetic-run"),
                "unsupported observation kind")
        date.fromisoformat(data["date"])
        require(strings(data["limitations"]), "limitations are required")
        require(isinstance(data["reviewer"], str) and bool(data["reviewer"].strip()), "missing reviewer")
        source = data["source"]
        require(source["coverage"] in ("partial", "complete"), "invalid source coverage")
        require(isinstance(source["description"], str) and bool(source["description"].strip()), "missing source description")
        require(source["coverage"] != "complete" or bool(source["locator"]), "complete source requires locator")
        require(set(data["runtime"]) == {"model_label", "immutable_model_id", "reasoning_setting", "environment"},
                "runtime declarations missing")
        require(isinstance(data["materials"]["version"], str) and bool(data["materials"]["version"].strip()),
                "missing material version boundary")
        require(strings(data["materials"]["files"]), "missing materials")
        if data["kind"] == "synthetic-run":
            require(bool(source["locator"]), "synthetic run requires an actual run locator")
            hashes = data["materials"].get("sha256")
            require(isinstance(hashes, dict) and set(hashes) == set(data["materials"]["files"]),
                    "synthetic run requires every material hash")
            require(all(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value)
                        for value in hashes.values()), "invalid material hash")
        for reference in data["materials"]["files"]:
            resolved = (root / reference).resolve()
            require(not Path(reference).is_absolute() and root in resolved.parents and resolved.is_file(),
                    "material must resolve inside repository")
        seen = set()
        for observation in data["observations"]:
            identifier = observation["case_id"]
            require(identifier in cases and identifier not in seen, "unknown or duplicate observation case")
            seen.add(identifier)
            require(len(observation["results"]) == len(cases[identifier]["criteria"]), "criterion count mismatch")
            for result in observation["results"]:
                require(set(result) == {"status", "evidence"}, "unexpected criterion fields")
                require(result["status"] in ("observed", "concern", "not-observed"), "invalid criterion status")
                require(isinstance(result["evidence"], str) and bool(result["evidence"].strip()), "missing observation basis")
        require(seen == set(cases), "unobserved cases must be explicit")
    return len(cases), len(paths)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        cases, records = validate(args.root.resolve())
    except (ValueError, KeyError, TypeError, OSError, yaml.YAMLError) as error:
        print(f"teaching observations failed: {error}", file=sys.stderr)
        return 1
    print(f"teaching observations: valid ({cases} multi-turn cases, {records} records; no behavioral verdict)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

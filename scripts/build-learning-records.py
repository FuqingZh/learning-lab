#!/usr/bin/env python3
"""Validate learning records and emit their learner-owned capability projection.

Examples:
  python3 scripts/build-learning-records.py validate
  python3 scripts/build-learning-records.py normalized-data --root /path/to/learning-lab
  python3 scripts/build-learning-records.py audit
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from learning_records import LearningRecordsError, build_projection


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "normalized-data", "audit"))
    parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    parsed = parse_arguments(sys.argv[1:] if arguments is None else arguments)
    try:
        projection = build_projection(parsed.root)
    except LearningRecordsError as error:
        print(f"learning records validation failed: {error}", file=sys.stderr)
        return 1
    if parsed.command == "validate":
        print(
            "learning records: valid "
            f"({projection['audit']['structured_count']} structured, "
            f"{projection['audit']['legacy_count']} legacy)"
        )
    elif parsed.command == "audit":
        print(json.dumps(projection["audit"], ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(json.dumps(projection, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

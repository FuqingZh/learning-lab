#!/usr/bin/env python3
"""Fail when committed knowledge-map projections differ from their sources."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORIES = (
    "case-labs",
    "concepts",
    "histories",
    "learning-records",
    "learning-state",
    "lessons",
    "scripts",
    "tracks",
)


def run(command: list[str], *, cwd: Path) -> None:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode:
        details = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"command failed: {' '.join(command)}\n{details}")


def files_under(root: Path) -> dict[str, bytes]:
    if not root.is_dir():
        return {}
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def compare_directory(expected: Path, actual: Path, *, label: str) -> list[str]:
    expected_files = files_under(expected)
    actual_files = files_under(actual)
    errors: list[str] = []
    for path in sorted(expected_files.keys() - actual_files.keys()):
        errors.append(f"{label}: missing generated file: {path}")
    for path in sorted(actual_files.keys() - expected_files.keys()):
        errors.append(f"{label}: unexpected generated file: {path}")
    for path in sorted(expected_files.keys() & actual_files.keys()):
        if expected_files[path] != actual_files[path]:
            errors.append(f"{label}: stale generated file: {path}")
    return errors


def main() -> int:
    try:
        with tempfile.TemporaryDirectory(prefix="learning-lab-map-check-") as directory:
            temporary_root = Path(directory) / "learning-lab"
            temporary_root.mkdir()
            for name in SOURCE_DIRECTORIES:
                shutil.copytree(ROOT / name, temporary_root / name)

            run(
                [sys.executable, "scripts/render-knowledge-map-markdown.py"],
                cwd=temporary_root,
            )
            run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "render-knowledge-map-site.py"),
                    "--root",
                    str(temporary_root),
                    "--output",
                    str(temporary_root / "site" / "index.html"),
                ],
                cwd=ROOT,
            )

            errors = compare_directory(temporary_root / "maps", ROOT / "maps", label="maps")
            errors.extend(
                compare_directory(temporary_root / "site", ROOT / "site", label="site")
            )
    except (OSError, RuntimeError) as error:
        print(f"knowledge-map generated check failed: {error}", file=sys.stderr)
        return 1

    if errors:
        print("knowledge-map generated artifacts are stale:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        print(
            "regenerate with both render-knowledge-map scripts",
            file=sys.stderr,
        )
        return 1

    print("knowledge-map generated artifacts: current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

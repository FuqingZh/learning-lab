#!/usr/bin/env python3
"""Build the self-contained knowledge explorer with the TypeScript frontend."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


RUNTIME_DIAGNOSTIC = (
    "Learning Lab site generation requires Node.js 22.x and frontend dependencies "
    "installed with `npm ci`."
)


def node_runtime() -> str:
    """Return a Node 22 executable or fail with the supported recovery command."""
    node = shutil.which("node")
    if node is None:
        raise RuntimeError(RUNTIME_DIAGNOSTIC)
    try:
        result = subprocess.run(
            [node, "--version"],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        raise RuntimeError(RUNTIME_DIAGNOSTIC) from error
    version = result.stdout.strip()
    if result.returncode or not version.startswith("v22."):
        raise RuntimeError(RUNTIME_DIAGNOSTIC)
    return node


def run_frontend_build(
    root: Path,
    output: Path,
    *,
    data_file: Path | None = None,
) -> None:
    """Invoke the sole production browser implementation."""
    toolchain_root = Path(__file__).resolve().parents[1]
    build = toolchain_root / "frontend" / "build.mjs"
    if not build.is_file():
        raise RuntimeError(f"frontend build entrypoint is missing: {build}")
    command = [
        node_runtime(),
        str(build),
        "--root",
        str(root),
        "--output",
        str(output),
    ]
    if data_file is not None:
        command.extend(["--data-file", str(data_file)])
    result = subprocess.run(
        command,
        cwd=toolchain_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        if "dependencies are missing" in detail:
            raise RuntimeError(RUNTIME_DIAGNOSTIC)
        raise RuntimeError(detail or "TypeScript frontend build failed")


def render_html(
    graph: dict[str, Any],
    learning_state: dict[str, Any],
    history: dict[str, Any] | None = None,
) -> str:
    """Render supplied normalized fixtures through the production frontend."""
    root = Path(__file__).resolve().parents[1]
    payload = {
        "graph": graph,
        "learningState": learning_state,
        "history": (
            history
            if history is not None
            else {"schema_version": 1, "dossiers": []}
        ),
    }
    with tempfile.TemporaryDirectory(prefix="learning-lab-site-render-") as directory:
        temporary = Path(directory)
        data_file = temporary / "frontend-data.json"
        output = temporary / "index.html"
        data_file.write_text(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        run_frontend_build(root, output, data_file=data_file)
        return output.read_text(encoding="utf-8")


def main(arguments: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    parsed = parser.parse_args(sys.argv[1:] if arguments is None else arguments)
    root = parsed.root.resolve()
    output = (parsed.output or root / "site/index.html").resolve()
    try:
        run_frontend_build(root, output)
    except (OSError, RuntimeError) as error:
        print(f"knowledge map site render failed: {error}", file=sys.stderr)
        return 1
    print(f"knowledge map site: rendered {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

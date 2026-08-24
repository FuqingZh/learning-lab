#!/usr/bin/env python3
"""Run the frozen frontend contracts against the isolated TypeScript build."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / "tests/knowledge-map/test_frontend_contract.py"
SPEC = importlib.util.spec_from_file_location("frontend_contract_baseline", BASE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load frontend contracts from {BASE_PATH}")
BASE_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE_MODULE)


class TestTypeScriptCandidateContract(BASE_MODULE.TestFrontendContract):
    """Require the candidate artifact to satisfy every frozen browser contract."""

    def render(self, output: Path) -> str:
        result = subprocess.run(
            ["node", str(ROOT / "frontend/build.mjs"), "--output", str(output)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return output.read_text(encoding="utf-8")


if __name__ == "__main__":
    import unittest

    unittest.main()

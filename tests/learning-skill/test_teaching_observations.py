"""Observation declarations cannot masquerade as a behavioral pass."""

from copy import deepcopy
import importlib.util
from pathlib import Path
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("observations", ROOT / "scripts/check-teaching-observations.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ObservationTests(unittest.TestCase):
    def test_missing_runtime_identity_is_allowed_but_unsupported_claims_are_not(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            directory = root / "docs/evaluations"
            directory.mkdir(parents=True)
            for name in ("continuity-observation-cases.yaml", "20260907-classroom-observation.yaml"):
                (directory / name).write_bytes((ROOT / "docs/evaluations" / name).read_bytes())
            path = directory / "20260907-classroom-observation.yaml"
            original = yaml.safe_load(path.read_text())
            for reference in original["materials"]["files"]:
                material = root / reference
                material.parent.mkdir(parents=True, exist_ok=True)
                material.write_text("Synthetic material\n")
            self.assertEqual(MODULE.validate(root), (4, 1))
            mutations = [
                lambda d: d.update(aggregate="pass"),
                lambda d: d.update(kind="synthetic-run"),
                lambda d: d.update(limitations=[]),
                lambda d: d["source"].update(coverage="complete", locator=None),
                lambda d: d["observations"][0]["results"].pop(),
                lambda d: d["observations"][0]["results"][0].update(status="pass"),
                lambda d: d["observations"][0]["results"][0].update(evidence=""),
                lambda d: d["observations"].pop(),
            ]
            for mutation in mutations:
                candidate = deepcopy(original)
                mutation(candidate)
                path.write_text(yaml.safe_dump(candidate, allow_unicode=True))
                with self.assertRaises(ValueError):
                    MODULE.validate(root)
            synthetic = deepcopy(original)
            synthetic["kind"] = "synthetic-run"
            synthetic["source"]["locator"] = "synthetic-test:run-1"
            synthetic["materials"]["sha256"] = {
                name: "a" * 64 for name in synthetic["materials"]["files"]
            }
            path.write_text(yaml.safe_dump(synthetic, allow_unicode=True))
            # This asserts declarations only, not existence of a model run.
            self.assertEqual(MODULE.validate(root), (4, 1))


if __name__ == "__main__":
    unittest.main()

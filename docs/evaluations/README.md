# Tutor evaluation contract

This directory documents the static, repository-owned evaluation contract for
the mission-led tutor. It does **not** establish model quality or reliability.
The fixtures are privacy-safe synthetic learner turns with fixed allowed
sources, observable criteria, critical failure flags, and expected durable
state facts.

Run the deterministic checks from the repository root:

```bash
python3 scripts/run-tutor-evaluation.py validate-fixtures
python3 scripts/run-tutor-evaluation.py verify-static
python3 scripts/run-tutor-evaluation.py validate-scorecard path/to/result.json
```

`verify-static` invokes no model. It validates all six fixtures and runs the
actual learning-state CLI in isolated temporary roots for the resume-only and
assisted-evidence cases. It therefore proves only that fixture expectations
match the current state engine.

## Future opt-in model runs

Any model-backed run must be opt-in and write only a sanitized aggregate
scorecard. The scorecard's `runner` object requires all of the following
non-empty fields: `provider`, `model`, `immutable_digest`, `runner_name`,
`runner_version`, `reasoning_effort`, `tool_policy`, and `sandbox`. It must
also record `aggregate` (`pass`, `fail`, `mixed`, or `incomplete`), a
non-empty `limitations` array, and an `attempt_index` for every case result.
The runner must ensure and record the following operational facts:

- immutable model identifier and digest, rather than a mutable alias alone;
- evaluator runner name and version, reasoning configuration, tool policy, and sandbox boundary;
- SHA-256 hash of the exact fixture bytes;
- one isolated run per fixture attempt, with no cross-case conversational state;
- criterion and critical-flag booleans only—no raw learner-like transcripts,
  secrets, or private workspace contents.

The scorecard schema is at
[`tests/tutor-evaluation/scorecard.schema.json`](../../tests/tutor-evaluation/scorecard.schema.json).
`validate-scorecard` checks provenance and structure, but intentionally does
not interpret a score as a claim of general reliability. Each result's boolean
maps must contain exactly the observable-criterion and critical-flag strings
from its fixture. `aggregate: pass` is allowed only for a `combined` scorecard
covering all six cases, with at least three distinct isolated attempts for each
case, where every status is `pass` and every boolean is true. An authoring-only
or holdout-only scorecard, a missing case, a `not-run` result, or fewer than
three attempts per case must use `aggregate: incomplete`. Once that full
three-attempt combined sample exists, any observed failure or false boolean
must use `fail` or `mixed`, according to the runner's documented aggregation
policy.

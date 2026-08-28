# Tutor Evaluation Status — 2026-08-27

## Decision

The v1.4 evaluation infrastructure is **structurally passed** and
**model-backed reliability is incomplete**. These are deliberately separate
claims.

The repository-owned static gate passed with six privacy-safe cases:

```text
python3 scripts/run-tutor-evaluation.py verify-static
tutor evaluation: static verification passed
(6 fixtures, sha256=a8fbf930bb7f2307d8ba048d31a7a9dfc80ca042be7e13ef942bed2435216b89)
```

The same verifier and its nine contract tests also passed inside
`bash scripts/check-structure.sh`. The state-backed cases use isolated temporary
roots and the production learning-state engine to establish only these
deterministic facts:

- a v2 resume-only event preserves the exact lesson and checkpoint, with no
  capability or review-cue change; and
- an assisted passing transfer creates a next-day review cue without promoting
  the session-derived observational capability projection.

## Model boundary

No target model was run. No provider/model/digest, reasoning setting, tool
policy, and sandbox tuple was selected and frozen for this delivery, and no raw
transcript or model scorecard was committed. Consequently this status does not
claim that a model reliably selects the mission-linked unit, withholds a due
answer, writes the right event, teaches in Chinese, uses the allowed source, or
ends with the intended unaided check.

A future opt-in run must satisfy the provenance and criterion-binding contract
in [the evaluation README](README.md) and validate its sanitized aggregate with
`scripts/run-tutor-evaluation.py validate-scorecard`. Reliability remains
`incomplete` until repeated authoring and holdout attempts meet that gate.

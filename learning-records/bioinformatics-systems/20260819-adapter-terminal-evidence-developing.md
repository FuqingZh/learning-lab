# Adapter terminal-evidence classification is developing

Superseded by
[the mastered record](20260819-adapter-terminal-evidence-mastered.md) after the
batch-level classification check was completed.

The learner recognizes that tool/runtime identity and scientific parameters
are necessary parts of computation identity, and correctly classifies a
schema-mismatched raw output or nonzero process exit as failure rather than
terminal evidence.

## Boundary still being consolidated

Successful process completion is not itself a `hit`. It only permits the
adapter to interpret a valid primary output:

```text
successful execution + valid output + accepted evidence rows -> hit
successful execution + valid output + zero evidence rows     -> no_hit
execution, parsing, linkage, or contract validation failure  -> failure
```

Only `hit` and `no_hit` are immutable reusable terminal evidence for an exact
EvidenceKey. Failure, timeout, malformed output, and adapter rejection are not
reusable evidence.

## Evidence

In unaided classification on 2026-08-19, the learner correctly rejected a
14-column InterPro TSV under a 15-column contract and an empty artifact from a
nonzero process exit. The learner initially classified a successful, valid,
zero-row result as `hit`; a batch-level application check remains before
mastery.

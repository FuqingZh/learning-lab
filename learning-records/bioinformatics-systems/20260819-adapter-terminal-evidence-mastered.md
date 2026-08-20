# Adapter terminal-evidence classification is understood

The learner can separate computation identity, process completion, raw-output
validation, and terminal evidence classification. The learner understands that
tool/runtime identity and semantic parameters are necessary but insufficient:
the complete EvidenceKey also includes sequence identity, adapter contract
version, and resource identity, after which process status and native output
must still pass validation.

The learner can classify valid evidence per input sequence:

```text
successful execution + valid output + accepted rows -> hit
successful execution + valid output + zero rows     -> no_hit
execution or output-contract violation              -> failure
```

## Evidence

In unaided batch application on 2026-08-19, the learner classified sequence A
as `hit` when it owned the only valid result rows and classified sequences B
and C as `no_hit` when the successful valid batch contained no rows for them.
The learner also classified an unexpected output row for non-input sequence D
as failure rather than exposing or committing it as evidence.

The subsequent retry action was refined separately: a deterministic linkage or
contract violation should block the batch commit and be diagnosed, not trigger
an automatic blind rerun. Retry is appropriate only after correction or when
bounded evidence supports a transient failure.

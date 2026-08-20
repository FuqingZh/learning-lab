# Adapter output validation and terminal evidence

## Four separate decisions

An external tool output becomes SeqEvi evidence only after four boundaries are
kept distinct:

```text
computation identity
  -> process completion
  -> native-output validation
  -> per-sequence terminal classification
```

## 1. Computation identity

Reusable evidence is identified by the complete tuple:

```text
EvidenceKey = (
    SequenceID,
    AdapterContractVersion,
    ToolRuntimeDigest,
    ResourceID,
    SemanticParameters,
)
```

`ToolRuntimeDigest` is an immutable executable-environment identity rather than
a path or informal version label. `ResourceID` identifies the exact annotation
database. `SemanticParameters` includes every result-affecting option and its
explicit default. The adapter contract version covers parsing, linkage, row
grain, and evidence semantics.

Matching this tuple answers whether evidence belongs to the same scientific
computation contract. It does not prove that a new execution succeeded.

## 2. Process completion

The adapter validates exit status, timeout and cancellation state, and the
presence of the expected primary raw output. A nonzero exit, timeout,
cancellation, or missing output is failure rather than `no_hit`.

## 3. Native-output validation

A present file must still satisfy the adapter contract. Checks can include:

- exact header and column layout;
- parseable scalar values and required fields;
- sequence-to-result linkage and input ownership;
- sequence digest and coordinate consistency;
- adapter-specific restrictions on result provenance;
- preservation of the upstream row grain.

An output row for a sequence absent from the submitted batch is a linkage
violation. The batch must not partially commit evidence from an output whose
ownership cannot be trusted.

## 4. Terminal classification

Classification occurs per input sequence only after successful execution and
valid output:

```text
one or more accepted evidence rows -> hit
zero accepted evidence rows        -> no_hit
invalid execution or output        -> failure
```

Execution success is therefore not equivalent to `hit`. A batch containing
rows only for A can validly yield `A=hit`, `B=no_hit`, and `C=no_hit`.

Both `hit` and `no_hit` are immutable reusable terminal evidence for one exact
EvidenceKey. Failure, timeout, malformed output, and adapter rejection are not
terminal evidence and must not be cached as `no_hit`.

## Failure and retry

Failure prevents evidence commit and preserves diagnostic information. It does
not imply that an identical blind retry is useful. A deterministic schema or
linkage violation should first be diagnosed and corrected. Retry is appropriate
only after correction or when bounded evidence indicates a transient failure.

## Sources

- [SeqEvi Sequence and Evidence Contract](https://github.com/FuqingZh/seqevi/blob/main/docs/architecture/20260720-v1.0-sequence-evidence-contract.md)
- [SeqEvi Adapter Contract](https://github.com/FuqingZh/seqevi/blob/main/docs/architecture/20260720-v1.0-adapter-contract.md)

# Layers, boundaries, and invariants

## Three structural ideas

```text
layer       owns one coherent class of responsibility
boundary    defines how responsibility is handed to another layer
invariant   states what must remain true across that handoff
```

A useful layer is not merely a directory or wrapper. It hides real complexity,
has a clear caller, and exposes a smaller stable contract than its internal
implementation.

A boundary contract can include multiple kinds of promise: domain meaning,
schema, identity, lifecycle, state transition, authority, service quality, and
compatibility. `Contract` therefore does not name one universal checklist item;
it names the observable agreement between a caller and the layer that owns the
boundary. The track-level
[systems map](../../tracks/bioinformatics-systems/SYSTEMS-MAP.md) provides the
full taxonomy and contract anatomy.

## A generic analysis path

```text
input -> computation -> storage -> delivery
```

Possible boundary invariants include:

- input: every emitted record is structurally and semantically valid;
- computation: every result is linked to the exact input and computation;
- storage: a successful commit exposes complete state rather than a partial
  write;
- delivery: the reported status agrees with authoritative state.

Downstream layers may rely on an upstream invariant only if the owning boundary
actually validates and enforces it.

## First broken boundary

Suppose an invalid date is silently converted to null, the computation treats
null as zero, the database commits the output, and the user downloads a report.

The storage and delivery mechanisms completed operationally. The end-to-end
system nevertheless failed because the report is semantically wrong. The first
broken invariant belongs to the input boundary: invalid domain data escaped as
if it were valid.

```text
input invariant broken
  -> computation consumes a false assumption
  -> storage faithfully persists a wrong result
  -> delivery faithfully exposes a wrong result
```

The final error is a downstream symptom, not necessarily the origin.

## Why validation belongs at the owning boundary

The layer that owns a concept should enforce its rules. An input parser can own
syntax, while a domain-validation boundary owns whether a date, taxon, unit, or
scientific value is acceptable. A storage layer should not guess missing domain
semantics, and a presentation layer should not repair silently corrupted state.

Failing at the earliest authoritative boundary:

- keeps invalid state from spreading;
- reduces the number of components that must defend against it;
- produces a diagnosis close to the cause;
- protects downstream invariants from false assumptions.

## Diagnostic rule

When a final result is wrong:

1. trace the data, control, and state flows backward;
2. identify the earliest boundary whose promised postcondition was false;
3. fix validation or ownership at that boundary;
4. do not treat successful downstream mechanics as proof of correctness.

```text
operational success != semantic correctness
```

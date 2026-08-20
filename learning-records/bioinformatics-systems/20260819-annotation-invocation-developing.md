# Annotation invocation mapping is developing

Superseded by
[the mastered record](20260819-annotation-invocation-mastered.md) after the
second-invocation cache-provenance check was completed.

The learner understands that identical canonical protein content maps to one
`SequenceID`, that exact cached evidence avoids external recomputation, and
that only the distinct cache-miss sequence C needs computation in the initial
example.

## Boundary still being consolidated

Compute deduplication must not collapse invocation-level input records. If the
input FASTA contains A, B, and C, `sequence-map.tsv` retains three rows in input
order even when A and B map many-to-one to the same `SequenceID` and evidence.

`EvidenceSource` is not an input identifier. Its value records provenance for
this invocation:

```text
A -> cache
B -> cache
C -> computed
```

`EvidenceStatus` independently records `hit` or `no_hit`. A cached no-hit is
therefore `EvidenceSource=cache` and `EvidenceStatus=no_hit`; source and status
must not be conflated.

## Evidence

In unaided application on 2026-08-19, the learner correctly computed one cache
miss and one shared SequenceID for duplicate inputs A and B. The learner
initially collapsed the three invocation rows to two and interpreted
`EvidenceSource` as an input label. A materialization-level check remains
before mastery.

In a second check, the learner retained all three input rows and correctly
computed only one unique cache-miss sequence for duplicate inputs D and E. The
remaining boundary is temporal provenance: both D and E receive
`EvidenceSource=computed` because their shared evidence was newly computed in
this invocation. Intra-invocation deduplication does not turn the second input
alias into a historical cache reuse.

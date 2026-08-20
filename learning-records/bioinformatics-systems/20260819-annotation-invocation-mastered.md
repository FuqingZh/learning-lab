# Annotation invocation mapping is understood

The learner can distinguish invocation input records, unique canonical
sequences, exact EvidenceKeys, and actual external computations. Duplicate
input labels remain separate rows in `sequence-map.tsv` while mapping
many-to-one to one `SequenceID` and one reusable evidence object.

The learner can also distinguish evidence provenance from evidence status:

```text
EvidenceSource = cache | computed
EvidenceStatus = hit | no_hit
```

Within one invocation, duplicate inputs sharing a newly computed sequence both
receive `EvidenceSource=computed`; compute deduplication does not make one alias
a cache hit. In a later invocation under the same exact EvidenceKey, both reuse
the committed evidence and receive `EvidenceSource=cache`.

## Evidence

In unaided application on 2026-08-19, the learner:

- computed only one unique sequence for duplicate cache misses D and E;
- retained D, E, and F as three invocation-level sequence-map rows;
- assigned D and E the shared `hit` and F its cached `no_hit`; and
- correctly concluded that a second identical invocation performs zero
  external computations, with D and E reported as cached hits and F as a
  cached no-hit.

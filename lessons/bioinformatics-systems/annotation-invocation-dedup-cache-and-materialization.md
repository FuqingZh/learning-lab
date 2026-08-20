# Annotation invocation: deduplication, cache, and materialization

## The complete flow

One annotation invocation separates user-facing input records from reusable
content evidence:

```text
parse and canonicalize input
  -> preserve input mapping
  -> deduplicate by SequenceID
  -> look up exact EvidenceKeys
  -> compute unique misses
  -> validate native outputs
  -> commit terminal evidence
  -> materialize results for every input record
```

## Three different counts

For an input FASTA containing A, B, and C, where A and B have identical
canonical sequence content:

```text
input records:       3  (A, B, C)
unique SequenceIDs:  2  (SQ.x, SQ.y)
external computes:   0, 1, or 2 depending on exact cache state
```

Deduplication reduces work at the content layer. It must not delete or merge
the user's invocation-level records.

## Sequence map

`sequence-map.tsv` preserves one row per input FASTA record in input order.
Different input IDs may map to the same `SequenceID`:

```text
A -> SQ.x
B -> SQ.x
C -> SQ.y
```

This many-to-one mapping is the bridge between ephemeral user labels and
reusable content-addressed evidence.

## Exact cache lookup

Cache lookup operates on the complete EvidenceKey rather than SequenceID alone:

```text
EvidenceKey = (
    SequenceID,
    AdapterContractVersion,
    ToolRuntimeDigest,
    ResourceID,
    SemanticParameters,
)
```

Only an exact terminal `hit` or `no_hit` avoids recomputation. A changed
runtime, resource, adapter contract, or semantic parameter creates a distinct
cache miss even for the same sequence.

## Source and status are independent

Each materialized input row reports two separate dimensions:

```text
EvidenceSource = cache | computed
EvidenceStatus = hit | no_hit
```

All four valid combinations can occur across invocations:

```text
cache + hit
cache + no_hit
computed + hit
computed + no_hit
```

`computed` means the shared evidence was newly computed during this invocation.
If duplicate inputs D and E share one cache-miss SequenceID, the tool computes
that sequence once, but both sequence-map rows receive `computed`. Neither
input alias is the scientific owner of the computation.

After that evidence is committed, a second identical invocation performs zero
computations for D and E; both rows then receive `cache` while preserving the
same evidence status.

## Materialization boundary

Evidence is stored once per exact content-and-computation identity, then joined
back to every invocation input through `SequenceID`. Materialization can repeat
the reference to shared evidence for A and B without duplicating the underlying
scientific computation or losing either input label.

This yields two simultaneous guarantees:

- computation and storage are deduplicated by stable content identity;
- delivery remains faithful to every user-provided FASTA record.

## Sources

- [SeqEvi Sequence and Evidence Contract](https://github.com/FuqingZh/seqevi/blob/main/docs/architecture/20260720-v1.0-sequence-evidence-contract.md)
- [SeqEvi Adapter Contract](https://github.com/FuqingZh/seqevi/blob/main/docs/architecture/20260720-v1.0-adapter-contract.md)

# Result joins, row grain, and no-hit preservation

## Grain determines join multiplicity

SeqEvi result relations intentionally have different row grains:

```text
sequence_map  one row per input FASTA record
evidence      one row per adapter-native accepted evidence item
annotations   one row per input record and matching evidence row
```

If input IDs A and B share one SequenceID and that sequence has three Pfam
domain-match rows, joining by SequenceID produces six annotations rows:

```text
2 input rows * 3 evidence rows = 6 joined rows
```

This is not accidental duplication. Each output row represents a distinct
input-record-to-native-match relationship.

## The canonical left join

The public `annotations` view is conceptually:

```sql
SELECT sequence_map.*, evidence.<adapter_columns>
FROM sequence_map
LEFT JOIN evidence USING (SequenceID)
```

The left side is `sequence_map` because the result is a complete snapshot of
the requested FASTA, including successful no-hit inputs.

For example:

```text
A -> two evidence matches
B -> no_hit
C -> one evidence match
```

The left join yields four rows: two for A, one for B, and one for C. B retains
all sequence-map fields such as InputID, InputHeader, SequenceID, MD5, Length,
EvidenceStatus, and EvidenceSource. Only the adapter evidence fields are null.

## Why inner join is wrong for the complete view

An inner join would return only the three hit-match rows and silently remove B.
That would confuse two different statements:

```text
the input was processed successfully and had no accepted evidence
the input record was never present in the result
```

`no_hit` is reusable terminal evidence, not missing data. It must remain visible
through the sequence map and canonical annotations view.

## Explicit one-row-per-input aggregation

Consumers may need one display row per InputID, but the aggregation belongs in
an explicit downstream query or presentation layer. The chosen result must
state its semantics, for example:

- a list of structs preserving accession, coordinates, score, and E-value;
- a match count;
- a documented best-hit selection rule, including tie behavior.

Comma concatenation or an implicit first-row choice can destroy match tuples
and should not be presented as native evidence.

## Review rule

Before joining or aggregating, state:

1. the grain of every input relation;
2. the join cardinality expected for each key;
3. how no-hit inputs remain observable; and
4. whether aggregation preserves evidence or deliberately summarizes it.

## Source

- [SeqEvi v1.1 Result Consumption Contract](https://github.com/FuqingZh/seqevi/blob/main/docs/architecture/20260804-v1.1-result-consumption-contract.md)

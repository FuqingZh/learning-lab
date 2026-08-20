# Thin normalization and native row grain

## Purpose

SeqEvi normalization makes native evidence safe to store and consume. It does
not reinterpret different upstream tools as one universal annotation ontology.

The governing distinction is:

```text
representation-preserving change -> thin normalization
meaning- or grain-changing change -> semantic transformation
```

## Row grain

Row grain answers what one row represents. In a Pfam-native result, one row may
represent one domain-signature match at one sequence interval. Three matches on
the same protein are therefore three evidence rows.

Collapsing them into one protein row changes the grain and can destroy the
relationships among:

```text
signature accession <-> start/end <-> score <-> E-value
```

Comma-separated lists do not reliably preserve repeated occurrences, nulls,
ordering, or the tuple-level correspondence required to reconstruct the native
matches.

## Permitted thin normalization

An adapter may perform narrowly specified representation changes such as:

- adding canonical `SequenceID` linkage;
- converting a valid numeric string to the required numeric scalar type;
- normalizing declared null representations;
- handling invalid encodings under an explicit contract;
- documenting required derived or renamed fields;
- sorting and writing validated rows into an adapter-specific artifact.

These operations preserve the upstream row grain and original field meaning.
For example, converting Pfam E-value text `"1e-20"` to a floating-point value is
thin normalization if it remains the same Pfam match statistic on the same row.

## Cross-adapter semantic boundary

Columns with the same name are not automatically equivalent. An eggNOG
seed-alignment E-value and a Pfam region-to-profile-HMM E-value differ in:

- the objects being compared;
- the scoring model and null hypothesis;
- search-space calibration;
- whole-sequence versus region-level row grain;
- the biological claim supported by the row.

Renaming both values to `evidence_strength`, unioning their rows, and comparing
the numbers would invent semantics not supplied by either upstream tool. This
remains invalid even if their storage types and column layouts can be made
identical.

SeqEvi therefore keeps adapter outputs physically and logically separate.
Cross-tool interpretation belongs in an explicit downstream consumption layer
whose comparison rules and limitations are separately defined.

## Review test

Ask three questions before calling a transformation thin:

1. Does one output row still represent the same native object?
2. Can the original match fields and their relationships be reconstructed?
3. Did the adapter preserve upstream meaning rather than invent comparability?

If any answer is no, the operation exceeds thin normalization.

## Source

- [SeqEvi Adapter Contract](https://github.com/FuqingZh/seqevi/blob/main/docs/architecture/20260720-v1.0-adapter-contract.md)

# Result joins and row grain are understood

The learner can predict one-to-many join multiplication from relation grain
and place one-row-per-input aggregation in an explicit downstream consumption
or presentation layer rather than altering native evidence.

The learner also understands why the canonical `annotations` relation is a
left join from `sequence_map` to adapter evidence. A no-hit input retains its
complete sequence-map fields, including `EvidenceStatus=no_hit` and
`EvidenceSource`, while adapter evidence fields are null. An inner join would
silently delete meaningful no-hit records.

## Evidence

In unaided application on 2026-08-19, the learner:

- predicted six rows when two input IDs sharing one SequenceID joined to three
  native Pfam match rows;
- kept any one-row-per-input aggregation at the outer presentation layer;
- predicted four rows for a left join containing two matches for A, a no-hit B,
  and one match for C; and
- predicted that an inner join would return only three rows and incorrectly
  discard the biologically meaningful no-hit input.

The description of B was refined from an ID-only empty row to a complete
sequence-map row with null adapter-evidence fields.

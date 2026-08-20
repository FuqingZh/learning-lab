# Thin normalization is developing

Superseded by
[the mastered record](20260819-thin-normalization-mastered.md) after the
cross-adapter semantic comparison was completed.

The learner understands that an adapter must preserve the native evidence row
grain and enough original fields to reconstruct each upstream match. In an
unaided example, the learner rejected collapsing three Pfam domain-match rows
into one comma-separated protein row because deleting match coordinates makes
the original evidence impossible to reconstruct.

## Boundary still being consolidated

The loss is broader than coordinates alone. Changing from one row per native
match to one row per protein can also destroy the correspondence among domain
accession, start and end positions, score, E-value, and repeated occurrences.

Thin normalization may add canonical `SequenceID` linkage and normalize
required scalar types, null values, or invalid encodings. It must preserve the
upstream row grain and field meanings, document derived or renamed fields, and
must not invent a shared ontology merely because two adapters expose similarly
named columns.

## Evidence

On 2026-08-19, the learner correctly identified irreversibility as evidence
that domain-row aggregation exceeded thin normalization. A cross-adapter
semantic comparison remains before mastery.

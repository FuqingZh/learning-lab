# Learning-record legacy audit — 2026-08-27

## Snapshot and boundary

This is an evidence-bounded migration inventory, not a capability assessment.
It was produced at `2026-08-27T15:28:41+08:00` with:

```bash
python3 scripts/build-learning-records.py audit
```

The checked commit was `7b5919013120509591d2bd4497a70031bac6d7db`.
The worktree was dirty and contained concurrent, uncommitted changes, including
the newly introduced learning-record schema and validator; this document
therefore records that visible working-tree snapshot rather than a clean-HEAD
release artifact.

The audit reported **37 legacy** records, **37 pending legacy** decisions,
**0 resolved legacy** decisions, and **0 structured** records. A
structured record is defined by [the learning-record schema](../../learning-records/README.md): it has
`schema_version: 1`, an explicit concept mapping, a structured capability
review, and `evidence_sessions` links.  The [audit command](../../learning-records/README.md#learning-records)
is the repeatable source for this inventory.

All 37 records lack a structured schema version, explicit structured capability
review, and session-evidence links.  Some also use the old `Status` frontmatter.
None may be promoted from filename, prose, or old status text.  In particular,
the current reviewed capability projection is **unassessed by design**: this
audit did not migrate any record.

## Inventory and required disposition

### Explicitly superseded — history-only (8)

These eight records explicitly name a replacement.  They remain traceable
history and are not migration candidates unless a later recorded decision says
otherwise.

- `learning-records/bioinformatics-systems/0001-sequence-level-reuse-starting-point.md`
- `learning-records/bioinformatics-systems/0004-annotation-boundaries-developing.md`
- `learning-records/bioinformatics-systems/0006-alignment-significance-developing.md`
- `learning-records/bioinformatics-systems/20260819-orthology-transfer-developing.md`
- `learning-records/scientific-ai-platforms/0007-authority-boundary-starting-point.md`
- `learning-records/scientific-ai-platforms/0010-dataset-handle-boundary-developing.md`
- `learning-records/scientific-ai-platforms/0012-authentication-authorization-developing.md`
- `learning-records/scientific-ai-platforms/0014-contract-invariants-developing.md`

### Active `*-mastered` filenames — manual-review candidates only (21)

The suffix is historical labeling, not evidence of a demonstrated capability.
Each item needs a human review that can establish its exact concepts, state,
assistance condition, and cited session observations before it can become a
structured record.

- `learning-records/bioinformatics-systems/0003-exact-evidence-reuse-mastered.md`
- `learning-records/bioinformatics-systems/0005-annotation-boundaries-mastered.md`
- `learning-records/bioinformatics-systems/0009-alignment-significance-mastered.md`
- `learning-records/bioinformatics-systems/20260819-adapter-terminal-evidence-mastered.md`
- `learning-records/bioinformatics-systems/20260819-annotation-invocation-mastered.md`
- `learning-records/bioinformatics-systems/20260819-cache-authority-rebuildability-mastered.md`
- `learning-records/bioinformatics-systems/20260819-orthology-transfer-mastered.md`
- `learning-records/bioinformatics-systems/20260819-protein-entry-types-mastered.md`
- `learning-records/bioinformatics-systems/20260819-result-joins-row-grain-mastered.md`
- `learning-records/bioinformatics-systems/20260819-system-success-beyond-computation-mastered.md`
- `learning-records/bioinformatics-systems/20260819-system-success-flow-boundaries-mastered.md`
- `learning-records/bioinformatics-systems/20260819-thin-normalization-mastered.md`
- `learning-records/bioinformatics-systems/20260820-contract-taxonomy-idempotency-mastered.md`
- `learning-records/bioinformatics-systems/20260820-layers-boundaries-invariants-mastered.md`
- `learning-records/bioinformatics-systems/20260821-cross-cutting-quality-objectives-mastered.md`
- `learning-records/bioinformatics-systems/20260821-systems-map-first-pass-mastered.md`
- `learning-records/scientific-ai-platforms/0008-validation-feedback-boundary-mastered.md`
- `learning-records/scientific-ai-platforms/0011-handle-boundary-mastered.md`
- `learning-records/scientific-ai-platforms/0013-authentication-authorization-mastered.md`
- `learning-records/scientific-ai-platforms/0015-contract-invariants-mastered.md`
- `learning-records/scientific-ai-platforms/0016-idempotency-foundations-mastered.md`

### Active developing records — insufficient for capability (7)

These are current historical learning notes.  They are not failures, but they
cannot establish a reviewed capability without the same explicit evidence as
the preceding group.

- `learning-records/bioinformatics-systems/20260819-adapter-terminal-evidence-developing.md`
- `learning-records/bioinformatics-systems/20260819-annotation-invocation-developing.md`
- `learning-records/bioinformatics-systems/20260819-cache-authority-rebuildability-developing.md`
- `learning-records/bioinformatics-systems/20260819-protein-entry-types-developing.md`
- `learning-records/bioinformatics-systems/20260819-result-joins-row-grain-developing.md`
- `learning-records/bioinformatics-systems/20260819-system-success-flow-boundaries-developing.md`
- `learning-records/bioinformatics-systems/20260819-thin-normalization-developing.md`

### Early classification record — insufficient for capability (1)

- `learning-records/bioinformatics-systems/0002-evidence-reuse-classification.md`

This record is neither an explicit supersession nor an active `*-mastered` or
`*-developing` filename case.  Its early classification wording cannot supply
the missing structured review fields.

## Common blockers and next decision

Every inventory item is blocked from authoritative capability use by all of the
following absent facts:

1. no structured `schema_version` contract;
2. no explicit `concepts` mapping to canonical concept IDs;
3. no structured `capability_state` plus `assisted` review condition; and
4. no `evidence_sessions` linkage to append-only session observations.

Those facts must be recorded, not reconstructed from a filename or narrative.
For each listed record, a future review must record exactly one disposition:

- migrate with explicit evidence into a valid structured record;
- remain legacy, with the reason preserved; or
- be superseded by a new structured record.

The pending audit count reaches zero only through those recorded decisions. A
structured replacement can name a legacy path in `supersedes`; the legacy file
then remains traceable with `resolved_by` while leaving the pending queue. A
bulk filename/prose inference is not a valid migration path.

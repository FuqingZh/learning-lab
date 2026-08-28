# Learning Records

Records capture demonstrated personal learning state; they are not source
repository authority. Each record belongs to one capability track.

Structured records are the only source for the machine-readable capability
projection. They begin with the exact frontmatter schema below and cite
append-only session evidence. A record may cover more than one concept only
when every concept is covered by the record's track and observed by its cited
sessions.

```yaml
---
schema_version: 1
track: scientific-ai-platforms
concepts:
  - idempotency
capability_state: usable
demonstrated_at: "2026-08-27"
assisted: false
evidence_sessions:
  - 20260827T120000+0800-idempotency-fresh-case-transfer
supersedes: []
---
```

`capability_state` is one of `encountered`, `familiar`, `usable`, or
`retained`. `usable` requires an unassisted transfer or real-work pass;
`retained` additionally requires two unassisted passing observations at least
seven days apart and a latest transfer or real-work pass. `demonstrated_at`
must match the latest relevant cited observation's local calendar date.

Historical Markdown files without `schema_version` are legacy: they remain
readable and auditable, but never imply a capability state from filename,
prose, or a legacy `Status` frontmatter field. The audit names missing schema,
missing structured-capability review, and missing session links explicitly.
When a structured record lists a legacy record in `supersedes`, that legacy
entry remains traceable but is marked with `resolved_by`; only entries with an
empty `resolved_by` list remain migration work.
Inspect the migration inventory with:

```bash
python3 scripts/build-learning-records.py audit
python3 scripts/build-learning-records.py normalized-data
```

- [Bioinformatics Systems](bioinformatics-systems/)
- [Scientific AI Platforms](scientific-ai-platforms/)

Existing numbered records retain their historical filenames. New records use
`YYYYMMDD-topic-state.md`. A developing or superseded record remains traceable
and links directly to its replacement when one exists.

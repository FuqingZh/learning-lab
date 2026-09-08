# Bioinformatics Systems Track

This track builds transferable biological and computing understanding using
SeqEvi as the anchor case. SeqEvi makes sequence identity, annotation evidence,
adapter execution, storage, concurrency, and result-consumption boundaries
concrete; its current implementation is case evidence rather than the syllabus.

Do not optimize for memorizing current relation names, columns, schema IDs,
paths, CLI flags, or version-specific contracts. Begin with the underlying
biology, cache model, relational model, execution model, transaction, or
concurrency problem; use SeqEvi only after the principle is independently
understood, and finish with a transfer problem outside SeqEvi.

## Read in this order

1. [Modern Scientific Systems Map](SYSTEMS-MAP.md)
2. [Curriculum](CURRICULUM.md)
3. [Resources](RESOURCES.md)
4. [Learning records](../../learning-records/bioinformatics-systems/)
5. [Reusable lessons](../../lessons/bioinformatics-systems/)

## Recorded course context

Legacy classroom records describe work on biological annotation, alignment,
orthology, exact evidence reuse, row grain, terminal evidence, joins, cache,
concurrency and end-to-end scientific results. They also record a systems-map
orientation and an integrated microscopy example. These are historical
observations, not current structured capability assessments.

The 2026-09-07 workspace audit finds 37 legacy records and no structured reviews.
Do not infer mastery from those filenames or extend a case answer to untested
skills. Use reviewed records for capability, the session engine for observations
and review cues, and navigation for current discussion position:

```bash
python3 scripts/build-learning-records.py normalized-data
python3 scripts/build-learning-state.py normalized-data
python3 scripts/check-teaching-navigation.py resolve --track bioinformatics-systems
```

The documented route proceeds from the systems-map orientation into program,
process and service, then volatile memory and durable state. This route is
preserved; when no matching resume exists, use the learner's current request
and relevant records rather than importing another track's checkpoint.

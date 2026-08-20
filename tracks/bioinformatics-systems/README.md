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

## Current state

Biological annotation boundaries, alignment significance, orthology-aware
transfer, exact evidence reuse, native row grain, terminal evidence states,
deduplicated computation, and no-hit-preserving joins have been demonstrated
through SeqEvi cases.

The course is now deliberately returning to the whole-system first pass. The
active objective is to build the seven-part systems map and trace one generic
scientific request through it. Cache, SQL, async execution, transactions, and
concurrency will then be revisited as connected mechanisms rather than isolated
next topics.

The recently completed DuckDB relation and join exercises remain useful case
evidence, but they do not define the next lesson sequence.

The learner has already distinguished cache, source of truth, and materialized
results by rebuildability and deletion impact. That remains valid progress, but
the expiration/eviction/invalidation drill is deferred until the systems-map
orientation is complete.

In the systems-map first pass, the learner has now demonstrated the distinction
among data flow, control flow, and state flow; local versus end-to-end success;
and authoritative state versus caller knowledge after an ambiguous outcome.
Layers, boundaries, and invariants are also demonstrated, including diagnosis
at the first violated boundary and the distinction between operational
completion and semantic correctness. Contract taxonomy is now demonstrated as
well, including schema, identity, lifecycle, transaction, authority, service,
and compatibility promises; the learner also separates idempotency from
physical compute deduplication. The next orientation concept is how
cross-cutting qualities create measurable tradeoffs and budgets across every
layer rather than belonging to one component.

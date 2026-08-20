# Bioinformatics Systems Curriculum

This map preserves the whole journey while each session teaches only one
bounded, demonstrable capability. SeqEvi is introduced after the underlying
concept and serves as a case laboratory, not as a list of tables or contracts
to memorize.

## Required first pass

Read and retrieve the [Modern Scientific Systems Map](SYSTEMS-MAP.md) before
following the depth modules below. The first pass builds a shallow but complete
model of domain meaning, data and identity, computation, state, interfaces,
concurrency and failure, and operations and evolution.

No cache policy, SQL operator, async primitive, SeqEvi table, or adapter
contract should be taught as an isolated next item before the learner can place
it on that map.

## Spiral teaching route

Each computing topic follows this order:

```text
location on the whole-system map
  -> underlying problem
  -> implementation-independent model
  -> minimal example or experiment
  -> design tradeoffs and failure modes
  -> SeqEvi application
  -> transfer to a fresh system
```

Repository-specific relation names, columns, paths, command flags, and version
identifiers may explain a case but are not mastery targets unless the active
lesson explicitly concerns that public contract.

## Depth modules

The numbered modules below describe eventual depth and dependencies. They are
not the first-pass teaching order and should not be traversed as a checklist of
adjacent details.

## 0. Systems reasoning

Separate biological facts, scientific contracts, software representations,
operational settings, and deployment choices. Learn to read invariants,
provenance, identities, states, and failure evidence.

## 1. Proteins and FASTA

Amino acids, residues, proteins, alphabets, ambiguity and stop markers; bytes,
text encodings, FASTA headers and records, streaming parsing and validation.

## 2. Representation and content identity

Bytes, text, records, equality, canonicalization, aliases, hashing, collisions,
SHA-512, MD5 compatibility, GA4GH refget, and content-addressed systems.
Explain why a project, filename, accession, and header are not content identity.

## 3. Cache and reuse from first principles

Why caches exist; key-value lookup; hit, miss, and negative caching; cache-aside
flow; correctness versus performance; identity, invalidation, eviction,
staleness, provenance, and reproducibility. Apply these ideas to annotation as
an evidence-producing computation and then to SeqEvi's exact EvidenceKey.

## 4. Bioinformatics search

Alignment, scoring, E-values, homology, orthology, profile HMMs, domains,
signatures, and functional transfer. Compare eggNOG-mapper/DIAMOND,
InterProScan/Pfam/HMMER, and dbCAN only after the biological and statistical
models are clear.

## 5. Relational data and SQL

Relations, rows, columns, types, schemas, keys, constraints, null, grain,
selection, projection, joins, grouping, aggregation, subqueries, views,
indexes, and query plans. Use generic data before applying SQL, DuckDB,
Parquet, or Polars to SeqEvi results.

## 6. Execution models: synchronous, asynchronous, and parallel

Call stacks, blocking, latency, throughput, processes, threads, coroutines,
event loops, async I/O, CPU parallelism, batching, queues, backpressure,
subprocesses, timeouts, cancellation, and cleanup. Explain why async does not
automatically mean parallel or faster.

## 7. Adapter and pipeline boundaries

Parse, stage, deduplicate, look up, compute misses, validate, commit, and
materialize. Study upstream tools versus adapters, native schemas, thin
normalization, scientific versus operational parameters, raw artifacts,
acceptance tests, and why a boundary should hide complexity without inventing
semantics.

## 8. Storage and transactions

Metadata versus immutable artifacts; SQLite, PostgreSQL, POSIX files,
transactions, uniqueness, idempotency, atomicity, integrity, and recovery.

## 9. Concurrency

Races, duplicate work, locks, claims, leases, fencing, renewal, deadlines,
cancellation, ownership loss, and ambiguous network outcomes. Distinguish
correctness, compute deduplication, and prompt cancellation.

## 10. Deployment

Processes, users, UID/GID, permissions, mounts, HTTP, authentication, TLS,
secrets, services and observability; containers, OCI identities, supply-chain
evidence, profiles, setup, and external resources.

## 11. Workflow integration

Cromwell/WDL, shared Store access, and site deployment, while preserving
SeqEvi's independence from workflow engines, CephFS, Docker, Kubernetes, and
specific products.

## 12. Validation and evolution

Unit, contract, integration, concurrency, scientific-equivalence, benchmark,
failure-injection and release tests; compatibility, schema evolution,
reproducibility, licenses, notices, SBOM, provenance, and release gates.

## Learning rule

Coverage is not mastery. A layer is established only after the learner can
retrieve and apply its central distinctions to a new case. Remembering a
SeqEvi table or field without being able to reconstruct the underlying cache,
SQL, execution, or concurrency principle does not count as mastery.

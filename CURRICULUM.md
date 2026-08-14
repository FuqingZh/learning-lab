# SeqEvi Systems Curriculum

This map preserves the whole journey while each session teaches only one
bounded, demonstrable capability.

## 0. Systems reasoning

Separate biological facts, scientific contracts, software representations,
operational settings, and deployment choices. Learn to read invariants,
provenance, identities, states, and failure evidence.

## 1. Proteins and FASTA

Amino acids, residues, proteins, alphabets, ambiguity and stop markers; bytes,
text encodings, FASTA headers and records, streaming parsing and validation.

## 2. Content identity

Canonicalization, equality, aliases, hashing, collisions, SHA-512, MD5
compatibility, GA4GH refget, and content-addressed systems. Explain why a
project, filename, accession, and header are not sequence identity.

## 3. Annotation evidence

Annotation as an evidence-producing computation; the complete EvidenceKey;
hit, cached no-hit, failure, immutability, exact reuse, and provenance.

## 4. Bioinformatics search

Alignment, scoring, E-values, homology, orthology, profile HMMs, domains,
signatures, and functional transfer. Compare eggNOG-mapper/DIAMOND,
InterProScan/Pfam/HMMER, and dbCAN.

## 5. Adapter boundaries

Upstream tools versus adapters, native schemas, thin normalization, runtime
digest, resource lock, scientific versus operational parameters, parser
contracts, raw artifacts, and acceptance tests.

## 6. An annotation invocation

Parse, stage, deduplicate, look up, compute misses, validate, commit, and
materialize. Study Python values, batching, files, subprocesses, environments,
working directories, process groups, timeout, and cancellation.

## 7. Data consumption

Rows, columns, schemas, nulls, grain and joins; TSV, JSON, Parquet, DuckDB, SQL,
Polars lazy execution, projection, predicate pushdown, and stable domain APIs.

## 8. The Store

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
retrieve and apply its central distinctions to a new case.

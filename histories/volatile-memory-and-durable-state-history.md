---
schema_version: 1
id: volatile-memory-and-durable-state-history
title: Development of volatile memory and durable state boundaries
summary: Documents selected steps from stable-storage abstraction through transaction durability, write-ahead recovery, and a modern file-synchronization boundary without asserting one direct lineage.
concepts: []
lessons:
  - lessons/bioinformatics-systems/volatile-memory-and-durable-state.md
tracks:
  - bioinformatics-systems
milestones:
  - id: lampson-sturgis-stable-storage-1979
    year: 1979
    month: 6
    day: 1
    kind: formalization
    actors:
      - Butler W. Lampson
      - Howard E. Sturgis
    claim: Lampson and Sturgis describe volatile processor state and construct an idealized stable-storage abstraction from disk pages, checked writes, redundancy, and post-crash cleanup under stated physical-failure assumptions.
    evidence_basis: primary-source
    sources:
      - url: https://bwlampson.site/21-CrashRecovery/WebPage.html
        title: Crash Recovery in a Distributed Data Storage System
        publisher: Butler W. Lampson archive
        role: primary
        kind: archive
  - id: haerder-reuter-durability-1983
    year: 1983
    month: 12
    day: null
    kind: formalization
    actors:
      - Theo Haerder
      - Andreas Reuter
    claim: Haerder and Reuter distinguish usually volatile main memory from permanent database storage and define durability as the guarantee that committed transaction results survive subsequent malfunctions within the recovery model they analyze.
    evidence_basis: primary-source
    sources:
      - url: https://doi.org/10.1145/289.291
        title: Principles of Transaction-Oriented Database Recovery
        publisher: ACM Computing Surveys
        role: primary
        kind: paper
  - id: aries-write-ahead-recovery-1992
    year: 1992
    month: 3
    day: null
    kind: revision
    actors:
      - C. Mohan
      - Don Haderle
      - Bruce Lindsay
      - Hamid Pirahesh
      - Peter Schwarz
    claim: The ARIES paper presents a write-ahead-logging recovery method intended to preserve transaction atomicity and durability across process, transaction, system, and media failures while supporting fine-granularity locking and partial rollback.
    evidence_basis: primary-source
    sources:
      - url: https://doi.org/10.1145/128765.128770
        title: "ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging"
        publisher: ACM Transactions on Database Systems
        role: primary
        kind: paper
  - id: linux-fsync-2026
    year: 2026
    month: 2
    day: 8
    kind: revision
    actors:
      - Linux man-pages project
    claim: The Linux fsync documentation distinguishes modified in-core file state from completed transfer to a storage device and states that synchronizing a file does not necessarily synchronize its containing directory entry.
    evidence_basis: primary-source
    sources:
      - url: https://man7.org/linux/man-pages/man2/fsync.2.html
        title: fsync(2) - Linux manual page
        publisher: Linux man-pages project
        role: primary
        kind: professional-documentation
---

## Historical setting

This dossier follows selected documents that make crash-survival boundaries
explicit. It does not claim that volatile memory, stable storage, transaction
durability, write-ahead logging, and `fsync` were invented together or form one
proved causal lineage. The documents address different layers: a distributed
storage abstraction, database transaction recovery, a concrete recovery
method, and a current operating-system interface.

## What the sources establish

The 1979
[Lampson and Sturgis report](https://bwlampson.site/21-CrashRecovery/WebPage.html)
starts from the possibility that a computer crashes and loses information it
held immediately before the crash. It distinguishes volatile processor state
from stable storage and constructs the latter as an ideal abstraction using
paired disk pages, checked writes, redundancy, and cleanup after crashes. The
abstraction is justified only under the report's stated assumptions about disk
errors, decay, and crashes.

The 1983
[Haerder and Reuter paper](https://doi.org/10.1145/289.291) describes a DBMS
storage hierarchy in which main memory and database or log buffers are usually
volatile and can be lost on abnormal termination. It defines durability as a
guarantee that committed transaction results survive later malfunctions and
relates recovery to movement and reconstruction across volatile and permanent
storage.

The 1992 [ARIES paper](https://doi.org/10.1145/128765.128770) presents a
write-ahead-logging recovery method for transaction systems. It describes
logging, restart processing, redo, compensation records, and undo support in a
method intended to preserve atomicity and durability across several stated
failure classes while permitting fine-grained concurrency and partial
rollback.

The current
[Linux `fsync` documentation](https://man7.org/linux/man-pages/man2/fsync.2.html)
specifies an application-visible boundary between modified in-core file state
and transfer to a disk or other permanent storage device. It also states that
`fsync` on the file alone does not necessarily make the containing directory
entry durable; the directory may require a separate synchronization call.

## What the sources do not establish

The Lampson and Sturgis report was circulated in drafts and is recorded by its
author's archive as an unpublished technical report. It does not establish
global priority for stable storage, and its ideal abstraction is not a claim
that physical media cannot fail. Its construction depends on a bounded failure
model and sufficient independence between redundant pages.

The 1983 paper does not establish that every database implementation, every
configuration, or every returned `COMMIT` covers all device, node, region, or
operator failures. The ARIES paper documents one recovery family rather than
the only possible path to durability, and a recovery algorithm cannot make
unlogged application memory durable. Neither paper turns backup, replication,
or disaster recovery into automatic consequences of a local commit.

The Linux manual documents current Linux interface behavior, not the original
history of `fsync`, a portable guarantee for every filesystem and device, or a
distributed durability contract. A successful synchronization call relies on
the lower storage stack's reported completion and does not by itself establish
replication, backup, application-level consistency, or a durable job-lifecycle
record.

## Development

The sources permit this bounded comparison; chronology alone does not show
that each document caused the next:

```text
1979: construct stable state from failure-prone storage under explicit assumptions
  -> 1983: make post-commit survival a named transaction property and recovery obligation
  -> 1992: realize transaction recovery through a detailed write-ahead-logging method
  -> 2026: expose a concrete file synchronization boundary and its directory caveat
```

Across the comparison, durability moves from an ideal storage abstraction, to
a transaction-level promise, to a recovery algorithm, and finally to an
application-visible operating-system operation. The layers remain distinct:
calling a write function is not a transaction commit, a commit is not a
backup, and a synchronized local file is not automatically a replicated
service state.

## Modern boundary

For this repository's systems teaching, **volatile state** is state that does
not survive the declared failure boundary, while **durable state** is state
recoverable after that boundary under an explicit storage and commit contract.
The terms are relative to a failure model: process crash, machine restart,
device loss, node loss, regional loss, and deletion are different boundaries.

Durability also remains separate from authority and rebuildability. A disk
cache can be durable but non-authoritative; a committed database record can be
durable and authoritative; a process-local result can be correct but volatile.
Diagnosis must identify the state, its commit point, its recovery path, and the
failures the concrete contract actually covers.

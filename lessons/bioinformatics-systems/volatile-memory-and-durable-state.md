# Volatile memory and durable state

## Place in the systems map

This lesson follows program, process, and service:

```text
program instructions
  -> process execution
  -> volatile runtime state
  -> storage operation
  -> durable state under an explicit failure model
  -> service recovery
```

A process can compute a correct result without making that result recoverable.
The boundary matters before studying files, databases, transactions, queues,
caches, retries, or distributed recovery.

## One documented historical increment

In 1979, Butler Lampson and Howard Sturgis described crash recovery for a data
storage system built from independent computers. Their report states that a
crash can lose information held immediately before the crash and can leave
permanently stored information inconsistent. It then constructs an idealized
`stable storage` abstraction from disk pages, redundancy, checked writes, and
post-crash cleanup under explicitly stated assumptions.

[The report](https://bwlampson.site/21-CrashRecovery/WebPage.html) supports
that bounded construction. It does not establish an infallible physical
medium, protection against every disaster, or global priority for the idea.
Later transaction-recovery and file-synchronization boundaries are recorded in
[the linked history dossier](../../histories/volatile-memory-and-durable-state-history.md).

## Modern working model

Volatile and durable describe behavior across a specified failure boundary:

| State | Example | Survives process crash? | Survives machine crash? |
| --- | --- | --- | --- |
| Process-local volatile state | stack, heap object, in-process cache | No | No |
| Kernel-managed dirty state | modified page-cache data not yet synchronized | Often | Not guaranteed |
| Committed local durable state | database commit or synchronized file under its stated contract | Expected | Depends on the storage contract |
| Replicated or backed-up state | committed replicas or verified backup | Usually | Depends on replica placement and recovery contract |

`Durable` never means immortal. A local disk contract may cover process and
machine restart while excluding device loss. Replication may cover one device
or node while excluding a shared region failure. Backups may cover deletion
while losing changes after the last completed backup.

## State crosses several boundaries

For a file, the path from a process variable to recoverable storage may be:

```text
application object
  -> language runtime buffer
  -> operating-system page cache
  -> storage-device cache
  -> persistent medium
```

`write`, `flush`, `fsync`, transaction `COMMIT`, and replica acknowledgement
are different contracts. None should be promoted to the next boundary without
evidence from the concrete runtime and storage system.

On current Linux, `fsync` is documented to transfer modified in-core file data
and metadata to the storage device and block until the device reports
completion. The same documentation warns that synchronizing a file does not
necessarily synchronize the directory entry that names it; durable file
publication may also require synchronizing the directory.

## Durable result and durable lifecycle are separate

A scientific worker can persist a result artifact while leaving its job state
only in memory:

```text
/results/J-7.json  -> durable artifact
jobs["J-7"]        -> volatile in-process status
```

After a crash, the result may remain while the lifecycle store says nothing.
The absence of a durable success record does not prove that computation failed,
and an unvalidated file does not by itself prove that the job contract
completed. Recovery must reconcile stable identities, result integrity,
version information, and authoritative lifecycle state.

## Durability and source-of-truth answer different questions

```text
volatile / durable
  asks: does the state survive the declared failure boundary?

cache / source of truth
  asks: is this state authoritative, or can it be rebuilt from another source?
```

A disk cache can be durable but non-authoritative. A process-local variable can
be authoritative for an unfinished computation yet volatile. A committed
database row can be both durable and authoritative within its contract.

## Transfer check

A worker computes `count = 428`, writes a complete result to a temporary file,
synchronizes the file, atomically renames it to `/results/J-7.json`, and
synchronizes the containing directory. It then records `jobs["J-7"] =
"success"` only in process memory and is killed before updating the job
database.

Classify the result value, published result artifact, and job success state by
their durability boundary. Can a replacement worker immediately declare the
whole job successful, or what evidence must it reconcile first?

# Modern Scientific Systems Map

This map is the first pass through the track. It establishes the whole system
before any topic is studied in depth. SeqEvi is one later realization of the
map, not the vocabulary used to define it.

## The whole path

```text
real-world input
  -> representation and identity
  -> orchestration and computation
  -> state and storage
  -> result interface and consumption
  -> observation, recovery, and evolution
```

Every arrow is governed by an explicit boundary. Every layer is evaluated
against cross-cutting concerns:

```text
correctness | performance | security | reproducibility | operability | change
```

These qualities are system-wide axes, not isolated layers. A measurable
quality objective needs a metric, target, scope, and observation window:

```text
for <scope>, measured over <window>, <metric> shall meet <target>
```

Different qualities require separate objectives. Low latency does not prove a
high success rate; a well-structured error remains a failed operation even when
it improves the interface and diagnosis experience.

## Three flows through the same system

The path can be inspected from three simultaneous views:

```text
data flow     what information moves and how it is transformed
control flow  who decides which step runs next
state flow    which facts become durable and committed
```

These are not three mutually exclusive components. One event can advance one
flow while another remains incomplete. A computation may produce correct data
in memory, control may fail before delivery, and no durable state may be
committed.

Observer knowledge is separate again. If a result is durably committed but the
success response is lost, the authoritative state says success while the
caller sees a timeout. The real outcome is successful; the outcome is unknown
to that caller until it performs an authoritative readback.

```text
observed timeout != proven operation failure
```

## Seven questions that locate a problem

### 1. Domain meaning

What real-world or scientific claim does the system handle? What is observed,
what is inferred, and what remains uncertain?

Examples: a protein sequence is input content; an alignment is computed
evidence; a functional label is an interpretation rather than a direct fact.

### 2. Data and identity

How is information represented, compared, named, versioned, and linked? Which
identifier denotes content, and which labels belong only to a request or user?

Underlying ideas include bytes, records, canonicalization, hashes, schemas,
keys, provenance, and lineage.

### 3. Computation and execution

What transformation is performed, where does it run, and what resources does
it consume? Does the caller block, wait asynchronously, run work concurrently,
or execute CPU work in parallel?

Underlying ideas include functions, call stacks, processes, threads,
coroutines, event loops, subprocesses, batching, queues, and cancellation.

### 4. State and storage

What must survive, what is authoritative, what is derived, and what is safe to
discard? How are multiple related changes committed or recovered?

Underlying ideas include memory, files, databases, caches, materialized
results, transactions, indexes, atomicity, durability, and recovery.

### 5. Interfaces and contracts

How do components communicate without depending on each other's internal
implementation? Which inputs, outputs, errors, side effects, and compatibility
rules are public?

Underlying ideas include functions, APIs, schemas, adapters, protocols,
serialization, invariants, versioning, and deep modules.

## Contract taxonomy

A contract is the set of observable promises made at a boundary. It is not
limited to an API specification or schema file. One boundary usually carries
several contract families at the same time:

| Contract family | Question it answers |
| --- | --- |
| Domain or semantic | What does the input or result mean, and what claims are valid? |
| Data or schema | What fields, types, units, nulls, and structural relationships are allowed? |
| Identity or equivalence | When are two inputs, requests, resources, or results considered the same? |
| Execution or lifecycle | How does work start, complete, fail, time out, cancel, and report status? |
| State or transaction | What changes, what becomes durable, and which changes are atomic or repeatable? |
| Security or authority | Who may invoke, read, modify, delegate, or cross a tenant boundary? |
| Service or quality | What latency, throughput, availability, capacity, or accuracy is promised? |
| Compatibility or evolution | Which versions interoperate, and how do migration and retirement work? |

These families are not mutually exclusive layers. For example, one upload API
can have a JSON schema contract, a scientific validation contract, a request
identity contract, an authorization contract, an asynchronous lifecycle
contract, and a latency service objective.

## Anatomy of one boundary contract

For any concrete boundary, inspect the same facets:

```text
preconditions    what the caller must supply
postconditions   what success guarantees
errors           how failure is represented
state effects    what may change or become durable
identity         how requests and results are correlated or deduplicated
authority        who is allowed to perform or observe the action
lifecycle        timeout, cancellation, retry, and completion behavior
quality          measurable latency, capacity, accuracy, or availability
evolution        versioning and compatibility rules
```

Not every boundary needs a strong promise for every facet. Unspecified facets
remain risks or implementation details; they should not be silently assumed by
callers.

### 6. Concurrency and failure

What changes when two actors operate at once, a process dies halfway, a network
reply is lost, or an operation is repeated? Which state is safe to retry?

Underlying ideas include races, locks, optimistic concurrency, idempotency,
claims, leases, fencing, timeouts, backpressure, and partial failure.

### 7. Operations and evolution

How is the system deployed, observed, secured, upgraded, and diagnosed in the
real environment? How can it change without corrupting old data or clients?

Underlying ideas include processes, containers, permissions, networks,
authentication, logs, metrics, traces, migrations, compatibility, and rollback.

## Modern mechanisms are combinations, not isolated vocabulary

Common technologies sit at intersections of the map:

```text
cache       = identity + derived state + performance + invalidation policy
SQL         = relational data model + constraints + queries + transactions
async       = execution scheduling + waiting + cancellation + backpressure
adapter     = interface contract + translation + validation + ownership
queue       = durable handoff + concurrency control + retry semantics
container   = execution environment + identity + isolation + deployment
```

Learning one mechanism therefore starts by locating its dependencies on this
map, not by memorizing its API.

## Frequent category errors

```text
identifier        is not necessarily content identity
process success   is not scientific correctness
cache             is not the source of truth
async             is not automatically parallel
same column type  is not the same field meaning
retry             is not safe without idempotency or deduplication
schema validity   is not domain validity
caller knowledge  is not necessarily authoritative state
```

These distinctions are recurring design tools, not SeqEvi-specific rules.

## Spiral learning order

### Pass 1: orientation

Explain the seven questions and trace one generic request through the complete
path. No product table names or implementation contracts are required.

### Pass 2: foundations

Build the minimum model of data representation, program execution, memory,
files, databases, networks, and failure needed to understand the path.

### Pass 3: modern mechanisms

Study cache, SQL, async execution, queues, transactions, concurrency control,
APIs, containers, observability, and evolution with minimal examples and
tradeoffs.

### Pass 4: integrated case

Map the complete model onto SeqEvi: sequence identity, evidence computation,
adapters, Store, result delivery, concurrency, and deployment. Repository
details appear here because the general questions already exist.

### Pass 5: transfer

Apply the same map to a different scientific or data system. Mastery requires
reconstructing the design without SeqEvi names.

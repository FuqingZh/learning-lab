# Cache, source of truth, and materialized results

## Classify by authority, not technology

A storage technology does not determine its role. Redis can hold authoritative
state, PostgreSQL can hold a disposable cache, and a file can be either a raw
source or a derived result.

Ask two questions:

1. Can the value be reconstructed correctly from independently retained
   authoritative inputs and a defined computation?
2. What contract is broken if this copy disappears: performance, correctness,
   or delivery?

## Cache

A cache is a derived, disposable copy used primarily to reduce latency, load,
or repeated computation.

```text
delete cache
  -> cache miss
  -> fetch or recompute from authority
  -> same correct result, but slower or more expensive
```

Deletion may cause operational pressure, but system correctness must not rely
on the cache being the only surviving copy.

## Source of truth

A source of truth owns authoritative information. If it is deleted without an
independent authoritative replica or recovery mechanism, information is lost
and correct reconstruction is impossible.

Calling the only copy a cache does not make it disposable. A user-authored
document stored only in Redis is authoritative state, regardless of the
component name.

## Materialized result

A materialized result is a persisted derived value with defined lineage. For
example, a monthly summary may be reconstructed from an immutable transaction
ledger and versioned SQL.

Its deletion need not destroy the underlying truth, but it may violate a
delivery, availability, audit, or reproducibility contract until rebuilt. It is
therefore not necessarily a freely disposable performance cache.

The same artifact may also accelerate reads, but roles should be described by
the strongest responsibility it carries. A required published report does not
become a mere cache because recomputation is theoretically possible.

## Rebuildability is a contract

Claiming that a value is rebuildable requires more than retaining raw inputs.
The system may also need:

- input identity and content;
- computation or code version;
- result-affecting parameters and defaults;
- external resource or database versions;
- environment dependencies;
- lineage linking the result to all of the above.

If these dependencies are unavailable, a nominally derived cache may have
silently become the only authoritative copy of the result.

## Review rule

Do not ask whether a component is called a cache. Ask:

```text
What is authoritative?
What is derivable?
What is disposable?
What breaks when it disappears?
```

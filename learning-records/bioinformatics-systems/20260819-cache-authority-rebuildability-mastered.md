# Cache authority and rebuildability are understood

The learner can classify storage roles by authority, rebuildability, and the
effect of deletion rather than by storage technology or persistence.

```text
cache               deletion primarily affects performance
source of truth     deletion destroys authoritative information and correctness
materialized result deletion affects delivery or availability but can preserve truth
```

The learner understands that a so-called cache containing the only surviving
copy is actually carrying source-of-truth responsibility, and that a durable
derived result may be rebuildable while still belonging to a delivery or audit
contract rather than being freely disposable.

## Evidence

In unaided application on 2026-08-19, the learner correctly classified:

- a short-lived Redis copy of a retrievable weather API response as cache, with
  deletion causing a performance cost;
- a user document stored only in Redis as the source of truth despite its
  misleading cache label, with deletion breaking correctness; and
- a monthly summary derived from immutable transaction records and versioned
  SQL as a materialized result, with deletion disrupting delivery while
  leaving the underlying facts reconstructable.

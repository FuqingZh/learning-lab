# Contract taxonomy and idempotency boundaries are understood

The learner can classify observable boundary promises as schema, identity,
execution/lifecycle, state/transaction, security/authority, service/quality,
or compatibility/evolution concerns without inferring unrelated contracts from
the business name of the data.

The learner also distinguishes a contract violation from the quality it harms,
and separates request identity, idempotent logical effects, and physical
compute deduplication.

## Evidence

In unaided application on 2026-08-20, the learner correctly classified:

- integer field requirements as schema;
- access restricted to a creator or billing service as security/authority;
- all-or-nothing task and fee writes as state/transaction atomicity;
- old-client support as compatibility/evolution; and
- latency percentiles as service/quality promises.

After refinement, the learner explained that a request ID does not constrain
execution by itself and correctly judged a two-worker scenario as idempotent
but not compute-deduplicated: both workers performed the expensive work, one
logical result committed, correctness was preserved, and performance was
wasted.

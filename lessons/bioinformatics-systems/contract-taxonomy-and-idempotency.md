# Contract taxonomy and idempotency

## Contract means observable promise

A contract is the set of observable promises at a boundary. It is not limited
to an API document, type signature, or schema file. One boundary can carry
several contract families at once:

| Family | Promise |
| --- | --- |
| Domain/semantic | Meaning and valid claims |
| Data/schema | Fields, types, units, nulls, and structure |
| Identity/equivalence | When requests, inputs, or results count as the same |
| Execution/lifecycle | Start, status, completion, failure, timeout, and cancel |
| State/transaction | Durable changes, transitions, atomicity, and repetition |
| Security/authority | Who may invoke, read, modify, or delegate |
| Service/quality | Latency, throughput, availability, capacity, or accuracy |
| Compatibility/evolution | Version interoperability, migration, and retirement |

Not every scenario provides evidence about every family. An unspecified
security or compatibility rule is not automatically satisfied or violated; it
is simply outside the available claim.

## Cause and system impact

The violated contract is the cause. A cross-cutting quality describes the
system-level impact.

```text
false identity equivalence -> correctness and reproducibility damage
authorization bypass       -> security damage
latency SLO miss            -> performance damage
```

Correctness does not necessarily fail when a latency promise fails, and a
performance improvement does not excuse an incorrect result.

## Classify the promise, not the business noun

The same fee record can participate in several different contracts:

```text
fee must be decimal                  schema
fee follows the pricing rule         domain/semantic
only billing service may write       security/authority
task and fee commit together         state/transaction atomicity
same request must not charge twice   identity + state/idempotency
```

The fact that data represents money does not make every rule a security rule.

## Identity is necessary but not sufficient for idempotency

A stable request ID provides a coordinate for recognizing one logical
operation. If the system never checks, constrains, or records that identity,
retries can still create duplicate effects.

Idempotency requires a state rule such as an atomic idempotency record, a
uniqueness constraint, or an equivalent compare-and-commit mechanism:

```text
same logical request repeated -> no additional logical effect
```

## Idempotency is not compute deduplication

Two workers may both perform expensive computation for the same request while
a uniqueness constraint permits only one result to commit. In that case:

```text
idempotency          yes: one committed logical effect
compute deduplication no: work occurred twice
correctness          preserved
performance          degraded
```

At-most-one physical execution is a stronger and different goal. Systems often
protect correctness with idempotent commit even when they cannot prevent every
duplicate computation.

## Boundary review

For a concrete operation, ask:

1. Which contract family owns the promise?
2. What precondition, postcondition, error, and state effect are observable?
3. Which stable identity correlates retries and results?
4. What enforces authority and idempotent state change?
5. Which cross-cutting quality is harmed if the promise fails?

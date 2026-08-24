# Cross-cutting quality objectives are understood

The learner can turn a vague quality claim into a measurable objective using
metric, target, scope, and observation window. The learner understands that
correctness, performance, reliability, security, reproducibility, operability,
and evolvability are independent system-wide axes rather than interchangeable
labels or isolated components.

## Evidence

In unaided application completed on 2026-08-21, the learner:

- decomposed a p99 latency objective into its request-size and load scope,
  seven-day window, latency metric, and 800 ms target;
- correctly judged that a system can satisfy latency performance while failing
  reliability through fast internal errors;
- excluded invalid-input 400 responses from a metric explicitly scoped to
  valid requests and counted structured 500 responses as failures;
- distinguished a structured error interface from a durable failed lifecycle
  state and from a real reduction in failure rate; and
- mapped those changes respectively to interface, state/lifecycle, and
  reliability improvements.

The learner therefore treats a quality claim as a measured vector of promises,
not a single assertion that a system is good.

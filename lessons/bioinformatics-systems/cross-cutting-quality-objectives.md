# Cross-cutting quality objectives

## Qualities cross every layer

Layers divide responsibility vertically. Cross-cutting qualities evaluate how
well the complete path behaves:

```text
correctness       result and state satisfy their meaning
performance       latency, throughput, and resource use
reliability       valid operations succeed consistently
security          authority, confidentiality, and integrity hold
reproducibility   exact conditions can reconstruct and audit results
operability       deployment, observation, diagnosis, and recovery work
evolvability      versions and state can change safely
```

A system can be fast but unreliable, correct but slow, secure but hard to
operate, or reproducible but incompatible with a new client. No one metric
proves overall system quality.

## From aspiration to objective

Statements such as “fast” or “reliable” are aspirations. A verifiable quality
objective requires:

```text
metric  what is measured
target  the acceptable bound
scope   eligible inputs, callers, workload, and conditions
window  the observation period
```

A reusable form is:

```text
For <scope>, measured over <window>, <metric> shall meet <target>.
```

Example:

```text
For valid files no larger than 20 MB at no more than 50 requests per second,
measured over a rolling seven-day window,
p99 request latency shall be no greater than 800 ms.
```

This is a performance objective only. It does not establish reliability.

## Scope determines the population

A success-rate metric for valid requests can exclude correctly rejected
invalid input. A valid request that reaches an internal 500 response remains a
reliability failure even when the response is fast and well structured.

Metric definitions must therefore specify which requests enter the numerator
and denominator. Otherwise teams can improve a number by silently changing the
population rather than improving the system.

## Error representation and actual success

```text
structured error response     improves interface/error contract
request ID linked to logs      improves operability/observability
durable terminal failed state  improves lifecycle/state visibility
fewer valid-request failures   improves reliability
```

A structured 500 is an expression of failure, not a successful request. Error
packaging can make failure usable and diagnosable without changing the failure
rate.

## Tradeoffs need guardrails

Optimizing one quality can damage another. Caching may reduce latency while
returning stale data; stricter validation may add latency while protecting
correctness; retries may improve completion rate while duplicating side
effects; encryption may consume resources while protecting security.

An optimization is acceptable only when the system measures its target quality
and preserves explicit guardrails for the others.

## Review questions

1. Which quality is being claimed?
2. What metric, target, scope, and window make the claim testable?
3. Which other qualities could the change damage?
4. Are fast or well-formed failures incorrectly counted as success?
5. Does the metric population match the real contract population?

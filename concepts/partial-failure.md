---
id: partial-failure
title: Partial failure
summary: A distributed operation can have some effects occur while another participant cannot determine the final outcome.
kind: foundation
terminology:
  preferred_english_term: Partial failure
  checked_on: "2026-08-21"
  sources:
    - url: https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/rel_mitigate_interaction_failure_graceful_degradation.html
      publisher: Amazon Web Services
      kind: professional-documentation
    - url: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/implement-resilient-applications/handle-partial-failure
      publisher: Microsoft
      kind: professional-documentation
tracks:
  - scientific-ai-platforms
  - bioinformatics-systems
case_labs: []
prerequisites: []
enables: []
contrasts_with: []
related: []
lessons: []
records: []
---

A lost response, timeout, or process interruption does not by itself prove
that the underlying operation did not commit. This uncertainty is the reason a
caller needs evidence before retrying an operation with durable effects.

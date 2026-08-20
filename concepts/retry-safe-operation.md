---
id: retry-safe-operation
title: Retry-safe operation
summary: An operation that can be attempted again after an uncertain response without duplicating its intended side effects.
kind: pattern
tracks:
  - scientific-ai-platforms
  - bioinformatics-systems
case_labs: []
prerequisites:
  - "[[concepts/idempotency]]"
  - "[[concepts/partial-failure]]"
  - "[[concepts/side-effect]]"
enables: []
contrasts_with: []
related: []
lessons: []
records:
  - learning-records/scientific-ai-platforms/0016-idempotency-foundations-mastered.md
---

Retry safety is not guaranteed success or proof that a request was executed
only once. A retry follows only after the uncertain outcome has been resolved
or the operation is known to be safely repeatable.

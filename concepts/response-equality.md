---
id: response-equality
title: Response equality
summary: The property that repeated attempts return identical response representations.
kind: boundary
tracks:
  - scientific-ai-platforms
case_labs: []
prerequisites: []
enables: []
contrasts_with: []
related: []
lessons: []
records:
  - learning-records/scientific-ai-platforms/0016-idempotency-foundations-mastered.md
---

Equal response bytes do not prove that an operation avoided duplicate durable
effects. Conversely, an idempotent operation can produce different responses
while preserving the same intended final effect.

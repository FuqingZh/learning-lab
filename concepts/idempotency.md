---
id: idempotency
title: Idempotency
summary: Repeating one logical operation preserves its intended final effect.
kind: foundation
tracks:
  - scientific-ai-platforms
case_labs: []
prerequisites:
  - "[[concepts/logical-operation]]"
  - "[[concepts/partial-failure]]"
  - "[[concepts/side-effect]]"
enables: []
contrasts_with:
  - "[[concepts/response-equality]]"
related:
  - "[[concepts/operation-scope]]"
lessons: []
records:
  - learning-records/scientific-ai-platforms/0016-idempotency-foundations-mastered.md
---

Idempotency concerns the intended final effect, not identical response bytes,
exactly-once delivery, or guaranteed success. It makes recovery from uncertain
attempts reasoned rather than blind.

---
id: idempotency-key
title: Idempotency key
summary: A stable identifier retained across attempts for one scoped logical operation.
kind: pattern
tracks:
  - scientific-ai-platforms
case_labs: []
prerequisites:
  - "[[concepts/logical-operation]]"
  - "[[concepts/operation-scope]]"
enables:
  - "[[concepts/idempotency]]"
  - "[[concepts/retry-safe-operation]]"
contrasts_with: []
related: []
lessons: []
records:
  - learning-records/scientific-ai-platforms/0016-idempotency-foundations-mastered.md
---

The key is reused after an uncertain attempt for the same scoped operation. A
genuinely new operation needs a new key, and a changed payload under the same
scoped key is a caller conflict rather than a valid retry.

---
id: operation-scope
title: Operation scope
summary: The operation type or namespace within which an idempotency key identifies one logical operation.
kind: boundary
tracks:
  - scientific-ai-platforms
case_labs: []
prerequisites:
  - "[[concepts/logical-operation]]"
enables: []
contrasts_with: []
related: []
lessons: []
records:
  - learning-records/scientific-ai-platforms/0016-idempotency-foundations-mastered.md
---

The same key string in different scopes does not identify the same operation.
Scope is part of the operation identity, not merely a workflow-stage label.

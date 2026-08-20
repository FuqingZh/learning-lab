---
id: logical-operation
title: Logical operation
summary: The user-intended unit of work, which can require more than one transport request or execution attempt.
kind: foundation
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

A logical operation is not the same thing as one HTTP request. For example,
creating one Job remains one logical operation when the caller must retry after
losing the response.

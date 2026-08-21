---
id: idempotency
title: Idempotency
summary: Repeating one logical operation preserves its intended final effect.
kind: foundation
terminology:
  preferred_english_term: Idempotency
  checked_on: "2026-08-21"
  sources:
    - url: https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2
      publisher: Internet Engineering Task Force
      kind: standard
    - url: https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/
      publisher: Amazon Web Services
      kind: professional-documentation
tracks:
  - scientific-ai-platforms
case_labs: []
prerequisites:
  - "[[concepts/partial-failure]]"
  - "[[concepts/side-effect]]"
enables: []
contrasts_with: []
related: []
lessons: []
records:
  - learning-records/scientific-ai-platforms/0016-idempotency-foundations-mastered.md
---

Idempotency concerns the intended final effect, not identical response bytes,
exactly-once delivery, or guaranteed success. It is the property that can make
a repeat attempt safe after an uncertain result, provided the attempt still
represents the same intended unit of work.

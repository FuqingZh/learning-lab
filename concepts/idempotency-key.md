---
id: idempotency-key
title: Idempotency key
summary: A stable identifier retained across attempts for one scoped logical operation.
kind: pattern
terminology:
  preferred_english_term: Idempotency key
  checked_on: "2026-08-21"
  sources:
    - url: https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/
      publisher: Internet Engineering Task Force
      kind: standard
    - url: https://docs.stripe.com/api/idempotent_requests
      publisher: Stripe
      kind: professional-documentation
tracks:
  - scientific-ai-platforms
case_labs: []
prerequisites:
  - "[[concepts/idempotency]]"
enables: []
contrasts_with: []
related: []
lessons: []
records:
  - learning-records/scientific-ai-platforms/0016-idempotency-foundations-mastered.md
---

The key is reused after an uncertain attempt for the same intended operation.
Its meaning is limited to the API operation or namespace that defines it, so a
genuinely new operation needs a new key. A changed payload under the same key
is a caller conflict rather than a valid retry.

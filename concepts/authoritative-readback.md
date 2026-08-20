---
id: authoritative-readback
title: Authoritative readback
summary: Recovering an uncertain operation by checking durable authoritative state through its stable identity.
kind: mechanism
tracks:
  - bioinformatics-systems
  - scientific-ai-platforms
case_labs: []
prerequisites:
  - "[[concepts/logical-operation]]"
  - "[[concepts/partial-failure]]"
enables:
  - "[[concepts/retry-safe-operation]]"
contrasts_with: []
related:
  - "[[concepts/idempotency]]"
lessons:
  - lessons/bioinformatics-systems/system-success-flows-and-ambiguous-outcomes.md
records:
  - learning-records/bioinformatics-systems/20260819-system-success-flow-boundaries-mastered.md
---

When a result may have committed before a response was lost, query the
authoritative state using the stable request or Job identity. The readback
separates durable system state from what the caller happened to observe.

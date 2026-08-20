---
id: partial-failure
title: Partial failure
summary: A distributed operation can have some effects occur while another participant cannot determine the final outcome.
kind: foundation
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

---
id: side-effect
title: Side effect
summary: An observable change to execution or its environment caused by evaluation or an operation.
kind: foundation
terminology:
  preferred_english_term: Side effect
  checked_on: "2026-08-21"
  sources:
    - url: https://docs.oracle.com/javase/specs/jls/se7/html/jls-15.html#jls-15.1
      publisher: Oracle
      kind: standard
    - url: https://www.gnu.org/software/c-intro-and-ref/manual/html_node/Side-Effects.html
      publisher: GNU Project
      kind: professional-documentation
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

Assignments, increment operations, and method or function calls can have side
effects: observable changes beyond an expression's resulting value. In a
system, creating a Job, updating a database record, consuming quota, or
writing a result file are side effects. A returned identifier alone is not an
effect, although producing it can accompany one.

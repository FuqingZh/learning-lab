---
id: service
title: Service
summary: A capability made available to consumers through a prescribed interface and its stated constraints.
kind: foundation
terminology:
  preferred_english_term: Service
  checked_on: "2026-08-24"
  sources:
    - url: https://docs.oasis-open.org/soa-rm/v1.0/soa-rm.html#section3.1
      publisher: OASIS Open
      kind: standard
    - url: https://www.w3.org/TR/ws-arch/#whatis
      publisher: World Wide Web Consortium
      kind: standard
tracks:
  - bioinformatics-systems
case_labs: []
prerequisites: []
enables: []
contrasts_with: []
related:
  - "[[concepts/process]]"
lessons:
  - lessons/bioinformatics-systems/program-process-and-service.md
records: []
---

A service is identified by what it makes available at its interface, rather
than by a particular runtime instance. In software systems it is commonly
realized by one or more processes, which may be replaced without changing the
service's exposed capability or contract. Platform-specific service managers
may also use *service* for a managed unit, so that label alone does not prove a
one-process implementation.

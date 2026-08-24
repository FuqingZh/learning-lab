---
id: process
title: Process
summary: An executing program together with the operating-system resources that support its execution.
kind: foundation
terminology:
  preferred_english_term: Process
  checked_on: "2026-08-24"
  sources:
    - url: https://learn.microsoft.com/en-us/windows/win32/procthread/processes-and-threads
      publisher: Microsoft
      kind: professional-documentation
    - url: https://man7.org/linux/man-pages/man2/fork.2.html
      publisher: Linux man-pages project
      kind: professional-documentation
tracks:
  - bioinformatics-systems
case_labs: []
prerequisites:
  - "[[concepts/program]]"
enables: []
contrasts_with: []
related: []
lessons:
  - lessons/bioinformatics-systems/program-process-and-service.md
records: []
---

A process is a runtime instance, not the prepared program artifact. Operating
systems attach resources such as an address space, threads, handles, and
credentials according to their platform model; identifiers and exact resource
sets therefore vary by platform and lifetime. Multiple processes can execute
the same program independently.

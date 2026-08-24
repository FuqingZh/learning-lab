---
schema_version: 2
id: program-process-and-service-history
title: Development of program, process, and service boundaries
summary: Documents selected steps that separate instructions, executing processes, process communication, and an abstract service from its realizing agent without asserting one direct lineage.
concepts: []
lessons:
  - lessons/bioinformatics-systems/program-process-and-service.md
tracks:
  - bioinformatics-systems
milestones:
  - id: dijkstra-ewd123-1965
    year: 1965
    month: null
    day: null
    kind: formalization
    actors:
      - Edsger W. Dijkstra
    claim: Dijkstra's EWD123 distinguishes a program as rules of behavior from a sequential process as what happens during execution, then analyzes cooperation among independently progressing processes.
    subjects:
      - process
      - program
    boundaries:
      - Does not establish a service concept.
      - Does not establish global priority for the program and process distinction.
    evidence_basis: primary-source
    sources:
      - url: https://www.cs.utexas.edu/~EWD/transcriptions/EWD01xx/EWD123.html
        locator: Section 1, paragraphs beginning "The technical term"; section 2, opening cooperation paragraphs.
        title: Cooperating Sequential Processes
        publisher: E. W. Dijkstra Archive
        role: primary
        kind: archive
      - url: https://www.cs.utexas.edu/~EWD/transcriptions/EWD10xx/EWD1000.html
        locator: Paragraph beginning "EWD123", stating that it was written in 1965 for that year's fall course.
        title: Twenty-eight years
        publisher: E. W. Dijkstra Archive
        role: primary
        kind: archive
  - id: unix-fork-execute-1974
    year: 1974
    month: 7
    day: null
    kind: adoption
    actors:
      - Dennis M. Ritchie
      - Ken Thompson
    claim: The 1974 UNIX paper documents fork creating a child process whose code initially remains the shell's, followed by execute bringing in and starting the named program.
    subjects:
      - process
      - program
    boundaries:
      - Documents the UNIX interface rather than all modern process semantics.
    evidence_basis: primary-source
    sources:
      - url: https://doi.org/10.1145/361011.361061
        locator: Section 5.1 "Processes" and 5.3 "Execution of Programs", page 370; section 6.5 "Implementation of the Shell", page 372.
        title: The UNIX Time-Sharing System
        publisher: Communications of the ACM
        role: primary
        kind: paper
  - id: tcp-process-service-1981
    year: 1981
    month: 9
    day: null
    kind: adoption
    actors:
      - Jon Postel
    claim: RFC 793 specifies TCP as a reliable process-to-process communication service and defines interfaces between application processes, TCP, and lower-level protocols.
    subjects:
      - process
      - service
    boundaries:
      - Does not establish every current use of service.
    evidence_basis: primary-source
    sources:
      - url: https://www.rfc-editor.org/rfc/rfc793.html#section-1.2
        locator: Section 1.2 "Scope"; sections 2.1–2.2 "Elements" and "Model of Operation".
        title: RFC 793 - Transmission Control Protocol
        publisher: Internet Engineering Task Force
        role: primary
        kind: standard
  - id: w3c-agent-service-2004
    year: 2004
    month: 2
    day: 11
    kind: formalization
    actors:
      - Web Services Architecture Working Group
    claim: The 2004 W3C Web Services Architecture distinguishes an abstract Web service from the concrete agent that implements it and states that the agent may change while the same service remains.
    subjects:
      - service
    boundaries:
      - Applies to Web services and does not define every software service.
    evidence_basis: primary-source
    sources:
      - url: https://www.w3.org/TR/2004/NOTE-ws-arch-20040211/
        locator: Section 1.4.1 "Agents and Services"; section 2.3.2.10 "Service".
        title: Web Services Architecture
        publisher: World Wide Web Consortium
        role: primary
        kind: professional-documentation
---

## Historical setting

This dossier follows selected documents that make different abstraction
boundaries explicit. It is not a claim that `program`, `process`, and `service`
were invented together or developed along one continuous causal line. The
documents address different problems: reasoning about sequential execution,
operating-system process creation, inter-process communication, and Web-service
architecture.

## What the sources establish

In [EWD123](https://www.cs.utexas.edu/~EWD/transcriptions/EWD01xx/EWD123.html),
Dijkstra calls rules of behavior an algorithm or program and calls what happens
during execution a sequential process. He then discusses independently
progressing processes that must communicate when they cooperate.

The 1974
[UNIX paper](https://doi.org/10.1145/361011.361061) makes a related distinction
operational. Its shell calls `fork` to create a child process; that child
initially has the shell's code, and `execute` then loads and starts a named
program. The paper therefore documents that the process and the program it
executes are not the same identity.

[RFC 793](https://www.rfc-editor.org/rfc/rfc793.html#section-1.2) describes TCP
as a reliable process-to-process communication service. It defines interfaces
between application processes, TCP, and lower-level protocols while allowing
implementation freedom behind the required functionality.

The 2004
[W3C Web Services Architecture](https://www.w3.org/TR/2004/NOTE-ws-arch-20040211/)
explicitly distinguishes a Web service from the concrete agent that realizes
it. It says an agent may change while the service remains the same and permits
one service to be realized by multiple agents.

## What the sources do not establish

EWD123 does not establish global priority for the program/process distinction,
and its sequential process is not identical to every later operating-system
process model. The UNIX paper documents its own process interface rather than
all modern process semantics. RFC 793's communication service is not evidence
for every current use of `service`, including service-manager units or
microservices. The W3C document is a Working Group Note about Web services,
not a universal standard definition of all software services.

The dates alone do not establish that one document caused the next. No source
in this dossier establishes a single inventor, one origin event, or a direct
line from Dijkstra's terminology through UNIX and TCP to the W3C architecture.

## Development

The sources support a bounded comparison rather than a causal origin story:

```text
1965: rules or program != the process occurring during execution
  -> 1974: a UNIX process can be created, then made to execute a named program
  -> 1981: application processes consume a communication service through an interface
  -> 2004: an abstract Web service can remain while its realizing agent changes
```

Across these documents, attention moves from instructions and execution, to
runtime lifecycle, to communication across processes, and finally to a
capability whose identity is explicitly separated from its implementation
agent. This comparison is useful even though the four documents do not define
one shared formal model.

## Modern boundary

For this repository's modern systems teaching, a **program** is prepared
instructions or an executable artifact, a **process** is one runtime execution
instance with state and resources, and a **service** is a capability exposed
under an interface or operational contract. A program can have many executing
processes, and a service can be realized by different process sets over time.

This working boundary is an engineering synthesis, not a historical claim
attributed to any one source. Concrete platforms may narrow `process` or
`service` differently, so system diagnosis must name the platform, identity,
lifetime, and contract being discussed.

# Scientific AI Systems Knowledge Map

This is a dependency map of transferable knowledge, not a workflow diagram for
Bio Plot Platform. Learning proceeds from foundations, through modern system
synthesis, to repository case labs.

## Level A: foundational disciplines

These disciplines supply the concepts used by every later system.

1. **Computation and information**
   Representation, identity, state, transition, determinism, algorithms,
   complexity, abstraction, and contracts.
2. **Operating systems and runtime**
   Processes, memory, filesystems, users, permissions, scheduling, IPC,
   virtualization, containers, and isolation boundaries.
3. **Data systems**
   Data models, schemas, indexes, transactions, concurrency control,
   durability, immutability, lineage, and databases.
4. **Networks and distributed systems**
   Partial failure, time, ordering, messaging, delivery semantics, consensus,
   replication, retries, idempotency, backpressure, and fault tolerance.
5. **Security and authority**
   Threat models, principals, authentication, authorization, capabilities,
   least privilege, zero trust, confused deputy, secrets, and supply chains.
6. **Probability, statistics, and scientific reasoning**
   Uncertainty, measurement, experimental design, estimation, testing,
   causality, evidence, reproducibility, and the limits of inference.
7. **Machine learning and language models**
   Training versus inference, probabilistic prediction, representation,
   generalization, prompting, context, tool use, evaluation, and model limits.

The important dependency shape is:

```text
computation and information
   |----> operating systems ----> execution isolation
   |----> data systems ---------> durable state
   |----> distributed systems --> reliable coordination
   `----> security -------------> bounded authority

probability and scientific reasoning
   `----> machine learning -----> probabilistic model behavior

all branches
   `----> modern scientific AI systems
```

## Level B: modern system synthesis

These are combinations of foundations rather than isolated technologies.

1. **Cloud-native and multi-tenant platforms**: control planes, schedulers,
   containers, policy, quotas, workload identity, and isolation tradeoffs.
2. **Event-driven and durable execution**: queues, state machines, workflow
   engines, retries, compensating actions, and long-running operations.
3. **Zero-trust and capability-oriented systems**: explicit identity,
   least-privilege resource references, policy enforcement, and removal of
   ambient authority.
4. **Agentic systems**: model proposals, application-owned context, tool
   protocols, capability negotiation, constrained execution, durable tasks,
   and human control.
5. **Evaluation and observability**: traces, structured outcomes, independent
   checks, privacy-aware telemetry, offline evaluation, and production feedback.
6. **Provenance and software supply chains**: artifact identity, attestations,
   dependency resolution, reproducible builds, and verifiable origin.
7. **Scientific AI systems**: semantic data contracts, statistical validity,
   reproducible analysis, provenance, expert acceptance, and claim-scoped
   evidence.

The frontier portion of this level is refreshed against current primary
standards and specifications. Product names are examples of patterns, not the
knowledge map itself.

## Level C: repository case labs

Bio Plot Platform, SeqEvi, bioextract, proteomics, and other repositories are
used only after the relevant general model exists. A case lab asks:

1. Which foundational disciplines does this feature combine?
2. Which modern pattern is it implementing?
3. What invariant or failure model justifies the design?
4. Does the implementation actually satisfy that principle?
5. Can the learner transfer the reasoning to a different system?

Routes, classes, tables, deployment values, and current product workflow are
not the curriculum spine.

## Teaching order

1. Survey the complete Level A dependency map without quizzing every node or
   descending into mechanisms.
2. At a meaningful boundary, invite a map-level explanation or application;
   do not require a quiz merely to close a reply.
3. Study one coherent foundational unit at a time; include all connected
   concepts and historical context required for a complete mental model instead
   of enforcing one-term or one-mechanism turns.
4. Periodically synthesize mastered foundations into one Level B pattern.
5. Use a Level C case after explaining the relevant general model. For a
   beginner, work through a complete example before asking for independent design.

Lessons must be map-first, not detail-first. Their scope follows conceptual
coherence rather than a fixed duration or information quota. Coverage is not mastery; a
capability is established only after unaided use on a fresh case.

## Historical technology spiral

Frameworks and products are neither a second curriculum spine nor material to
postpone until every foundational discipline is complete. They also cannot be
used as unexplained starting points. For a learner without prior web-programming
knowledge, the route first reconstructs the documented problem sequence and
only then introduces the modern mechanism:

```text
documented historical problem
  -> historically documented proposal or formalization
  -> modern implementation-independent boundary
  -> one technology realization
  -> Bio Plot Platform case evidence
  -> transfer to a fresh system
```

The technology name identifies the laboratory; the transferable capability is
the learning target. The beginner route is:

| Sequence | Historical and technical unit | Map location | Learning outcome |
| --- | --- | --- | --- |
| 1 | Linked documents, browser, and server | Networks plus program/process/service | Explain what the early Web proposal meant by browser, server, node, link, and navigation before treating a page as an application. |
| 2 | ECMAScript in a host environment | Computation and information | Understand values, expressions, variables, functions, and a program executed by a browser host before adding static types. |
| 3 | DOM as a programmatic document interface | Representation plus side effects | Distinguish a document representation from programmatic reads and observable document mutation. |
| 4 | TypeScript after JavaScript | Computation and information | Use static types to describe possible JavaScript values and function boundaries while recognizing type erasure and runtime limits. |
| 5 | React after JavaScript and DOM | UI state and computation | Compare imperative DOM updates with components whose render step derives a UI description from inputs. |
| 6 | React state, events, and Effects | UI runtime | Separate state snapshots, event-triggered work, React commit, and synchronization with external systems. |
| 7 | PostgreSQL | Data systems | Model identity and invariants with relations, keys, constraints, and transactions before studying concurrency and durability. |
| 8 | FastAPI | Networks, services, contracts, and authority | Define an HTTP boundary whose runtime validation, authorization, and transaction ownership are explicit. |
| 9 | Vertical slice | Modern system synthesis | Trace one operation from React through FastAPI into PostgreSQL, including identity, failure, commit, and response boundaries. |

This is a dependency order, not a requirement to finish one technology in
isolation. JavaScript is a prerequisite for TypeScript here, and the browser,
document, and DOM models are prerequisites for React. Earlier concepts are
retrieved inside later laboratories: for example, `side-effect` is revisited
in DOM mutation, React render, PostgreSQL mutation, and FastAPI request handling
rather than extended through standalone terminology sessions.

The first technology lesson is
[The Web before JavaScript: document, browser, and server](../../lessons/scientific-ai-platforms/web-document-browser-and-server.md).
It uses the sourced 1990 setting to build the complete document/browser/server
model before JavaScript, TypeScript, React, or repository component APIs.

## Lesson loop for this track

1. Give an advance organizer: map location, historical setting, prior
   capability, unresolved problem, prerequisites, and intended mental model.
2. Teach one coherent framework or capability with enough connected background;
   do not interrupt every term or paragraph with a question.
3. Answer direct questions before asking for evidence.
4. At a natural conceptual boundary, use a mastery check suited to the target:
   retrieval for facts, performance for procedures, or explain-back plus
   transfer and boundary for concepts and designs.
5. If needed, explain the blocking prerequisite with a connected example;
   invite another attempt when useful, without a fixed retry quota.
6. Record mastery only after the lesson-level evidence is sufficient.

## Current pilot: return to the React bridge

The learner's feedback identifies insufficient setup and unexplained syntax.
Earlier systems reasoning and TypeScript answers do not establish React or
JavaScript syntax fluency. Keep previous evidence; do not restart everything
or infer that typed props are the next appropriate task.

The prepared next unit is
[From document updates to React](../../lessons/scientific-ai-platforms/react-from-document-updates.md).
It develops one display-update problem through ordinary JavaScript, DOM access,
and a React description. Object access, function arguments, and conversion are
explained where needed; destructuring, JSX syntax, hooks, and imports are not
assumed. State/event-triggered updates remain the following unit, subject to
the learner's questions and actual evidence. PostgreSQL and FastAPI stay on the
larger route, not inside this introduction.

Detailed position and meaningful branches live in
[navigation](../../learning-state/navigation/README.md), separately from
capability. The pilot is prepared, not taught or accepted. Its success requires
a real learner encounter, not just passing repository checks.

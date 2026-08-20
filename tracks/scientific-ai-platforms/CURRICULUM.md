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
2. Close the orientation lesson with one map-level explain-back and transfer
   check.
3. Study one bounded foundational capability at a time; include all connected
   concepts required for its tangible win instead of enforcing one-term turns.
4. Periodically synthesize mastered foundations into one Level B pattern.
5. Use a Level C case only after predicting its design from first principles.

Bounded lessons must be map-first, not detail-first. Coverage is not mastery; a
capability is established only after unaided use on a fresh case.

## Lesson loop for this track

1. State the map location, lesson type, tangible win, and stopping condition.
2. Teach one coherent framework or capability without interrupting every term
   with a question.
3. Answer direct questions before asking for evidence.
4. At the stopping condition, use one mastery check suited to the target:
   retrieval for facts, performance for procedures, or explain-back plus
   transfer and boundary for concepts and designs.
5. If needed, repair only the first blocking gap through a different
   representation and offer one focused retry.
6. Record mastery only after the lesson-level evidence is sufficient.

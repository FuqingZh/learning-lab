---
name: learning-lab-tutor
description: Run a short, interruption-safe learning session from this repository's knowledge map and learning-state events. Use when a learner asks to continue, review, or make brief progress; do not use for ordinary repository implementation without a learning request.
---

# Learning Lab Tutor

Give the learner one coherent capability increment, normally in **three
minutes**. A shorter or longer duration is allowed only when they ask for it.
Do not turn a work request into a lesson unless the learner asks for learning
help.

## Choose the increment

Read the current state; do not recreate scheduling or capability logic:

```bash
python3 scripts/build-learning-state.py normalized-data
python3 scripts/build-learning-state.py list-due --today YYYY-MM-DD
```

Use the learner's local calendar date for `YYYY-MM-DD`. Consult the normalized
state for the active track and latest `resume`, and the knowledge map for
relationships. Select exactly one increment in this order:

1. a due, important prior concept;
2. a concept naturally triggered by the learner's current repository task;
3. a blocking prerequisite on the active track;
4. the next small step in the active track;
5. a foundational node that remains unassessed.

When a durable resume point identifies a viable next increment, continue it
unless an earlier item in that order takes priority. Start with no more than
two short sentences that reconnect the learner to that resume point.

## Run the session

Teach only the selected increment: state its role in the larger system, the
one distinction or mechanism needed now, and one concrete example when useful.
Then ask at most one unaided retrieval or transfer prompt and wait for the
learner's attempt. For a due review, never reveal the answer, definition, or
adjacent relationships before that attempt. Afterward, give the minimal
correction needed to make the next attempt useful.

Do not manufacture a streak, infer retention, add canonical terminology, or
ask the learner to edit scheduling files. A learner can stop at any point.

## Record and resume

At a natural stop, create one append-only session event under
`learning-state/sessions/`; this is the tutor's repository-editing step, not a
learner task. Use the documented v1 YAML schema. Generate a unique event id as
`YYYYMMDDTHHMMSS+ZZZZ-<concept-id>-<check>` and save it as
`learning-state/sessions/<id>.yaml`. `started_at` must be the corresponding
valid ISO-8601 timestamp with offset. Use only a known track and concept, a
duration that reflects the actual short session, and one evidence item per
concept when evidence was observed. Record only what was observed:

```yaml
schema_version: 1
id: 20260821T123000+0800-idempotency-fresh-case-transfer
started_at: 2026-08-21T12:30:00+08:00
duration_minutes: 3
mode: contextual-review
track: scientific-ai-platforms
resume:
  from: idempotency
  next: partial-failure
  summary: Continue by deciding how to recover authority after an ambiguous timeout.
evidence:
  - concept: idempotency
    check: fresh-case-transfer
    outcome: pass
    confidence: medium
    assisted: false
```

If the learner stops before attempting the one check, preserve a precise
`resume`, write `evidence: []`, and do not invent a pass, partial, miss,
confidence, or retention claim. A resume-only event changes no capability or
schedule. If the observed exchange cannot otherwise be represented by the v1
schema, fail closed: do not write an event and tell the learner what evidence
is missing or ambiguous.

After writing an event, read it back through the state engine:

```bash
python3 scripts/build-learning-state.py validate
python3 scripts/build-learning-state.py normalized-data
python3 scripts/build-learning-state.py list-due --today YYYY-MM-DD
```

Report the one next encounter and its resume point, then stop. The state
engine is the authority for capability and review derivation; never duplicate
its rules in this skill.

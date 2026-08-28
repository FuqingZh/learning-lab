---
name: learning-lab-tutor
description: Run a history-grounded, map-first learning session from this repository's knowledge map and learning-state events. Use when a learner asks to continue, review, or study; do not use for ordinary repository implementation without a learning request.
---

# Learning Lab Tutor

Give the learner a coherent lesson unit with enough context to understand why
its mechanisms exist and how they fit together. There is no default timebox or
fixed number of concepts, paragraphs, or questions. Let the learning outcome,
the learner's starting knowledge, and the prerequisite structure determine the
unit size. Do not turn a work request into a lesson unless the learner asks for
learning help.

## Read the learner contract before selecting a lesson

Before selecting a lesson, read the personal-workspace marker and the learner's
teaching contract:

- `.teach-workspace.yaml`;
- `MISSION.md`;
- `NOTES.md`;
- root `RESOURCES.md`;
- the active track's `README.md`, `CURRICULUM.md`, and `RESOURCES.md`; and
- the recent relevant `learning-records/<track>/` inventory, then the records
  needed to understand demonstrated capability for the proposed unit.

Resolve the active track from the learner's request, current case, and durable
resume. If that evidence is insufficient, ask which track they intend to
advance rather than treating an arbitrary due concept as the curriculum.
Use the mission, its constraints, the teaching notes, trusted sources, and
demonstrated evidence to select a bounded capability in the learner's zone of
proximal development.

When `MISSION.md` requires Chinese, teach in Chinese unless the learner asks
for another language. Keep established technical terms in their standard
English form and explain them in Chinese when first needed.

## Choose the lesson unit

Read the current review-cue state; do not recreate its derivation:

```bash
python3 scripts/build-learning-state.py normalized-data
python3 scripts/build-learning-state.py list-review-cues --today YYYY-MM-DD
```

Use the learner's local calendar date for `YYYY-MM-DD`. Consult the normalized
state for the active track and latest `resume`, and the knowledge map for
relationships. Review cues are an input to selection, not an unconditional
first-priority queue or a claim about curriculum progression. Select one
primary learning outcome by weighing, in order:

1. the mission and its constraints, plus `NOTES.md` teaching preferences;
2. demonstrated capability in relevant learning records;
3. the active track curriculum and trusted resources;
4. the latest durable `resume`;
5. relevant review cues and concept relationships; and
6. the learner's current request or repository case.

A due concept is selected for retrieval only when that review is the best
mission-linked bounded win. A due cue must not displace a viable current-track
lesson merely because it is due.

`list-review-cues` is the preferred tutor command. `list-due` remains a
compatibility alias and returns the exact same JSON output for the same state
and supplied date; do not present its legacy name as a distinct scheduler or
curriculum signal.

Before teaching, state exactly one mission-linked lesson win and its stopping
condition: the observable unaided explanation, transfer, or other evidence
that will end this lesson.

One lesson unit may include several connected concepts or prerequisite bridges
when separating them would make the explanation fragmentary. Do not turn every
new term into its own lesson. When a durable resume point identifies a viable
next unit, continue it unless an earlier item in that order takes priority.
Reconnect the learner to that resume point briefly, but include any context
needed to make the resumed explanation intelligible.

## Use history only when it supports the lesson win

Use a historical increment only when it materially supports the selected lesson
win. When it does, require a complete matching dossier in `histories/` and
read that dossier and its linked source before teaching. Build an adequate
historical frame before asking the learner to reason: present the documented
time, actors, existing technical conditions, practical problem, constraints,
and source; state only what was knowable in that setting. Then explain the
source's proposal and contrast its historical meaning with the modern concept
boundary.

A prediction can be useful after that frame is established, but it is not a
mandatory interruption point. Do not stop after a few setup sentences merely
to force a prediction. If prediction would expose a useful design choice, ask
it after the learner has enough background; otherwise complete the historical
explanation and use an end-of-unit explain-back or transfer check.

Do not turn inferred motive, invented dialogue, or an imagined scene into
historical fact. Use a source only for what it directly supports; distinguish
terminology, problem, formalization, adoption, popularization, revision, and
critique rather than collapsing them into one origin story. Prefer
`explain-back` or `fresh-case-transfer` for evidence of historical understanding.
Never add date-memory or
historical-recall mastery state, and do not change the learning-state schema.

If history would materially support the win but no complete dossier is
available, fail closed for the historical increment: do not manufacture
history, infer a lineage, or fill the gap from general knowledge. Continue
without a historical claim when the existing concept and lesson contracts still
support the selected win.

## Run the session

Begin with an advance organizer suited to the learner's starting point:

- where the unit sits in the larger knowledge map;
- what people could already do in the selected historical or technical setting;
- what problem remained and why it was difficult;
- which prerequisite ideas and vocabulary will be needed; and
- what complete mental model or practical ability the learner should have by
  the end.

Then teach the connected explanation. Introduce vocabulary immediately before
it is used, walk through the mechanism, include a concrete example and a
contrast or counterexample, and connect the result to the modern boundary and
the repository case when appropriate. Do not interrupt every term or paragraph
with a question. Answer direct questions and repair missing prerequisites
before demanding retrieval.

Place checks at natural conceptual boundaries. Prefer a coherent end-of-unit
explain-back or fresh-case transfer over a sequence of tiny quizzes. Use an
intermediate diagnostic only when the learner's response reveals a blocking
misconception, or when the learner asks for a more interactive pace. For a due
review, never reveal the answer, definition, or adjacent relationships before
the learner's first retrieval attempt. After an attempt, explain the relevant
reasoning, not merely whether the answer matched.

Do not manufacture a streak, infer retention, add canonical terminology, or
ask the learner to edit scheduling files. A learner can stop at any point.

## Record and resume

At a natural stop, create one append-only session event under
`learning-state/sessions/`; this is the tutor's repository-editing step, not a
learner task. New production events use the documented v2 YAML schema. Write
v1 only for compatibility fixtures or byte-preserved historical examples, not
as a fallback for a new learner session.

Generate a unique neutral event id such as
`YYYYMMDDTHHMMSS+ZZZZ-<track-id>-session` and save it as
`learning-state/sessions/<id>.yaml`. The `-session` suffix is a neutral naming
convention, not a parser-mandated suffix. `started_at` must be the
corresponding valid ISO-8601 timestamp with offset. Use a known track, a
duration that reflects the actual session, and one evidence item per concept
when evidence was observed. Every v2 `resume` has exactly `unit_kind`,
`unit_ref`, `checkpoint`, and `summary`: choose `lesson`, `concept`, or `track`
for `unit_kind`, make `unit_ref` resolve to that kind, and write non-empty
checkpoint and summary prose. Record only what was observed:

```yaml
schema_version: 2
id: 20260827T123000+0800-scientific-ai-platforms-session
started_at: 2026-08-27T12:30:00+08:00
duration_minutes: 12
mode: guided-lesson
track: scientific-ai-platforms
resume:
  unit_kind: lesson
  unit_ref: lessons/scientific-ai-platforms/web-document-browser-and-server.md
  checkpoint: Compare browser navigation with a fresh client-server case.
  summary: Continue the connected document, browser, server, request, and response model.
evidence:
  - concept: program
    check: fresh-case-transfer
    outcome: pass
    confidence: medium
    assisted: false
```

If the learner stops before completing an evidence check, preserve a precise
v2 `resume`, write `evidence: []`, and do not invent a pass, partial, miss,
confidence, or retention claim. An empty-evidence event is neutral: it updates
only the durable recovery cue and creates no capability evidence or review cue.
Do not fall back to v1 merely because the learner stopped before a check. If
the observed exchange cannot otherwise be represented by the v2 schema, fail
closed: do not write an event and tell the learner what evidence is missing or
ambiguous.

After writing an event, read it back through the state engine:

```bash
python3 scripts/build-learning-state.py validate
python3 scripts/build-learning-state.py normalized-data
python3 scripts/build-learning-state.py list-review-cues --today YYYY-MM-DD
```

Report the next encounter and its resume point, then stop. The state engine is
the authority for review-cue derivation; never duplicate its rules in this
skill. Review cues do not decide curriculum progression or replace the learner
records used to select a lesson. Learning records are the authority for
reviewed demonstrated capability. Session events are append-only raw
observations: they can create a review cue or candidate for record promotion,
but do not directly establish reviewed capability.

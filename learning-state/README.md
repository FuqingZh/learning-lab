# Learning state

Append-only YAML events in `sessions/` are the source of personal learning
evidence. `scripts/build-learning-state.py` validates them against the
canonical knowledge graph and derives deterministic JSON state.

```bash
python3 scripts/build-learning-state.py validate
python3 scripts/build-learning-state.py normalized-data
python3 scripts/build-learning-state.py list-due --today 2026-08-21
python3 scripts/build-learning-state.py list-review-cues --today 2026-08-21
```

`normalized-data` deliberately contains no current-clock-dependent due label.
`list-due` is retained as a compatibility command. `list-review-cues` is the
preferred name and returns its exact JSON envelope. Both apply the
caller-supplied calendar date. A `partial`, `miss`, or assisted latest outcome
is projected for the next day; `overdue` independently reports whether the
next review date is earlier than the supplied date.

Events remain append-only. Schema v1 uses `resume.from`, `resume.next`, and
`resume.summary`; normalized output marks that recovery cue as `legacy: true`,
maps `next` to the unified concept reference, and preserves additive `from` and
`next` aliases for schema-v1 consumers. Schema v2 uses this exact block:

```yaml
resume:
  unit_kind: concept # concept, track, or lesson
  unit_ref: idempotency
  checkpoint: distinguish-authority
  summary: Resume by checking the authority at the uncertain boundary.
```

For `lesson`, `unit_ref` must be a canonical repository-relative, existing
Markdown path below `lessons/`; it is not inferred from an event filename or
restricted to the event's track. A v2 cue always normalizes with `legacy:
false`. Empty-evidence events update only the latest recovery cue. Assisted
evidence is preserved as observation, but cannot promote a session-derived
capability or lengthen the pass interval.

The normalized `capability_state` remains a compatibility projection over raw
session observations. It is not reviewed demonstrated capability. Structured
records under `learning-records/` own that separate conclusion, while this
producer owns observation history, resume, and review cues.

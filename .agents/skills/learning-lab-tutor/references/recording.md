# Evidence and recording

Read before writing learning events or reviewing capability. Preserve the v2
session contract; discussion navigation has a separate schema.

Reviewed records under `learning-records/` own demonstrated capability. Session
events are append-only observations; normalized `capability_state` is only a
compatibility projection. Review cues do not decide curriculum progression.
The state engine is the authority for review-cue derivation; never duplicate it.
`list-review-cues` is preferred; `list-due` remains its compatibility alias.

At a natural stop in an actual learning encounter, write one observed v2 event
under `learning-state/sessions/`. Do not create subject-mastery events for a
teaching-design discussion or coding task. Preserve existing events. Neutral
IDs use `YYYYMMDDTHHMMSS+ZZZZ-<track-id>-session`; the suffix is a convention,
not parser-mandated. Use actual timestamps/duration; never invent them.
Read `learning-state/README.md` for the existing producer contract.

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
  checkpoint: Explain the client/server boundary in another case.
  summary: Continue the connected document, browser, and server model.
evidence: []
```

This is an illustrative event, not an event to copy into production. Every v2
resume contains exactly `unit_kind`, `unit_ref`, `checkpoint`, and `summary`.
Kinds are `lesson`, `concept`, or `track`; references must resolve. Without a
check, write `evidence: []`: no capability or review-cue change. Do not invent
pass, partial, miss, confidence or retention. Observed checks use existing
fields including `assisted`; preserve hints/repair and do not label replay as
fresh independent transfer. Unknown evidence stays unconfirmed.

Do not add canonical terms just to encode syntax or spread broad `program`
evidence to untested frontend skills. Keep precise prose and unknown prerequisites
instead of inventing state fields. New production events must not fall back to
v1; v1 is for compatibility fixtures and unchanged historical examples. If the
exchange cannot be represented faithfully, do not write an event; explain the gap.

After writing, read back through the existing producer:

```bash
python3 scripts/build-learning-state.py validate
python3 scripts/build-learning-state.py normalized-data
python3 scripts/build-learning-state.py list-review-cues --today YYYY-MM-DD
```

After navigation edits run its validator too. Navigation owns detailed discussion
position, not capability; keep new session resume consistent. No navigation
update may rewrite old events or promote mastery. Stopping/declining a check
is not a learning failure.

# Lightweight discussion navigation

One sanitized YAML snapshot per active track: `<track>.yaml`. It describes
discussion position, not mastery, review scheduling, or a transcript. Original
messages stay in the authorized platform source or a private export under the
Git-ignored `.learning-private/`. That directory is neither encrypted nor backed
up by this repository. Never commit raw conversations or private source paths.

```bash
python3 scripts/check-teaching-navigation.py validate
python3 scripts/check-teaching-navigation.py resolve --track scientific-ai-platforms
```

Both commands are read-only. There is no automatic navigation engine, database,
collector or change to the session schema. `resolve` reads only the selected
track's snapshot. If absent, it reads the old producer's latest resume and uses
it only if its track matches; otherwise reports no resume. It does not invent
a per-track scheduler. If invalid, it fails visibly rather than falling back.
The current user request always takes precedence over either stored position.
The generated website still shows old session resume; this CLI supplies the
tutor's detailed position and does not modify generated public projections.

## Snapshot schema (version 1)

Top-level fields are exactly `schema_version`, `track`, `updated_at`, `source`,
`main`, `active_branch`, and `branches`. `updated_at` is a quoted ISO timestamp
with timezone. Track names resolve below `tracks/`; filename must match track.

- `source`: exactly `enabled`, `locator`, `coverage`, `verified_range`, `gaps`.
  `enabled: true` declares explicit conversation opt-in, not proof of consent.
  `locator` is an opaque string or null, never an instruction/access grant.
  `coverage` is `missing`, `partial`, or `complete`. Missing needs nonempty gaps
  and null verified_range. Partial needs locator, checked range, and gaps.
  Complete needs locator and checked range with no gaps. These are declarations;
  structural validation does not verify the actual conversation or capture scope.
- `main`: exactly `unit_ref` and `checkpoint`; an existing Markdown lesson under
  `lessons/` plus a precise nonempty description of where to continue.
- `active_branch`: a branch ID or null. Null means resume the main checkpoint.
- `branches`: list of nodes with exactly `id`, `parent`, `unit_ref`, `question`,
  `purpose`, `status`, `return_to`, `conclusion`, and `unresolved`.
  `parent` is another node ID or null for the main route. IDs are unique
  lowercase hyphenated names other than `main`. Status is `open`, `parked`, or
  `resolved`. `return_to` has exactly `node` and `checkpoint`; node must equal
  the parent ID, or `main` for root branches. A resolved node requires a
  nonempty conclusion and no unresolved questions; a parked node requires a
  nonempty unresolved list. Conclusions otherwise may be null.

All open nodes must form exactly the active node's ancestor chain, belong to
the current main lesson, and have open ancestors. No cycle/orphan or unresolved
child of a resolved parent is accepted. Parent and child unit_ref must match.
Parked root branches may retain an old lesson after a route change. No natural
language checkpoint can be mechanically proven pedagogically correct.

## Manual updates

Before a substantial branch, save its purpose and interrupted checkpoint. For
a nested question, name its parent rather than overwriting the main checkpoint.
To return, record the bounded conclusion, mark the node resolved, set the active
node to its parent, and continue at return_to.checkpoint (update main.checkpoint
when returning to main). A connective explanation completes the return.
To pause a branch, record what remains unresolved and mark it parked; park
unfinished descendants too. On a new main route, retain unfinished old branches
as parked. Do not mark a branch resolved simply to satisfy the validator.

Validate after edits. No record update may promote capability or alter old
session observations. This file is a small current snapshot, not an event log;
Git supplies recoverability for sanitized changes, not the original messages.
Do not create subject-learning sessions for teaching-design or coding work.

Collection failure is non-blocking for teaching but blocks conclusions depending
on missing original evidence. Later exports must preserve message order, source
IDs and gaps. Do not reconstruct missing text. Automatic capture is not shipped
in this first edition. A consent change stops future collection; deleting raw
exports remains an explicit user-authorized operation.

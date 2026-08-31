---
schema_version: 1
approved_on: '2026-08-31'
original_revision: 983652c711c13c3153dc519b379b9e47179bd579
source_thread: 01a00e46-1bee-7081-a01d-111f587fdfbd
coverage: partial
events:
  - original_id: 20260828T102900+0800-scientific-ai-platforms-session
    corrected_id: 20260828T100124+0800-scientific-ai-platforms-session
    original_duration_minutes: 10
    source_turn: 01a04619-b347-73d3-853d-25475b70eaaa
    source_start: '2026-08-28T10:01:24+08:00'
    source_end: '2026-08-28T10:31:36+08:00'
    duration_minutes: 31
  - original_id: 20260828T130302+0800-scientific-ai-platforms-session
    corrected_id: 20260828T130242+0800-scientific-ai-platforms-session
    original_duration_minutes: 3
    source_turn: 01a046bf-af61-7451-9e49-5bf1a2c9d2de
    source_start: '2026-08-28T13:02:42+08:00'
    source_end: '2026-08-28T13:03:40+08:00'
    duration_minutes: 1
  - original_id: 20260828T144440+0800-scientific-ai-platforms-session
    corrected_id: 20260828T144424+0800-scientific-ai-platforms-session
    original_duration_minutes: 4
    source_turn: 01a0471c-c96c-72d1-8ebc-7c5a85054f58
    source_start: '2026-08-28T14:44:24+08:00'
    source_end: '2026-08-28T14:45:05+08:00'
    duration_minutes: 1
  - original_id: 20260828T160301+0800-scientific-ai-platforms-session
    corrected_id: 20260828T160244+0800-scientific-ai-platforms-session
    original_duration_minutes: 78
    source_turn: 01a04764-83af-7591-81d1-d8fb8b08a282
    source_start: '2026-08-28T16:02:44+08:00'
    source_end: '2026-08-28T16:03:38+08:00'
    duration_minutes: 1
  - original_id: 20260828T163152+0800-scientific-ai-platforms-session
    corrected_id: 20260828T163142+0800-scientific-ai-platforms-session
    original_duration_minutes: 28
    source_turn: 01a0477f-07f1-75a2-8702-d61ae27c3a4c
    source_start: '2026-08-28T16:31:42+08:00'
    source_end: '2026-08-28T16:32:13+08:00'
    duration_minutes: 1
  - original_id: 20260828T165150+0800-scientific-ai-platforms-session
    corrected_id: 20260828T165136+0800-scientific-ai-platforms-session
    original_duration_minutes: 20
    source_turn: 01a04791-3e84-7003-9da2-c11ad7eba6e2
    source_start: '2026-08-28T16:51:36+08:00'
    source_end: '2026-08-28T16:52:13+08:00'
    duration_minutes: 1
---
# Session timing and review-count audit

The learner authorized this correction on 2026-08-31 after PR #9 identified
overlapping imported timing and repeated-pass review inflation. This is a
bounded exception to append-only recording, not routine rewriting of history.

## Source and correction boundary

Read only the enabled thread identified above, paginating the platform's turn
records back through the relevant 2026-08-28 exchanges. The six source turn IDs
and platform start/completion timestamps are recorded above; raw messages,
reasoning, command output and host addresses are not copied into this repository.
This is a targeted audit, not complete transcript capture.

The former timestamps fall near record-writing time, not the beginning of the
whole lesson described in the summary. No source establishes the former 78-minute
interval as starting at 16:03. The imported durations cannot be treated as measured
active study time. Instead of guessing lesson starts, the corrected records cover
the six observable source turns that introduced the resume point or recorded the
final learner answer and tutor response. This intentionally narrows the timing
scope; the summaries retain earlier conversational context.

Duration is ceil((source_end - source_start) / 60), required by the existing
integer-minute schema. It bounds source-turn wall time, not exact response time,
reading time, whole-lesson duration or learning effort. The first turn includes
Git delivery and waiting: its 31 minutes must not be counted as 31 teaching
minutes. The five one-minute records are final feedback turns, not claims that
those subjects were learned in one minute. Adjacent user thinking/reading time
is unobserved. Do not aggregate these values as a learning-time metric.

IDs and filenames follow the corrected start, as required by the existing
parser. The frontmatter maps every old link/ID to its replacement. Original
files and values remain recoverable at the pinned original Git revision.
No other session, evidence item, assisted flag or capability record was changed.
Old conversation links to renamed files require this mapping or the original
revision; no duplicate live YAML events are retained.

## Review-count correction

The two unassisted program passes on August 28 represented separate checks
inside a continuous sequence, not spaced retrieval. The old fixed-v1 counter
advanced for every pass. Under fixed-v2-distinct-days, successful observations
are retained individually but contribute at most one count per concept and UTC
calendar day. Different offset spellings cannot create two success days.
The interval ladder remains 1/7/21/60; the due-date anchor remains the latest
observation's local date, and latest assisted/partial/miss still means next day.

The UTC day is an explicit conservative scheduling proxy, not an inferred
encounter identifier, universal pedagogical boundary, or retention proof.
A cross-midnight encounter can occupy two buckets; multiple independent
encounters within one day are coalesced. Evidence count and capability
projection algorithms are unchanged. Reviewed capability remains separately
owned by learning records. For program, the affected next-review output moves
from 2026-09-04 to 2026-08-29 without erasing the observed checks.

## History association

Register the React bridge in web-programming-history.lessons, the producer-owned
association consumed by search and the history panel. Only the lesson link is
added; historical claims, chronology and canonical concept definitions remain
unchanged. Regenerate the site through its existing renderer.

## Verification scope

Negative controls reproduced the old same-day and timezone-offset counter
failures before changing the implementation. Tests cover repeated-day counting,
later-day advancement, assisted behavior, source-window/record consistency and
lesson association. The repository gate and exact-head CI must also pass.

Automated checks verify the declared audit data against the live records, not
whether platform timestamps measure human attention. Source review remains
separate. The policy is a bug fix and a conservative bound; improved learning
outcomes and long-term retention are not claimed.

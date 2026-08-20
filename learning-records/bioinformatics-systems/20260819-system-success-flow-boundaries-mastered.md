# End-to-end system success and ambiguous outcomes are understood

The learner can inspect one system through data flow, control flow, and state
flow while keeping local computation success separate from end-to-end request
success.

The learner understands that a correct in-memory result is not a successful
request when durable commit and delivery have not occurred. Conversely, a
timeout is not proof of operation failure when the authoritative state may have
committed before the response was lost.

```text
authoritative state != caller knowledge != transport observation
```

## Evidence

In unaided application on 2026-08-19, the learner:

- identified data, control, and state as separate views of one system path;
- required actual result evidence rather than treating request acceptance as
  proof of completion;
- classified a committed result with a lost response as successful in
  authoritative state but unknown to the caller; and
- selected stable request/job identity plus authoritative status readback
  before retry, explicitly to avoid duplicate computation or side effects.

The learner also recognized that retry should occur only after the outcome is
resolved as absent or failed and the operation is known to be safely
repeatable.

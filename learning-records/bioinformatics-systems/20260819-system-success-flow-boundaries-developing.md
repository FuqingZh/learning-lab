# End-to-end system success is developing

Superseded by
[the mastered record](20260819-system-success-flow-boundaries-mastered.md)
after the authoritative-readback recovery check was completed.

The learner introduced a useful three-flow decomposition for reasoning about a
system:

```text
data flow     what information moves and is transformed
control flow  what decides and sequences execution
state flow    what durable facts change and become committed
```

The learner also rejected treating receipt of a request as proof of a real
result and required validation of the produced outcome.

## Boundary still being consolidated

The flow decomposition is an observation method rather than the answer to
whether one layer succeeded. In the crash scenario, the hypothetical already
states that the in-memory algorithmic result is correct, so the local
computation succeeded. The end-to-end request did not succeed because the
state transition was not durably committed and the result was not delivered or
acknowledged.

The failure crosses more than state flow: control stopped before the workflow
reached its commit and delivery steps, while data existed only in volatile
memory. A further scenario check is needed to separate local step success from
end-to-end system success.

In the committed-result/lost-response scenario, the learner correctly rejected
a timeout as proof of task failure and distinguished successful computation and
durable state from the caller's unknown outcome. The remaining refinement is
that data flow was not wholly complete: result data reached durable storage,
but the success response did not reach the user. A final recovery-action check
remains before mastery.

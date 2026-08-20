# System success, three flows, and ambiguous outcomes

## A system is more than a computation

A local algorithm can be modeled as `y = f(x)`. A real system must also
identify the input and computation, commit durable state, deliver a result, and
make failures observable and recoverable.

```text
end-to-end success
= correct input interpretation
+ correct computation
+ durable state transition
+ result delivery
+ observable recovery boundary
```

Completing one term does not imply that the whole request succeeded.

## Three views of one path

The same system can be inspected through:

```text
data flow     what information moves and is transformed
control flow  what decides and sequences the next action
state flow    what facts become durable and committed
```

These are views rather than independent components. A correct result may exist
in volatile memory while control fails before commit, leaving no durable state.

## Local success versus request success

If an algorithm computes a correct result and the process crashes before save
or response:

- the local computation step succeeded;
- control did not complete the workflow;
- state was not durably committed;
- the user request did not succeed.

Request receipt and process exit are observations about individual steps, not
proof of the complete outcome.

## Ambiguous outcome

If the result is committed and the success response is lost:

```text
authoritative state  success
caller knowledge     unknown
transport observation timeout
```

The operation succeeded in the system, but the caller cannot infer that fact
from the timeout. A transport failure is not equivalent to an operation
failure.

## Recovery rule

After an ambiguous outcome:

1. use a stable request or job identity;
2. read back the authoritative state;
3. deduplicate against an existing success;
4. retry only when the intended state is absent or failed and repetition is
   safe.

Blind retry can duplicate computation, charges, messages, or other side
effects. The later idempotency and concurrency modules explain how systems make
this recovery rule enforceable.

## Review questions

For any reported timeout, ask:

```text
What actually committed?
What did the caller observe?
Which response or acknowledgment was lost?
What stable identity allows authoritative readback?
Is repeating the operation safe?
```

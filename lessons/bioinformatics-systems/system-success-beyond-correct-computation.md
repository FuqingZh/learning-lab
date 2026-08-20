# System success beyond correct computation

## From a function to a system

A function-level model is:

```text
y = f(x)
```

A real system must additionally identify the input and computation, manage
state, deliver the result, and remain observable and recoverable when something
fails.

```text
real-world input
  -> representation and identity
  -> orchestration and computation
  -> state and storage
  -> result interface and consumption
  -> observation, recovery, and evolution
```

## Different success boundaries

An algorithm can produce the correct value in memory while the enclosing
request still fails. If the process crashes before persistence and delivery:

- the transformation may be computationally correct;
- no durable result has been committed;
- the caller has not received a completed result;
- the system must report or recover from an incomplete request.

System success is therefore conjunctive:

```text
correct input interpretation
+ correct computation
+ reliable state transition
+ valid result delivery
+ observable and recoverable failure behavior
```

Passing one term does not compensate for a missing term.

## Review rule

When a component reports success, ask which boundary succeeded:

```text
algorithm, process, state commit, result publication, or user request?
```

Do not promote a narrower success claim to a broader one without evidence for
the remaining layers.

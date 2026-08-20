# System success beyond correct computation is understood

The learner can distinguish local algorithmic success from end-to-end system
success. A correct value computed only in process memory does not complete the
user request if the process crashes before durable state publication and result
delivery.

## Evidence

In unaided application on 2026-08-19, the learner classified a correct
in-memory scientific computation as algorithmically successful but the overall
request as failed. The learner located the missing guarantees in the state and
storage layer and the result interface and consumption layer.

This establishes the first systems-map distinction:

```text
correct computation != completed system contract
```

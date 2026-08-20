---
Status: superseded by [handle boundary mastery](0011-handle-boundary-mastered.md)
---

# Dataset handle boundaries are developing

The learner correctly recognizes the value of preprocessing inputs into trusted
schema and summaries and of keeping host file paths outside the model-facing
contract. These are important determinism and security properties.

The learner now distinguishes the handle boundary from the sandbox boundary:
the handle participates in selecting an authorized input, while the sandbox
constrains what executing code can access and do.

One boundary still needs correction. A `dataset_handle` is not an input summary
or the scientific identity of its bytes. In the current project it is an opaque
digest-derived reference whose authoritative meaning lives in the server-side
`ExternalToolRun.dataset_id_by_handle` mapping. Schema and summaries are
separate descriptors, while content hashes and the immutable `Dataset` establish
the input's content identity.

## Evidence

In the first capability-boundary explanation on 2026-08-17, the learner
attributed schema, content, and preprocessed file information to the handle and
described it as fundamentally preventing escape, while correctly identifying
the dangers of exposing real host paths and allowing the model to infer raw
file structure without deterministic preprocessing.

In the first retry, the learner correctly separated handle authorization from
sandboxed execution but still described the handle as the input's summary and
fixed identity.

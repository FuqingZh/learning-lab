# Systems map first-pass walkthrough

## Scenario

A microscopy analysis service accepts images, counts cells with a model, and
returns one report for each image. This case is deliberately generic: its role
is to expose reusable system questions, not to prescribe a repository schema.

## The seven views

### 1. Domain meaning

“The program returned a count” is not the same as “the count is scientifically
correct.” Algorithm quality needs a reference: for example, expert-reviewed
cell counts across a representative evaluation set. Domain meaning determines
what counts as a correct result and how correctness is evaluated.

### 2. Data and identity

Identity begins by defining what “the same input” means.

- A content hash such as SHA-256 can identify the exact retained byte stream.
- Base64 is an encoding, not a content identity algorithm.
- A PNG and a JPEG depicting the same scene normally have different bytes, so
  they are not equal under exact-file identity.
- A normalized-pixel identity is a different contract and needs an explicit
  decoding and normalization procedure.

A hash is an identifier for content; it is not the content itself. If the raw
image is deleted, its hash cannot reconstruct the image.

### 3. Computation

A result depends on more than an input ID. Its computation identity may include
the model architecture and weights, model version, preprocessing procedure,
scientific parameters, tool version, and relevant execution environment.

Logical independence does not require physical one-by-one execution. Two
hundred images may be processed in one efficient batch as long as each output
remains correctly linked to its input and the batch operation does not change
the promised per-image semantics.

### 4. State and lifecycle

The system must distinguish accepted, queued, running, succeeded, no-result,
and failed states, and persist enough authoritative facts to recover after an
interruption. Reanalysis requires the authoritative input, or a lossless route
to retrieve it, plus the computation identity. An input hash alone is
insufficient.

If computation succeeds but the response is lost, caller knowledge is
“unknown”; the authoritative job state may still be “succeeded.” A stable
request or job ID lets the caller inspect that state before deciding whether a
retry is safe.

### 5. Interface

The interface must preserve input-to-result linkage. A successful HTTP response
is not enough if image A receives image B's report. Error responses should also
preserve the public error contract rather than expose an internal exception as
though it were a valid scientific result.

### 6. Concurrency and failure

Duplicate submissions, worker interruption, partial batch completion,
ambiguous responses, and cleanup are normal design cases. Stable identities,
idempotent request handling, authoritative state inspection, and bounded
cleanup make these cases controllable. Retrying blindly can duplicate work or
confuse an already committed result with a new execution.

### 7. Operations and evolution

Results must remain interpretable after the model or pipeline changes. A model
v1 result cannot silently become a model v2 result, nor can it be reused as v2
without a compatibility rule that justifies that reuse. Monitoring, retention,
migration, and rollback all depend on explicit versioned identities.

## Cross-cutting qualities

Correctness, reproducibility, reliability, performance, security, and
observability cut across all seven views. They are not individual components.
Each measurable objective should state its metric, target, scope, and window.

## Review checklist

For a new scientific service, ask:

1. What scientific claim is being made, and against what reference is it judged?
2. What exactly makes two inputs or two computations the same?
3. Which facts must be retained to reproduce or rebuild a result?
4. Which authority owns lifecycle state after a timeout or interruption?
5. Does the interface preserve the association between every input and result?
6. What happens under duplication, concurrency, partial failure, and retry?
7. How are old and new algorithm versions kept scientifically distinguishable?

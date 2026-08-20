# Handle, descriptor, content identity, and sandbox are distinguished

The learner can now separate four independent concerns in a scientific AI
system: a `dataset_handle` selects an authorized data object, columns and
summaries describe its shape, a content hash establishes exact byte identity,
and a sandbox constrains what executing code can access and modify.

This closes the earlier misconception that the handle contains a summary or
itself provides execution isolation. Future lessons can build on this boundary
to study authorization context, capability leakage and revocation, and the
confused-deputy problem.

## Evidence

In an unaided four-way classification on 2026-08-17, the learner mapped each
object to the correct question: authorization reference, data description,
byte equality, and execution authority respectively.

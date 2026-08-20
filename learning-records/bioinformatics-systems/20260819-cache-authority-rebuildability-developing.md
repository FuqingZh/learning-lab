# Cache authority and rebuildability are developing

Superseded by
[the mastered record](20260819-cache-authority-rebuildability-mastered.md)
after the role-and-impact classification was completed.

The learner recognizes that a component whose deletion causes unrecoverable
loss is not merely an acceleration cache. It has accumulated authoritative
responsibility for the source, construction, or result instead of remaining a
disposable derived copy.

## Boundary still being consolidated

The decisive property is not whether source, process, and result are physically
stored together. It is whether an independent authoritative source plus a
defined computation can reconstruct the value correctly.

```text
deletable and reconstructable, with only performance loss -> cache
only surviving authoritative copy                         -> source of truth
durable derived output with defined lineage               -> materialized result
```

A database, file, or object store can play any of these roles. Persistence and
technology do not determine authority. Rebuildability requires sufficient
inputs, computation identity, parameters, resources, and provenance; a claim
that data is cached is false if those dependencies are unavailable or cannot
reproduce the value.

## Evidence

On 2026-08-19, the learner described a non-rebuildable component as carrying
the combined construction-source, process, and result responsibilities without
separation. A role-classification exercise remains before mastery.

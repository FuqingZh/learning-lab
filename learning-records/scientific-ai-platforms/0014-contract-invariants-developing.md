---
Status: superseded by [contract and invariant mastery](0015-contract-invariants-mastered.md)
---

# Contract and invariant layers are developing

The learner correctly states that passing a formal check does not establish
that the content is correct, and recognizes that machine-readable form is
valuable for contracts and downstream processing while content requires a
separate judgment.

The remaining distinction is that “form” and “content” are too coarse as a
system model. A typed contract can encode more than parseability: field types,
enums, ranges, forbidden extra fields, conditional requirements, and
cross-field invariants can all be mechanically checked. Other invariants depend
on authoritative runtime state, while scientific correctness depends on claims
and evidence that the encoded gates may not establish.

The active target is therefore to ask what proposition each gate proves:
structural/schema validity, cross-field domain consistency, temporal/state
legality, or scientific correctness. Passing a gate proves only the assertions
that the system actually encoded and evaluated.

One focused retry remains: classify a structurally valid request that violates
a cross-field domain rule, then state the proof scope of the first three gates
without importing untested authentication, authorization, path-resolution, or
sandbox claims.

## Evidence

On 2026-08-18, when beginning the typed-contract lesson, the learner
spontaneously separated formal validity from content correctness and explained
the operational value of formal structure. A fresh classification task is
still needed to demonstrate separation of schema, domain, state, and scientific
invariants.

On 2026-08-19, the learner correctly classified replacement of an accepted
revision as a state-invariant violation and misuse of an independent-samples
analysis for paired data as a scientific-correctness failure. The learner
classified `inferential` with an empty but structurally permitted
`input_datasets` object as a structural-contract failure rather than the
downstream domain-invariant failure. The learner also generalized passage of
the first three layers into identity binding, path execution, and sandbox
safety even though those propositions require their own explicit gates and
evidence.

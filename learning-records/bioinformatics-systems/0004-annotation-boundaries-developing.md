---
Status: superseded by [annotation boundary mastery](0005-annotation-boundaries-mastered.md)
---

# Annotation boundary classification is developing

The learner correctly identifies an eggNOG `seed_ortholog` as matching evidence
used for functional inference rather than the input protein's identity or a
direct functional fact. The learner also understands that direct Pfam scanning
can produce multiple region-level matches for one protein, while eggNOG and
Pfam evidence retain different row grains.

The learner subsequently retrieved the runtime boundary correctly: changing
only the immutable external execution environment changes
`ToolRuntimeDigest`, not inherently `AdapterContractVersion`.

One boundary still needs unaided retrieval before this capability is treated
as mastered:

- a profile HMM is a statistical model of aligned sequence positions, insertions,
  and deletions, not a model of three-dimensional protein structure;

## Evidence

In the first annotation-boundary check, the learner classified the biological
role of `seed_ortholog` correctly and causally explained one-to-many Pfam domain
matches, while using “spatial model” for a profile HMM and conflating the
adapter boundary with runtime identity.

In the follow-up check, the learner corrected the adapter/runtime distinction
but stated that a Pfam profile HMM contains protein spatial structure inferred
from known databases. This remains the active misconception: the standard Pfam
profile used by HMMER is estimated from a multiple sequence alignment and does
not contain atomic coordinates.

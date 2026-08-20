---
Status: superseded by [orthology-aware transfer mastery](20260819-orthology-transfer-mastered.md)
---

# Orthology-aware functional transfer is developing

The learner correctly classifies `A_X` and `A_Y` as orthologs and `A_X` and
`B_Y` as paralogs when ancestral `G` duplicated into `A` and `B` before the
`X`/`Y` speciation. The learner also rejects exact functional transfer from a
top-scoring paralog and correctly states that a SeqEvi `hit` proves completion
of the exact computation contract rather than biological truth.

Two retrieval gaps remain. The learner does not yet explain that eggNOG-mapper
uses the seed match to enter an orthologous group, then refines candidate donors
with precomputed phylogenies, taxonomic scope, and ortholog-type selection. The
learner also described E-value as a random-occurrence probability; the mastered
definition is the expected number of chance matches scoring at least as well in
the defined search.

## Evidence

In the first application check on 2026-08-19, the learner classified the simple
duplication-before-speciation tree correctly, rejected E-value-only exact
function transfer, and preserved the computation-versus-truth boundary, while
leaving the post-seed eggNOG inference step unspecified.

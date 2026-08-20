# Protein entry types and signature matches are developing

Superseded by
[the mastered record](20260819-protein-entry-types-mastered.md) after the
architecture and donor-selection application checks were completed.

The learner can separate a biological protein feature from the computational
model used to detect it and from the result of one scan. In unaided retrieval,
the learner correctly classified a profile HMM as a signature, a protein
kinase domain as a biological domain, and a query-region result as a match.
The learner also rejected precise whole-protein function as a conclusion from
a statistically significant domain match.

## Boundary still being consolidated

Statistical significance belongs to the match between a sequence region and a
signature; it is not a property of the biological domain itself. A low E-value
does not establish orthology because orthology is an evolutionary relationship
defined by speciation rather than a score threshold.

A SeqEvi `no_hit` state means that no candidate match satisfied the exact
adapter, runtime, resource, parameters, and acceptance criteria. It does not
classify the whole sequence as statistically non-significant, nor does it prove
that the protein lacks domains or function.

## Evidence

On 2026-08-19, the learner correctly reconstructed the
signature/domain/match distinction and the statistical-versus-biological
interpretation boundary. A further architecture-level application is needed
to confirm the scope of `no_hit` and the extra evidence required for an exact
whole-protein claim.

In the subsequent architecture exercise, the learner correctly rejected exact
function as a conclusion from Pfam matches without an accepted eggNOG
orthology assignment. The remaining refinement is to state the positive
architecture-level claim supported jointly by the signal-peptide,
transmembrane-helix, and domain predictions, and to avoid referring to a site
match when no site result was present.

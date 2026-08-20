# Protein entry types and signature matches are understood

The learner can distinguish protein families, domains, sites, and repeats as
biological entry types; a profile HMM as a predictive signature; and a
sequence-region result as a computed match. The learner understands that
statistical significance belongs to the match and does not by itself establish
precise whole-protein function.

The learner can combine signal-peptide, transmembrane-helix, and Pfam domain
predictions into a bounded architecture-level claim while withholding receptor
identity, catalytic activity, exact substrate, and orthology when those claims
lack supporting evidence. The learner also understands that `no_hit` means no
candidate was accepted under one exact computation contract, not that the
protein lacks domains or function.

## Evidence

In unaided retrieval and application on 2026-08-19, the learner:

- classified a profile HMM, biological domain, and query-region match at the
  correct model, entity, and result layers;
- rejected exact functional and orthology claims from a low E-value alone;
- bounded a multi-predictor receptor-like architecture without treating it as
  a named receptor or experimentally established function; and
- selected a lower-identity one-to-one ortholog over a 92%-identity paralog for
  exact substrate transfer when the ortholog retained the key binding residues
  and carried direct same-substrate experimental evidence.

The final choice was based on the combined evidence rather than treating the
ortholog label as universally superior to sequence similarity.

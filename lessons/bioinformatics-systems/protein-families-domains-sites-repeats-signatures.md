# Protein families, domains, sites, repeats, and signatures

## Three different layers

Protein annotation becomes easier to reason about when biological objects,
detection models, and computed results are kept separate:

```text
biological object -> predictive signature -> sequence-to-signature match
domain               profile HMM            query positions 470-742
```

A signature match is evidence about a biological object. The model and the
object are not interchangeable.

## Biological entry types

- A **family** groups proteins with a common evolutionary origin. Family
  membership can support related function, but subfamilies may differ in
  substrate, specificity, localization, or regulation.
- A **domain** is a distinct structural, functional, or sequence unit that can
  be combined with other domains. The same domain can occur in proteins with
  different whole-protein functions.
- A **site** is a short set of conserved residues, such as an active, binding,
  post-translational-modification, or other conserved site. A matching site
  pattern does not alone prove biochemical activity.
- A **repeat** is a short sequence unit that occurs multiple times. Repeats can
  assemble into a structural scaffold or binding surface without determining
  the exact function of the whole protein.

## Signatures and matches

A **signature** is a predictive computational model used to detect a family,
domain, site, repeat, or other feature. A Pfam profile HMM is one kind of
signature. It is commonly derived from a multiple-sequence alignment and
represents position-specific residue and state-transition probabilities.

The following are different claims:

```text
PF00069 profile HMM                 signature
protein kinase domain               biological domain
Q positions 470-742 match PF00069   computed match
```

Statistical quantities such as raw score, bit score, and E-value describe the
computed match. The domain itself is not statistically significant or
non-significant.

## Why domain architecture matters

Consider a protein with this architecture:

```text
[extracellular domains]--[transmembrane helix]--[protein kinase domain]
```

A strong match to the kinase-domain signature supports the presence of a
kinase-like region. It does not by itself establish receptor status, substrate,
signaling role, catalytic activity, or orthology to a named protein. Those
claims may require the remaining architecture, conserved catalytic residues,
family or subfamily classification, localization, phylogenetic evidence, and
experimental observations.

High confidence and broad claim scope are therefore different axes: a domain
match may be highly reliable evidence for domain presence while remaining
insufficient evidence for an exact whole-protein function.

## Similarity, orthology, and research value

A highly similar paralog is a homolog whose separating evolutionary event was
gene duplication and whose protein sequence has changed relatively little.
This can result from a recent duplication, strong functional constraint, or
both. It supports shared sequence features and possibly shared biochemical
machinery, but a few altered specificity residues or changes in expression,
localization, interaction partners, and dosage can still produce different
biological roles.

A distantly similar ortholog is a homolog separated by speciation whose
orthologous relationship remains supported despite substantial sequence
divergence. Orthology supports descent through the corresponding speciation
lineages; it does not guarantee unchanged function, and divergence lowers the
confidence of transferring fine-grained sequence-dependent properties.

Neither category has universally greater research value. The useful donor or
comparison depends on the question:

- structure, catalytic machinery, and close biochemical behavior may favor a
  highly similar sequence, including a paralog;
- conserved ancestral roles and cross-species correspondence make a supported
  ortholog especially relevant;
- post-duplication specialization, redundancy, compensation, and dosage make
  highly similar paralogs particularly informative;
- exact function transfer should combine relationship type, duplication age,
  sequence and architecture similarity, key residues, organismal context, and
  the donor annotation's experimental evidence.

Empirical comparisons have not justified a categorical winner. Studies using
different functional datasets and bias controls have reported different effect
sizes, while agreeing that neither orthology nor sequence similarity alone is
an exact function predictor.

## SeqEvi evidence boundary

For a Pfam-backed adapter, a `hit` records that at least one signature match was
accepted under one exact runtime, resource, parameter set, and result contract.
Each accepted region may be represented as its own native evidence row.

A `no_hit` state means that no candidate result met those exact acceptance
conditions. It does not mean that the sequence has no domain or function, and
it does not classify the whole sequence as statistically non-significant.

## Sources

- [InterPro entries: essential information](https://interpro-documentation.readthedocs.io/en/latest/entries_info.html)
- [EMBL-EBI Training: What are protein signatures?](https://www.ebi.ac.uk/training/online/courses/protein-classification-intro-ebi-resources/what-are-protein-signatures/)
- [Testing the Ortholog Conjecture with Comparative Functional Genomic Data from Mammals](https://doi.org/10.1371/journal.pcbi.1002073)
- [Resolving the Ortholog Conjecture](https://doi.org/10.1371/journal.pcbi.1002514)

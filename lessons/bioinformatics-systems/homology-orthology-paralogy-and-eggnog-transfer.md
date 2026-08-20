# Homology, orthology, paralogy, and eggNOG transfer

## Relationship hierarchy

`Homolog` states that two genes or proteins descend from a common ancestral
gene. `Ortholog` and `paralog` refine that relationship by the evolutionary
event that separates the pair:

```text
homolog
  -> ortholog when the separating event is speciation
  -> paralog when the separating event is gene duplication
```

Homology is not a percentage. Sequence identity, alignment score, and E-value
provide evidence for common ancestry; they do not themselves classify a pair
as orthologous or paralogous.

## Duplication before speciation

```text
ancestral G
  -> duplication: A and B
  -> speciation:  A_X, A_Y, B_X, B_Y
```

`A_X` and `A_Y` are orthologs. `A_X` and `B_Y` are paralogs even though they
occur in different species, because the event separating the `A` and `B`
lineages was duplication.

## Functional-transfer risk

Orthologs often retain ancestral function more reliably because both species
continue to depend on the inherited copy. Duplication creates redundancy that
can permit neofunctionalization, subfunctionalization, expression divergence,
or loss. This makes precise function transfer from a paralog riskier.

Neither category is a proof of function. One-to-one orthology generally gives
a clearer correspondence than one-to-many or many-to-many orthology, while
taxonomic distance, donor evidence quality, alignment coverage, conserved key
residues, and domain architecture remain relevant.

## The eggNOG-mapper boundary

```text
query sequence
  -> sequence mapping and seed match
  -> orthologous-group lookup
  -> precomputed phylogeny refinement
  -> taxonomic-scope restriction
  -> ortholog-type donor selection
  -> annotation transfer
```

The seed match is an entry point into precomputed evolutionary context, not by
itself a proven functionally identical donor. A strict E-value can reject weak
or random matches but cannot remove all paralogs, because paralogs can retain
very strong sequence similarity.

Changing taxonomic scope or eligible ortholog type can change annotation donors
and final hit/no-hit or label outcomes. Those settings are therefore semantic
parameters for exact SeqEvi evidence reuse.

## SeqEvi interpretation

A SeqEvi eggNOG `hit` proves that the external computation completed and the
adapter accepted terminal evidence under one exact EvidenceKey. It does not
prove that every transferred function is experimentally true.

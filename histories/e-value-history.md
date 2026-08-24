---
schema_version: 1
id: e-value-history
title: History of the sequence-search E-value
summary: How random-sequence significance theory was applied to BLAST and refined for gapped search practice.
concepts: []
lessons:
  - lessons/bioinformatics-systems/alignment-score-bit-score-evalue.md
tracks:
  - bioinformatics-systems
milestones:
  - id: karlin-altschul-1990
    year: 1990
    month: 3
    day: null
    kind: formalization
    actors:
      - Samuel Karlin
      - Stephen F. Altschul
    claim: Karlin and Altschul formulated a random-sequence theory for assessing high-scoring sequence regions, including a no-gap pairwise local-alignment result under stated assumptions.
    evidence_basis: primary-source
    sources:
      - url: https://doi.org/10.1073/pnas.87.6.2264
        title: Methods for assessing the statistical significance of molecular sequence features by using general scoring schemes
        publisher: Proceedings of the National Academy of Sciences
        role: primary
        kind: paper
  - id: blast-1990
    year: 1990
    month: 10
    day: null
    kind: adoption
    actors:
      - Stephen F. Altschul
      - Warren Gish
      - Webb Miller
      - Eugene W. Myers
      - David J. Lipman
    claim: The original BLAST paper applies stochastic results on maximal segment-pair scores to analyze the statistical significance of alignments produced by the method.
    evidence_basis: primary-source
    sources:
      - url: https://doi.org/10.1016/S0022-2836(05)80360-2
        title: Basic local alignment search tool
        publisher: Journal of Molecular Biology
        role: primary
        kind: paper
  - id: gapped-blast-1997
    year: 1997
    month: 9
    day: 1
    kind: revision
    actors:
      - Stephen F. Altschul
      - Thomas L. Madden
      - Alejandro A. Schäffer
      - Jinghui Zhang
      - Zheng Zhang
      - Webb Miller
      - David J. Lipman
    claim: The 1997 Gapped BLAST and PSI-BLAST paper presents algorithmic and statistical refinements for gapped alignments and relates E-values to the effective search space.
    evidence_basis: primary-source
    sources:
      - url: https://doi.org/10.1093/nar/25.17.3389
        title: "Gapped BLAST and PSI-BLAST: a new generation of protein database search programs"
        publisher: Nucleic Acids Research
        role: primary
        kind: paper
---

## Historical setting

Karlin and Altschul's 1990 paper asks how to assess the statistical
significance of high-scoring sequence regions under an explicit random model.
It presents results for those regions and a no-gap pairwise local-alignment
variation. This dossier therefore begins with a documented statistical
formulation, not an inferred scene or motive for why the authors began the
work.

## What the sources establish

The [1990 statistical paper](https://doi.org/10.1073/pnas.87.6.2264)
derives results under a random-sequence model with conditions on residue
frequencies and scoring. The
[original BLAST paper](https://doi.org/10.1016/S0022-2836(05)80360-2)
uses recent stochastic results to assess the significance of maximal
segment-pair scores produced by the search method. The
[1997 Gapped BLAST and PSI-BLAST paper](https://doi.org/10.1093/nar/25.17.3389)
then describes algorithmic and statistical refinements for gapped and iterative
search practice.

## What the sources do not establish

The 1990 milestone is limited here to the paper's stated random-model results
and no-gap pairwise variation. The 1997 paper separately says the relevant
theory had not been proved for gapped local alignments, uses estimated
statistical parameters for that setting, and identifies biased composition as
a risk in iterative PSI-BLAST use. The original BLAST paper does not establish
every convention of a current BLAST report.

## Development

The historical development separates three steps that modern interfaces often
present together:

```text
random-model significance theory
  -> significance analysis for BLAST segment-pair scores
  -> refined estimation for gapped and iterative database searches
```

Database size, effective search space, scoring system, and model assumptions
therefore belong to the interpretation, not merely to display formatting.

## Modern boundary

The 1997 paper defines its E-value as the expected number of chance HSPs at or
above a normalized score for an effective search space. For this repository's
modern teaching boundary, that expected count under a model is not a posterior
probability of functional correctness. Because the papers make the random
model, search space, scoring system, gaps, and estimated parameters material to
the calculation, results from different search configurations should not be
treated as automatically equivalent.

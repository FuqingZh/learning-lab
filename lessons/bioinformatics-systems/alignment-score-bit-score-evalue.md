# Alignment score, bit score, and E-value

## Causal ladder

```text
aligned residues and gaps
  -> raw score under one substitution matrix and gap scheme
  -> bit score normalized for that scoring system
  -> E-value after accounting for the effective search space
```

Raw score measures one alignment under a particular substitution matrix and
gap-penalty scheme. Scores from different schemes are not directly comparable.

Bit score statistically normalizes the raw score. Higher bit scores indicate
stronger matches. Under the standard model, adding one bit approximately halves
the expected number of equally strong chance matches when the search space is
unchanged.

The simplified relationship is:

```text
E approximately equals effective query length
  * effective database size
  * 2^(-bit score)
```

E-value is the expected number of chance matches scoring at least as well in
the defined search. Increasing the database size increases the number of random
matching opportunities: an unchanged alignment searched against a database 100
times larger retains its raw and bit scores but has an E-value approximately
100 times larger.

E-value is not the probability that a function is wrong. Under a Poisson
approximation, the probability of at least one such chance match is
`1 - exp(-E)`, which is approximately `E` only for very small E. Expected counts
add across searches, but they do not identify which observations are random.

Percent identity must be interpreted with alignment length, coverage,
substitution pattern, sequence complexity, bit score, and E-value. A very short
high-identity match can be less significant than a long lower-identity match.

An E-value threshold is a semantic parameter in SeqEvi because changing it can
change whether an exact computation produces `hit` or `no_hit`; evidence from a
different threshold is not exactly reusable.

---
Status: superseded by [alignment significance mastery](0009-alignment-significance-mastered.md)
---

# Alignment significance is developing

The learner correctly explains that moving the same alignment into a database
100 times larger leaves its raw score and bit score unchanged while increasing
its E-value by approximately 100 times. The learner also understands why
percent identity must be interpreted with alignment length and coverage, and
correctly classifies an E-value threshold as a semantic parameter that can
change hit/no-hit status and invalidate exact evidence reuse.

One statistical boundary still requires unaided retrieval: an E-value is the
expected number of chance matches scoring at least as well in the defined
search, not directly the probability that such a match appears and not the
probability that the annotation is wrong. Under a Poisson approximation, the
probability of at least one such chance match is `1 - exp(-E)`, which is only
approximately equal to `E` when `E` is very small.

## Evidence

In the first alignment-significance check, the learner answered the score,
database-size, coverage, semantic-parameter, and cache-reuse cases correctly,
but described `E = 1e-20` as the probability of observing such significance
under randomness rather than as an expected count.

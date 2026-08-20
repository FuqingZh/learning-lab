# Alignment significance is understood

The learner can distinguish raw alignment score, normalized bit score, and
E-value. The learner explains that moving an unchanged alignment into a search
database 100 times larger leaves raw and bit scores unchanged while increasing
the E-value by approximately 100 times.

The learner also understands that alignment length and coverage prevent percent
identity from being interpreted alone, and that an E-value threshold is a
semantic parameter because it can change hit/no-hit classification.

The statistical boundary is now retrieved correctly: E-value is an expected
number of chance matches at least as strong as the observed match, not a direct
probability and not a functional-annotation error rate. Expected counts add
across searches, but they do not identify which matches or annotations are
wrong.

## Evidence

Given 200 searches with `E = 0.05` per search, the learner correctly calculated
an aggregate expectation of 10 random matches and stated that this does not
establish the number of incorrect functional annotations.

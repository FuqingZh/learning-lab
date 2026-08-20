# Layers, boundaries, and invariants are understood

The learner can distinguish a layer's responsibility, the contract at its
boundary, and the invariant that downstream components are allowed to assume.
The learner diagnoses an end-to-end failure at the first boundary that admitted
invalid state rather than at the final place where the error became visible.

## Evidence

In unaided application on 2026-08-20, the learner classified a report generated
from an invalid date as an unsuccessful system outcome even though computation,
database persistence, and delivery all completed operationally. The learner
located the first violated invariant at the input layer, which silently changed
an invalid date to null instead of rejecting it, and explained that downstream
execution success cannot establish correctness when its input assumptions were
already false.

This demonstrates the distinction between operational completion and semantic
correctness, together with the rule to diagnose the earliest broken boundary.

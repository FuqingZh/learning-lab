# Exact evidence reuse cases are classified correctly

The learner correctly classified five cache cases: changed FASTA labels reuse
the same evidence; a changed annotation database requires new evidence; a
successful no-hit is reusable; a timeout is not cacheable and must be retried;
and a thread-count-only change remains reusable when the upstream tool
guarantees unchanged scientific semantics. This establishes practical
classification of exact reuse, while causal explanation and unaided recall of
the complete EvidenceKey remain to be demonstrated.

## Evidence

The learner answered all five first-lesson retrieval cases correctly on
2026-08-14.

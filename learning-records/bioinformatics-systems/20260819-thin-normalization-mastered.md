# Thin normalization is understood

The learner can distinguish representation-preserving normalization from
semantic transformation. The learner understands that an adapter may normalize
required scalar types, null values, encodings, and canonical sequence linkage
while preserving the upstream row grain, field meanings, and reconstructable
match relationships.

The learner also understands that mechanically compatible schemas do not make
different adapter fields semantically comparable. An eggNOG seed-alignment
E-value and a Pfam region-to-profile-HMM E-value describe different statistical
experiments, hypotheses, models, search spaces, and row grains. Renaming both to
a universal `evidence_strength` and merging them would invent a cross-tool
ontology rather than perform thin normalization.

## Evidence

In unaided application on 2026-08-19, the learner:

- rejected collapsing multiple Pfam domain-match rows into a comma-separated
  protein row because it changed row grain and deleted reconstructable
  coordinates;
- accepted parsing a Pfam E-value string into a numeric scalar while retaining
  the original field meaning and match row; and
- rejected merging eggNOG and Pfam E-values into one comparable field because
  their result semantics and schemas are not interchangeable.

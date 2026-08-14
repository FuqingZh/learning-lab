# Bioinformatics Systems Glossary

Canonical language that the learner has demonstrated in the SeqEvi learning
track. Terms are added only after they can be applied and explained.

## Sequence and evidence identity

**Sequence-level reuse**:
Reusing annotation by canonical protein-sequence content rather than by FASTA
filename, project, header, or input identifier.
_Avoid_: File-level cache, project-level annotation identity

**Exact evidence reuse**:
Reusing a result only when the sequence and the complete result-affecting
annotation contract are identical; a matching human-readable tool version alone
is insufficient.
_Avoid_: Same-version reuse, latest-compatible reuse

**Semantic parameter**:
An annotation setting whose value can change the scientific result, such as an
E-value threshold, taxonomic scope, or search mode.
_Avoid_: Scientific parameter version

**Operational parameter**:
A setting that changes how computation runs but, under the upstream tool's
declared contract, does not change its scientific result, such as thread count
or a temporary directory.
_Avoid_: Nonessential parameter

## Evidence states

**Reusable terminal evidence**:
A successfully completed, validated annotation outcome for one exact evidence
identity; both a hit and a successful no-hit can be terminal evidence.
_Avoid_: Any finished process, any stored output

**No-hit**:
A successful annotation outcome stating that no evidence row was found under
the exact sequence, runtime, resource, adapter, and semantic-parameter contract.
_Avoid_: Empty error, failed annotation

**Operational failure**:
A run that did not produce a valid scientific terminal outcome, for example a
timeout, crash, malformed output, or adapter rejection; it cannot be reused as
annotation evidence.
_Avoid_: Negative result, no-hit

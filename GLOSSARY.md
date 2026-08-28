# Bioinformatics Systems Glossary

This glossary contains only established, transferable professional terms. It
does not assert that a learner has demonstrated any of them; demonstrated
capability belongs to learning records. The admission evidence and 2026-08-27
decisions are in [the terminology audit](docs/audits/20260827-terminology-audit.md).
Repository-specific explanatory language is kept separately in
[repository vocabulary](docs/reference/repository-vocabulary.md).

## Sequence analysis and functional annotation

**Profile HMM**:
A probabilistic model of a sequence family, typically built from a multiple
sequence alignment, that represents position-specific residue and indel
patterns for sequence search and alignment.

**Annotation transfer**:
The inference and assignment of functional annotations to a target sequence
from evidence associated with related, classified, or otherwise eligible
reference sequences. A transferred annotation is inferred evidence, not a
direct measurement of the target.

**Homolog**:
A gene or protein related to another by common evolutionary ancestry.
Homology is a relationship, not a percentage; orthology and paralogy are
particular evolutionary relationships among homologs.

**Ortholog**:
A homologous gene or protein whose divergence is attributed to a speciation
event. Orthology can support functional inference but does not establish
identical function.

**Paralog**:
A homologous gene or protein whose divergence is attributed to a gene-duplication
event. Paralogs can occur within or across species and may retain or diverge in
function.

**Raw score**:
The score assigned to an alignment by a specified substitution matrix and gap
scheme. It is meaningful only with that scoring system; *raw alignment score*
is the repository's earlier descriptive alias.

**Bit score**:
A normalized alignment score that incorporates the statistical parameters of
the scoring system, allowing comparison across compatible search settings.

**E-value**:
The expected number of chance matches with a score at least as good as the
observed match in the stated search space. It is neither a functional-annotation
error rate nor the probability that a match is random.

## Systems and security

**State invariant**:
A predicate over system state that must hold in every permitted reachable
state, and is therefore preserved by allowed state transitions.

**Content hash**:
A cryptographic digest of content used to identify or verify exact bytes under
a stated hash algorithm. Equal digests are evidence about bytes under that
contract, not authorization or scientific equivalence.

**Sandbox**:
A controlled execution environment that restricts the resources and privileges
available to code. Sandboxing does not itself decide whether a request is
authorized.

**Authentication**:
The process of establishing the identity or claimed identity of a principal
from trusted evidence. It is distinct from deciding what that principal may do.

**Authorization**:
The decision whether a principal may perform a requested action on a resource
in a given context. It is commonly made after authentication, but its policy
and enforcement boundary are distinct from identity establishment.

**Confused deputy**:
A vulnerability in which a more-privileged program is induced to use its own
authority on behalf of a less-privileged caller in a way the caller is not
authorized to request.

**Idempotency**:
The property that repeating the same requested operation has the same intended
server effect as performing it once. It does not require identical response
bytes or exactly-once delivery.

**Side effect**:
An observable effect of evaluating an expression or performing an operation
beyond producing its value, such as changing state, performing I/O, or consuming
a resource.

**Idempotency key**:
A client-supplied value that lets a resource recognize retries of one logical
request. Its scope, lifetime, and request-fingerprint rules are defined by the
operation that owns it.

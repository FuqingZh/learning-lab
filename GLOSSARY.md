# Bioinformatics Systems Glossary

Canonical language that the learner has demonstrated across the active learning
tracks. Terms are added only after they can be applied and explained; section
headings retain the context in which a term was established.

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

## Adapter boundaries

**Tool runtime identity**:
The immutable digest of the resolved external annotation runtime. It is a
separate EvidenceKey coordinate from the adapter contract version: changing an
executable environment does not inherently change the adapter's parsing and
evidence-semantics contract.
_Avoid_: Adapter runtime, executable path identity

## Bioinformatics search

**Profile HMM**:
A statistical sequence-family model estimated from a multiple sequence
alignment. It represents position-specific amino-acid probabilities and
transitions among match, insertion, and deletion states; it does not contain
protein atomic coordinates.
_Avoid_: Protein spatial model, three-dimensional HMM

**Annotation transfer**:
Assigning eligible annotations to a query through an inferred relationship to
annotated reference proteins or orthologous groups. The transferred label is
inferred evidence, not a direct measurement on the query.
_Avoid_: Direct domain scan, experimentally verified function

**Homolog**:
One of a pair of genes or proteins inferred to descend from a common ancestral
gene. Homology is a relationship, not a percentage; orthologs and paralogs are
event-specific homologous relationships.
_Avoid_: Percent homology, any similar sequence

**Ortholog**:
One of a pair of homologs whose separating evolutionary event is speciation.
Orthology generally strengthens functional-transfer confidence but does not
prove identical function.
_Avoid_: Best sequence hit, same function

**Paralog**:
One of a pair of homologs whose separating evolutionary event is gene
duplication. Paralogs can occur in different species and may retain or diverge
from their ancestral function.
_Avoid_: Same-species homolog, necessarily different function

**Orthology-aware annotation transfer**:
Selecting annotation donors through inferred orthology, taxonomic scope, and
ortholog type rather than transferring directly from a raw similarity hit.
_Avoid_: Best-hit annotation, E-value-only transfer

**Raw alignment score**:
The score of one alignment under a particular substitution matrix and gap
penalty scheme. It measures the alignment within that scoring system and is not
generally comparable across different systems.
_Avoid_: Match probability, universal alignment score

**Bit score**:
A statistically normalized form of an alignment score. Higher values indicate
stronger matches; unlike raw scores, bit scores are calibrated for comparison
across compatible search settings.
_Avoid_: Percent identity, E-value

**E-value**:
The expected number of chance matches scoring at least as well as the observed
match in the defined search space. It is not a functional-annotation error rate
and is not directly the probability of a random match.
_Avoid_: Error probability, homology probability

## AI scientific system boundaries

**Structural validity**:
An input satisfies the encoded type, presence, range, enumeration, and shape
assertions of a contract. It does not establish cross-field domain consistency
or facts outside that contract.
_Avoid_: Correct request, correct content

**Domain invariant**:
A relationship that must hold among otherwise structurally valid values for an
operation to be meaningful in its domain.
_Avoid_: Field type, scientific correctness

**State invariant**:
A constraint over authoritative current or historical system state that must
remain true for a state transition to be allowed.
_Avoid_: Schema rule, successful execution

**Scientific correctness**:
The extent to which methods, assumptions, evidence, and interpretation support
a scientific claim. It is not established merely by structural, domain, state,
or artifact gates passing.
_Avoid_: Successful execution, valid artifact

**Deterministic gate**:
A platform-owned check that accepts or rejects a request or artifact against
explicit rules. Passing it proves only those rules, not broader scientific
correctness.
_Avoid_: Correctness proof, model confidence check

**User feedback**:
A user's evaluation signal about an output or experience. It can guide later
evaluation and improvement but is not, by itself, scientific validation.
_Avoid_: Ground truth, scientific acceptance

**Opaque capability reference**:
A caller-visible token passed back to select an authorized resource while its
meaning is resolved server-side in an authenticated context.
_Avoid_: Encoded data, data summary, content identity

**Data descriptor**:
Derived metadata such as columns and summaries that describes a dataset's
shape without serving as its raw content or access authority.
_Avoid_: Dataset handle, dataset bytes

**Content hash**:
A cryptographic digest used as evidence that exact bytes are identical under
the same hashing contract; it does not establish authorization or scientific
equivalence.
_Avoid_: Dataset handle, semantic identity

**Sandbox**:
A constrained execution environment that limits what running code can access
and modify; it does not decide whether an input is authorized.
_Avoid_: Dataset handle, complete security proof

**Authentication**:
Establishing which principal a request represents from trusted evidence. It
does not decide what that principal may do.
_Avoid_: Authorization, user-provided identity field

**Authorization**:
Deciding whether an authenticated principal may perform a particular action on
a particular resource in the current context.
_Avoid_: Authentication, resource identity

**Confused deputy**:
A more privileged service induced by a caller to apply the service's own
authority to a resource or purpose the caller was not authorized to request.
_Avoid_: Sandbox escape, ordinary validation error

**Idempotency**:
The property that repeating the same logical operation produces the same final
intended business effect as performing it once.
_Avoid_: Identical response bytes, request delivered exactly once

**Side effect**:
An externally observable state change caused by an operation, such as creating
a Job, updating a database record, consuming quota, or writing a result file.
_Avoid_: Return value, internal calculation

**Idempotency key**:
A stable identifier for one logical operation across multiple request attempts;
a genuinely new operation requires a new key.
_Avoid_: Identifier for one network attempt, reusable operation type

**Retry-safe**:
An operation can be attempted again after an uncertain response without
duplicating its intended side effects.
_Avoid_: Guaranteed success, request executed only once

**Operation scope**:
The operation type or namespace within which an idempotency key identifies one
logical operation; the same key in different scopes does not denote the same
operation.
_Avoid_: Workflow stage, global meaning of a key string

# Repository Vocabulary

These labels are descriptive language used to explain this repository's
workflows. They are intentionally **not canonical glossary terms**, should not
be promoted to `concepts/` merely because they appear here, and do not state a
learner capability.

## Evidence and execution descriptions

**Sequence-level reuse**: Reusing annotation by canonical protein-sequence
content rather than by FASTA filename, project, header, or input identifier.

**Exact evidence reuse**: Reusing a result only when the sequence and complete
result-affecting annotation contract are identical; a matching human-readable
tool version alone is insufficient.

**Semantic parameter**: An annotation setting whose value can change the
scientific result, such as an E-value threshold, taxonomic scope, or search
mode.

**Operational parameter**: A setting that changes how computation runs but,
under the upstream tool's declared contract, does not change its scientific
result, such as thread count or a temporary directory.

**Reusable terminal evidence**: A successfully completed, validated annotation
outcome for one exact evidence identity; both a hit and a successful no-hit can
be terminal evidence.

**No-hit**: A successful annotation outcome stating that no evidence row was
found under the exact sequence, runtime, resource, adapter, and
semantic-parameter contract.

**Operational failure**: A run that did not produce a valid scientific terminal
outcome, for example a timeout, crash, malformed output, or adapter rejection;
it cannot be reused as annotation evidence.

**Tool runtime identity**: The immutable digest of the resolved external
annotation runtime. It is separate from the adapter-contract version: changing
an executable environment does not inherently change parsing and
evidence-semantics rules.

**Orthology-aware annotation transfer**: Selecting annotation donors through
inferred orthology, taxonomic scope, and ortholog type rather than transferring
directly from a raw similarity hit.

**Raw alignment score**: A descriptive legacy alias for the established term
*raw score*. The canonical definition is retained in
[`GLOSSARY.md`](../../GLOSSARY.md); this longer phrase is not treated as a
separate professional term.

## Validation and interface descriptions

**Structural validity**: An input satisfies encoded type, presence, range,
enumeration, and shape assertions. It does not establish cross-field domain
consistency or facts outside that contract.

**Domain invariant**: A relationship that must hold among otherwise
structurally valid values for an operation to be meaningful in its domain.

**Scientific correctness**: The extent to which methods, assumptions,
evidence, and interpretation support a scientific claim. It is not established
merely by structural, domain, state, or artifact gates passing.

**Deterministic gate**: A platform-owned check that accepts or rejects a request
or artifact against explicit rules. Passing it proves only those rules, not
broader scientific correctness.

**User feedback**: A user's evaluation signal about an output or experience.
It can guide later evaluation and improvement but is not, by itself, scientific
validation.

**Opaque capability reference**: A caller-visible token passed back to select
an authorized resource while its meaning is resolved server-side in an
authenticated context.

**Data descriptor**: Derived metadata such as columns and summaries that
describes a dataset's shape without serving as its raw content or access
authority.

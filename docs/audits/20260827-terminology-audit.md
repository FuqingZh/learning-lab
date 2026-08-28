# 2026-08-27 Terminology Audit

## Decision

The prior glossary mixed 33 labels from three different roles: established
professional terms, repository design shorthand, and teaching explanations.
Only an established term with two independent, authoritative sources remains a
canonical glossary headword. This audit was checked on **2026-08-27**. The
original 33 headings resolve to 16 retained names and 17 demoted descriptive
labels, including one renamed legacy alias. The resulting canonical glossary has 17
terms because **Raw score** replaces the earlier wording **Raw alignment
score**. The descriptive vocabulary and aliases are not evidence that a learner
has demonstrated a capability.

The source pairs below are provenance for terminology admission, not a claim
that the linked organizations endorse this repository's particular workflow.

## Retained canonical terms

| Canonical term | Decision and scope | Independent source 1 | Independent source 2 |
| --- | --- | --- | --- |
| Profile HMM | Retain; established sequence-family model. | [Eddy paper, *Bioinformatics* (Oxford University Press)](https://pubmed.ncbi.nlm.nih.gov/9918945/) | [Pfam glossary, EMBL-EBI](https://pfam-docs.readthedocs.io/en/latest/glossary.html) |
| Annotation transfer | Retain; define as *functional annotation transfer* in prose where specificity helps. | [UniProt automatic annotation](https://www.uniprot.org/help/automatic_annotation) | [Genome Research article, Cold Spring Harbor Laboratory Press](https://pmc.ncbi.nlm.nih.gov/articles/PMC311165/) |
| Homolog | Retain; evolutionary relationship, not a similarity percentage. | [NCBI Bookshelf: Homology](https://www.ncbi.nlm.nih.gov/books/NBK20255/) | [Genome Biology: OrthoFinder](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-019-1832-y) |
| Ortholog | Retain; divergence through speciation. | [NCBI Bookshelf: Homology](https://www.ncbi.nlm.nih.gov/books/NBK20255/) | [Genome Biology: OrthoFinder](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-019-1832-y) |
| Paralog | Retain; divergence through duplication. | [NCBI Bookshelf: Homology](https://www.ncbi.nlm.nih.gov/books/NBK20255/) | [Genome Biology: OrthoFinder](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-019-1832-y) |
| Raw score | Retain. The earlier phrase *Raw alignment score* is a descriptive legacy alias, not a canonical entry. | [NCBI BLAST glossary](https://www.ncbi.nlm.nih.gov/books/NBK62051/) | [EMBL-EBI similarity-search training](https://www.ebi.ac.uk/training/online/courses/guide-to-sequence-analysis-tools/sequence-alignment/sequence-similarity-search/) |
| Bit score | Retain; normalized score with stated comparability limits. | [NCBI BLAST glossary](https://www.ncbi.nlm.nih.gov/books/NBK62051/) | [EMBL-EBI similarity-search training](https://www.ebi.ac.uk/training/online/courses/guide-to-sequence-analysis-tools/sequence-alignment/sequence-similarity-search/) |
| E-value | Retain; expected chance matches in a defined search space. | [NCBI BLAST FAQ](https://blast.ncbi.nlm.nih.gov/doc/blast-help/FAQ.html) | [EMBL-EBI similarity-search training](https://www.ebi.ac.uk/training/online/courses/guide-to-sequence-analysis-tools/sequence-alignment/sequence-similarity-search/) |
| State invariant | Retain; a formal-methods term for a predicate preserved over permitted states. | [Microsoft Research: *Specifying Systems* chapter](https://www.microsoft.com/en-us/research/wp-content/uploads/2008/01/bookChapterOnSE.pdf) | [NASA technical report](https://ntrs.nasa.gov/citations/19940011063) |
| Content hash | Retain; a cryptographic digest of exact bytes under a specified algorithm. | [NIST Secure Hash Standard](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) | [IETF RFC 6234](https://www.rfc-editor.org/rfc/rfc6234) |
| Sandbox | Retain; controlled restricted execution environment. | [NIST CSRC glossary](https://csrc.nist.gov/glossary/term/sandbox) | [Apple App Sandbox](https://developer.apple.com/documentation/security/app-sandbox) |
| Authentication | Retain; establish a principal's identity or claimed identity. | [NIST SP 800-63-4](https://pages.nist.gov/800-63-4/sp800-63.html) | [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) |
| Authorization | Retain; decide what a principal may do in context; it is distinct from identity establishment. | [NIST SP 800-162](https://csrc.nist.gov/pubs/sp/800/162/upd2/final) | [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) |
| Confused deputy | Retain; a named authority-confusion vulnerability. | [Hardy, *The Confused Deputy*](https://www.cis.upenn.edu/~KeyKOS/ConfusedDeputy.html) | [MITRE CWE-441](https://cwe.mitre.org/data/definitions/441.html) |
| Idempotency | Retain; same intended request effect under repetition. | [IETF RFC 9110, §9.2.2](https://www.rfc-editor.org/rfc/rfc9110#section-9.2.2) | [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/2025-02-25/framework/rel_prevent_interaction_failure_idempotent.html) |
| Side effect | Retain; observable effect beyond evaluating a value. | [ISO C draft N1570, §5.1.2.3](https://www.iso-9899.info/n1570.html#5.1.2.3) | [MDN Glossary: side effect](https://developer.mozilla.org/en-US/docs/Glossary/Side_effect) |
| Idempotency key | Retain; a request-retry correlation value whose scope is operation-defined. The [IETF working-group draft](https://datatracker.ietf.org/doc/html/draft-ietf-httpapi-idempotency-key-header) is historical context, not admission evidence. | [Stripe API reference](https://docs.stripe.com/api/idempotent_requests) | [AWS ECS developer guide](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_Idempotency.html) |

## Demoted descriptive vocabulary

The following phrases are useful repository explanations but fail the canonical
terminology gate as exact, transferable professional headwords. They now live
in the descriptive vocabulary rather than `GLOSSARY.md` or `concepts/`.

| Original label | Decision / destination |
| --- | --- |
| Sequence-level reuse | Demote to descriptive repository vocabulary. |
| Exact evidence reuse | Demote to descriptive repository vocabulary. |
| Semantic parameter | Demote to descriptive repository vocabulary. |
| Operational parameter | Demote to descriptive repository vocabulary. |
| Reusable terminal evidence | Demote to descriptive repository vocabulary. |
| No-hit | Demote to descriptive repository vocabulary. |
| Operational failure | Demote to descriptive repository vocabulary. |
| Tool runtime identity | Demote to descriptive repository vocabulary. |
| Orthology-aware annotation transfer | Demote to descriptive repository vocabulary. |
| Raw alignment score | Demote to a descriptive alias for the canonical term **Raw score** in [repository vocabulary](../reference/repository-vocabulary.md). |
| Structural validity | Demote to descriptive repository vocabulary. |
| Domain invariant | Demote to descriptive repository vocabulary. |
| Scientific correctness | Demote to descriptive repository vocabulary. |
| Deterministic gate | Demote to descriptive repository vocabulary. |
| User feedback | Demote to descriptive repository vocabulary. |
| Opaque capability reference | Demote to descriptive repository vocabulary. |
| Data descriptor | Demote to descriptive repository vocabulary. |

## Original-label disposition ledger

This ledger accounts for every one of the original 33 headings and makes the
only rename explicit.

| # | Original label | Disposition |
| ---: | --- | --- |
| 1 | Sequence-level reuse | Demoted to descriptive vocabulary. |
| 2 | Exact evidence reuse | Demoted to descriptive vocabulary. |
| 3 | Semantic parameter | Demoted to descriptive vocabulary. |
| 4 | Operational parameter | Demoted to descriptive vocabulary. |
| 5 | Reusable terminal evidence | Demoted to descriptive vocabulary. |
| 6 | No-hit | Demoted to descriptive vocabulary. |
| 7 | Operational failure | Demoted to descriptive vocabulary. |
| 8 | Tool runtime identity | Demoted to descriptive vocabulary. |
| 9 | Profile HMM | Retained in canonical glossary. |
| 10 | Annotation transfer | Retained in canonical glossary. |
| 11 | Homolog | Retained in canonical glossary. |
| 12 | Ortholog | Retained in canonical glossary. |
| 13 | Paralog | Retained in canonical glossary. |
| 14 | Orthology-aware annotation transfer | Demoted to descriptive vocabulary. |
| 15 | Raw alignment score | Demoted to descriptive alias; canonical glossary headword is **Raw score**. |
| 16 | Bit score | Retained in canonical glossary. |
| 17 | E-value | Retained in canonical glossary. |
| 18 | Structural validity | Demoted to descriptive vocabulary. |
| 19 | Domain invariant | Demoted to descriptive vocabulary. |
| 20 | State invariant | Retained in canonical glossary. |
| 21 | Scientific correctness | Demoted to descriptive vocabulary. |
| 22 | Deterministic gate | Demoted to descriptive vocabulary. |
| 23 | User feedback | Demoted to descriptive vocabulary. |
| 24 | Opaque capability reference | Demoted to descriptive vocabulary. |
| 25 | Data descriptor | Demoted to descriptive vocabulary. |
| 26 | Content hash | Retained in canonical glossary. |
| 27 | Sandbox | Retained in canonical glossary. |
| 28 | Authentication | Retained in canonical glossary. |
| 29 | Authorization | Retained in canonical glossary. |
| 30 | Confused deputy | Retained in canonical glossary. |
| 31 | Idempotency | Retained in canonical glossary. |
| 32 | Side effect | Retained in canonical glossary. |
| 33 | Idempotency key | Retained in canonical glossary. |

The new canonical term **Raw score** was not an original glossary heading. The
original phrase **Raw alignment score** is retained only as its descriptive
legacy alias.

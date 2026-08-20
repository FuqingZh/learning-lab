# Bioinformatics Systems Resources

## Knowledge

- [NCBI Bookshelf: Protein Function — Molecular Biology of the Cell](https://www.ncbi.nlm.nih.gov/books/NBK26911/)
  Publisher: NCBI Bookshelf; Alberts et al. Historical foundational textbook
  context. Checked: 2026-08-14. Use for: the sequence-structure-function chain,
  binding chemistry, protein domains, and evolutionary conservation.
- [NCBI Bookshelf: BLAST QuickStart](https://www.ncbi.nlm.nih.gov/books/NBK1734/)
  Publisher: NCBI Bookshelf; Wheeler and Bhagwat. Historical algorithmic
  introduction. Checked: 2026-08-14. Use for: query/subject alignment,
  substitution matrices, gaps, local similarity, and E-value interpretation;
  re-check modern software defaults elsewhere before operational use.
- [NCBI Bookshelf: Evolutionary Concept in Genetics and Genomics](https://www.ncbi.nlm.nih.gov/books/NBK20255/)
  Publisher: NCBI Bookshelf; Koonin and Galperin. Historical foundational
  treatment checked: 2026-08-19. Use for: homology, orthology, paralogy,
  duplication/speciation event trees, co-orthology, gene loss, and the limits
  of functional transfer.
- [Testing the Ortholog Conjecture with Comparative Functional Genomic Data from Mammals](https://doi.org/10.1371/journal.pcbi.1002073)
  Publisher: PLOS Computational Biology; Nehrt et al. Primary comparative
  study checked: 2026-08-19. Use for: how sequence identity, paralog type,
  organismal context, and functional measurements complicate a universal
  ortholog-first rule for function prediction.
- [Resolving the Ortholog Conjecture](https://doi.org/10.1371/journal.pcbi.1002514)
  Publisher: PLOS Computational Biology; Altenhoff et al. Primary comparative
  study checked: 2026-08-19. Use for: bias-aware empirical support that
  orthologs are on average only weakly more functionally similar than paralogs,
  rather than guaranteed functionally equivalent.
- [UniProtKB Help](https://www.uniprot.org/help/uniprotkb)
  Publisher: UniProt Consortium. Current help page checked: 2026-08-14. Use for:
  manual versus computational annotation, evidence attribution, and the range
  of information attached to protein records.
- [UniProt Automatic Annotation](https://www.uniprot.org/help/automatic_annotation)
  Publisher: UniProt Consortium. Page last modified: 2024-03-22. Checked:
  2026-08-14. Use for: signature-based classification, InterPro integration,
  automatic rules, and sequence-feature prediction.
- [InterPro Entries: essential information](https://interpro-documentation.readthedocs.io/en/latest/entries_info.html)
  Publisher: EMBL-EBI InterPro. Applies to: current latest documentation checked
  2026-08-14. Use for: families, domains, sites, repeats, homologous
  superfamilies, member-database signatures, and InterPro integration.
- [EMBL-EBI Training: What are protein signatures?](https://www.ebi.ac.uk/training/online/courses/protein-classification-intro-ebi-resources/what-are-protein-signatures/)
  Publisher: EMBL-EBI Training. Current training page checked: 2026-08-19. Use
  for: distinguishing biological protein features from the computational
  models that detect them, and how multiple-sequence alignments and conserved
  positions are used to construct predictive signatures.
- [eggNOG-mapper v2](https://doi.org/10.1093/molbev/msab293)
  Publisher: Molecular Biology and Evolution; Cantalapiedra et al. Applies to:
  the published eggNOG-mapper v2 workflow. Checked: 2026-08-19. Use for:
  sequence mapping, precomputed phylogeny-based orthology refinement, taxonomic
  scope, functional transfer, and transferred versus de novo Pfam annotation.
- [SeqEvi v1 Architecture](https://github.com/FuqingZh/seqevi/blob/main/docs/architecture/20260720-v1.0-seqevi-architecture.md)
  Publisher: SeqEvi project. Applies to: approved v1 target architecture, with
  its result-delivery section superseded by the v1.1 DuckDB contract. Checked:
  2026-08-14. Use for: system purpose, invariants, flow, and component boundaries.
- [SeqEvi Sequence and Evidence Contract](https://github.com/FuqingZh/seqevi/blob/main/docs/architecture/20260720-v1.0-sequence-evidence-contract.md)
  Publisher: SeqEvi project. Applies to: approved contract version 1.0, dated
  2026-07-20. Checked: 2026-08-14. Use for: FASTA canonicalization, sequence
  identifiers, the exact evidence key, hit/no-hit states, and reuse rules.
- [SeqEvi Adapter Contract](https://github.com/FuqingZh/seqevi/blob/main/docs/architecture/20260720-v1.0-adapter-contract.md)
  Publisher: SeqEvi project. Applies to: approved contract version 1.0, dated
  2026-07-20. Checked: 2026-08-14. Use for: runtime and resource identity,
  semantic parameters, tool execution, and adapter-specific evidence.
- [SeqEvi v1.1 Result Consumption Contract](https://github.com/FuqingZh/seqevi/blob/main/docs/architecture/20260804-v1.1-result-consumption-contract.md)
  Publisher: SeqEvi project. Applies to: approved v1.1 DuckDB result contract.
  Checked: 2026-08-14. Use for: self-describing results, stable public
  consumption, schema discovery, and version compatibility.
- [SeqEvi Storage and Deployment Architecture](https://github.com/FuqingZh/seqevi/blob/main/docs/architecture/20260729-v1.1-storage-deployment-architecture.md)
  Publisher: SeqEvi project. Applies to: approved storage architecture v1.1.
  Checked: 2026-08-14. Use for: local SQLite, shared PostgreSQL/POSIX storage,
  immutable artifacts, concurrency, recovery, and deployment boundaries.

## Wisdom (Communities)

No community source has yet been selected. Practical advice will be added only
when it is clearly distinguished from normative product contracts.

## Gaps

- Add primary sources for FASTA, amino-acid alphabets, GA4GH refget, hashing,
  modern DIAMOND, Pfam/HMMER, dbCAN, relational databases,
  transactions, Linux processes, HTTP, containers, Parquet, DuckDB, and Polars
  as those lessons begin.
- Re-check repository links and authority status before relying on them after
  SeqEvi contract changes.

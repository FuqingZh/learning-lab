# Bioinformatics Systems Resources

## Knowledge

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
  relational databases, transactions, Linux processes, HTTP, containers,
  Parquet, DuckDB, and Polars as those lessons begin.
- Re-check repository links and authority status before relying on them after
  SeqEvi contract changes.

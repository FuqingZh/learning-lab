# Structural, domain, state, and scientific validity are distinguished

The learner can now classify structural validity, cross-field domain
invariants, authoritative-state invariants, and scientific correctness without
treating one successful gate as proof of the others. This establishes a usable
proof-scope rule for later work on state machines, transactions, execution
isolation, and scientific acceptance.

## Evidence

On 2026-08-19, in a fresh paired-design case, the learner correctly determined
that a nullable `subject_id_column` could pass the structural contract while
violating the domain rule that a paired design requires subject identity. The
learner also stated that passage of the structural, domain, and state gates
proves only their encoded assertions, and explicitly excluded scientific
correctness, identity/authorization binding, and path mapping from that
conclusion.

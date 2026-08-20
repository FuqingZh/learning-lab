# Scientific AI Platforms Resources

## Knowledge

- [NIST: AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
  Publisher: U.S. National Institute of Standards and Technology. Applies to:
  AI RMF 1.0 and the linked Generative AI Profile NIST AI 600-1; NIST reports
  that AI RMF 1.0 is under revision. Checked: 2026-08-19. Use for: modern AI
  system risk, trustworthiness, evaluation, governance, and lifecycle framing.
- [Model Context Protocol: 2026-07-28 Specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
  Publisher: Model Context Protocol project. Applies to: specification release
  2026-07-28. Checked: 2026-08-19. Use for: current agentic interoperability,
  stateless protocol design, durable Tasks, capability evolution, and
  authorization hardening. Treat MCP as a case of modern protocol synthesis,
  not as a foundational discipline.
- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
  Publisher: U.S. National Institute of Standards and Technology. Applies to:
  final SP 800-207, August 2020. Checked: 2026-08-19. Use for: explicit trust
  evaluation, resource protection, and modern authority architecture.
- [Kubernetes: Multi-tenancy](https://kubernetes.io/docs/concepts/security/multi-tenancy/)
  Publisher: Kubernetes project. Applies to: current upstream documentation as
  checked 2026-08-19. Use for: control-plane and data-plane isolation, tenant
  identity, quotas, sandboxing, and the tradeoff between isolation strength and
  operational cost.
- [W3C: PROV-O](https://www.w3.org/TR/prov-o/)
  Publisher: W3C. Applies to: W3C Recommendation dated 2013-04-30 with linked
  errata. Checked: 2026-08-19. Use for: interoperable provenance concepts and
  the relationship among entities, activities, and agents.
- [SLSA Specification v1.2](https://slsa.dev/spec/v1.2/)
  Publisher: SLSA project. Applies to: approved specification version 1.2.
  Checked: 2026-08-19. Use for: modern software supply-chain security,
  provenance, attestations, and progressively stronger source and build
  guarantees.

- [Bio Plot Platform: Scientific Plotting Core Contracts](https://github.com/FuqingZh/bio_plot_platform/blob/36594c4392412dabed4c7207007094efd9702363/docs/architecture/contracts.md)
  Publisher: Bio Plot Platform project. Applies to: repository commit
  `36594c4392412dabed4c7207007094efd9702363`. Checked: 2026-08-17. Use for:
  model-visible fields, domain-object ownership, and deterministic hard gates.
- [Bio Plot Platform: Runtime Architecture](https://github.com/FuqingZh/bio_plot_platform/blob/36594c4392412dabed4c7207007094efd9702363/docs/architecture/runtime.md)
  Publisher: Bio Plot Platform project. Applies to: repository commit
  `36594c4392412dabed4c7207007094efd9702363`. Checked: 2026-08-17. Use for:
  the probabilistic-model versus deterministic-platform boundary and scientific
  acceptance requirements.
- [Bio Plot Platform: External AI Shell Boundary](https://github.com/FuqingZh/bio_plot_platform/blob/36594c4392412dabed4c7207007094efd9702363/docs/architecture/20260712-v1.0-external-ai-shell-boundary.md)
  Publisher: Bio Plot Platform project. Applies to: approved boundary contract
  at repository commit `36594c4392412dabed4c7207007094efd9702363`.
  Checked: 2026-08-17. Use for: state authority, opaque capabilities, result
  inspection, and the boundary between artifact validity and scientific truth.
- [JSON Schema Validation: A Vocabulary for Structural Validation of JSON](https://json-schema.org/draft/2020-12/json-schema-validation)
  Publisher: JSON Schema specification authors. Applies to: Draft 2020-12,
  published 2022-06-16. Checked: 2026-08-18. Use for: assertion keywords,
  structural validity, dependent requirements, and the explicit limit that an
  instance is valid only relative to the constraints asserted by a schema.
- [Pydantic: Validators](https://docs.pydantic.dev/latest/concepts/validators/)
  Publisher: Pydantic. Applies to: Pydantic v2 concepts, checked against the
  repository's locked Pydantic 2.13.4. Checked: 2026-08-18. Use for: field and
  whole-model validators, including cross-field constraints that go beyond
  primitive field shapes.
- [Pydantic: Model configuration](https://docs.pydantic.dev/latest/api/config/)
  Publisher: Pydantic. Applies to: Pydantic v2 configuration, checked against
  the repository's locked Pydantic 2.13.4. Checked: 2026-08-18. Use for:
  `ConfigDict(extra="forbid")` and the rejection of unrecognized input fields.
- [W3C: State Chart XML (SCXML) 1.0](https://www.w3.org/TR/scxml/)
  Publisher: W3C. Applies to: W3C Recommendation dated 2015-09-01, including
  the linked errata. Checked: 2026-08-19. Use for: event-triggered transitions,
  guard conditions, source and target states, initial states, and final-state
  semantics.
- [Leslie Lamport: A High-Level View of TLA+](https://lamport.azurewebsites.net/tla/high-level-view.html)
  Publisher: Leslie Lamport. Applies to: author-maintained overview as checked
  on 2026-08-19. Use for: the bottom-level characterization of a state machine
  by an initial condition and a next-state relation, plus the boundary between
  allowed steps, invariance, and liveness or fairness.
- [PostgreSQL 18: `SELECT`](https://www.postgresql.org/docs/18/sql-select.html)
  Publisher: PostgreSQL Global Development Group. Applies to: PostgreSQL 18,
  matching the repository's checked Kubernetes PostgreSQL 18.4 image contract.
  Checked: 2026-08-19. Use for: `SELECT ... FOR UPDATE`, row locking against
  concurrent writers, and why a state transition's read-check-write sequence
  needs a database concurrency boundary.
- [RFC 9110: HTTP Semantics, Section 9.2.2](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)
  Publisher: IETF, served by the RFC Editor. Applies to: Standards Track RFC
  9110, June 2022. Checked: 2026-08-19. Use for: the formal definition of
  idempotent request semantics, retry after uncertain communication failure,
  and the distinction between stable intended effects and possibly different
  responses or per-request logging.
- [RFC 4949: Internet Security Glossary, Version 2](https://www.rfc-editor.org/rfc/rfc4949.html)
  Publisher: IETF, served by the RFC Editor. Applies to: Informational RFC 4949,
  August 2007. Checked: 2026-08-17. Use for: the standard security definition
  of a capability token and the distinction between authorization and identity.
- [W3C: Good Practices for Capability URLs](https://www.w3.org/TR/capability-urls/)
  Publisher: W3C Technical Architecture Group. Applies to: First Public Working
  Draft toward a TAG Finding; it is historical design guidance, not a W3C
  Recommendation. Checked: 2026-08-17. Use for: capability secrecy, leakage,
  expiry, revocation, unguessability, and why a capability is not a complete
  security boundary by itself.
- [The Confused Deputy — Norm Hardy](https://doi.org/10.1145/54289.871709)
  Publisher: ACM SIGOPS Operating Systems Review 22(4), pages 36-38. Published:
  October 1988. Checked: 2026-08-17. Use for: the original privileged-compiler
  example, mixed authority sources, and why caller-controlled designators must
  not be combined with a deputy's ambient authority.

## Wisdom (Communities)

No community source has yet been selected. Practical advice will be added only
when it is clearly distinguished from normative product contracts.

## Gaps

- Add independent primary sources for transactions, distributed retries,
  container isolation, AI evaluation, and scientific reproducibility as their
  lessons begin; project contracts are case evidence, not substitutes for
  those foundations.

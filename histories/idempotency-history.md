---
schema_version: 2
id: idempotency-history
title: History of idempotency
summary: Documents algebraic terminology, HTTP method semantics, and retry-oriented API practice without asserting a direct lineage.
concepts:
  - idempotency
  - idempotency-key
lessons: []
tracks:
  - scientific-ai-platforms
milestones:
  - id: peirce-1870
    year: 1870
    month: null
    day: null
    kind: terminology
    actors:
      - Benjamin Peirce
    claim: Benjamin Peirce's 1870 Linear Associative Algebra documents idempotent for an algebraic expression that gives itself when raised to a square or higher power.
    subjects:
      - idempotency
    boundaries:
      - Does not establish a direct lineage from algebra to HTTP.
      - Does not establish global priority for the underlying property.
    evidence_basis: mixed
    sources:
      - url: https://www.e-rara.ch/zut/content/titleinfo/6674068
        locator: Pages 16–17, paragraph beginning "When an expression", defining idempotent powers.
        title: Linear Associative Algebra
        publisher: National Academy of Sciences
        role: primary
        kind: monograph
      - url: https://www.unav.es/gep/GrattanGuinness.pdf
        locator: Article page 598, section 1 "Content", paragraph beginning "The associative", discussing idempotent and nilpotent.
        title: "Benjamin Peirce’s Linear Associative Algebra (1870): New Light on its Preparation and ‘Publication’"
        publisher: Annals of Science
        role: scholarly-secondary
        kind: paper
  - id: http-2068-1997
    year: 1997
    month: 1
    day: null
    kind: adoption
    actors:
      - Roy T. Fielding
      - Jim Gettys
      - Jeffrey C. Mogul
      - Henrik Frystyk Nielsen
      - Tim Berners-Lee
    claim: RFC 2068 specifies HTTP method idempotence through repeated-request side effects and identifies GET, HEAD, PUT, and DELETE as idempotent methods.
    subjects:
      - idempotency
      - side-effect
    boundaries:
      - Does not establish that every endpoint implementation lacks incidental side effects.
    evidence_basis: primary-source
    sources:
      - url: https://datatracker.ietf.org/doc/html/rfc2068#section-9.1.2
        locator: Section 9.1.2, Idempotent Methods.
        title: RFC 2068 - Hypertext Transfer Protocol HTTP/1.1
        publisher: Internet Engineering Task Force
        role: primary
        kind: standard
  - id: stripe-api-keys-2017
    year: 2017
    month: 2
    day: 22
    kind: adoption
    actors:
      - Brandur Leach
    claim: A 2017 Stripe engineering article documents using an Idempotency-Key value to correlate retries of a mutating API request after ambiguous network failure.
    subjects:
      - idempotency
      - idempotency-key
    boundaries:
      - Documents Stripe practice rather than universal retention or replay rules.
    evidence_basis: primary-source
    sources:
      - url: https://stripe.com/blog/idempotency
        locator: Section "Idempotency keys", retry paragraph and curl example.
        title: Designing robust and predictable APIs with idempotency
        publisher: Stripe
        role: primary
        kind: professional-documentation
  - id: http-9110-2022
    year: 2022
    month: 6
    day: null
    kind: revision
    actors:
      - Roy T. Fielding
      - Mark Nottingham
      - Julian Reschke
    claim: RFC 9110 defines idempotence by intended server effect and illustrates retrying a PUT after the connection closes before any response is received.
    subjects:
      - idempotency
      - side-effect
    boundaries:
      - Does not guarantee exactly-once execution or identical response bytes.
    evidence_basis: primary-source
    sources:
      - url: https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2
        locator: Section 9.2.2, Idempotent Methods, paragraphs 1–2.
        title: RFC 9110 - HTTP Semantics
        publisher: Internet Engineering Task Force
        role: primary
        kind: standard
---

## Historical setting

The earliest document included in this dossier is an algebra text rather than
a networking specification. Benjamin Peirce's 1870 *Linear Associative
Algebra* uses `idempotent` for an expression that returns itself under a higher
power. The surviving monograph and later historical analysis support that
documented use; they do not establish either global priority or a direct
intellectual path from Peirce to HTTP.

## What the sources establish

[RFC 2068](https://datatracker.ietf.org/doc/html/rfc2068#section-9.1.2)
applied idempotence to HTTP request methods in 1997. Its unit of concern was
the side effect of multiple identical requests, not equality of response
bytes. A
[2017 Stripe engineering article](https://stripe.com/blog/idempotency)
documents a different, application-level mechanism for mutating requests: a
client supplies the same key when retrying an operation whose outcome became
ambiguous. [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)
later states the modern HTTP rule in terms of intended server effect and gives
a lost-response retry example.

## What the sources do not establish

The sources do not justify saying that Peirce invented the underlying property
or intended a computing application. RFC 2068 is not established here as the
first HTTP use, and HTTP method idempotence does not prove that every endpoint
implementation is free of incidental side effects. The Stripe article
documents Stripe's practice in 2017; it does not establish that Stripe invented
idempotency keys or that its retention and replay rules are universal.

## Development

These documents permit a comparison of three uses; their chronological order
does not establish that one caused or directly transmitted the next:

- an algebraic expression under powers;
- intended side effects of repeated HTTP method requests; and
- a client-supplied key used to correlate retries of one API request.

The 2017 Stripe article establishes that last correlation-and-retry mechanism
for Stripe's mutating endpoints. It does not establish universal rules for key
scope, parameter comparison, retention, replay, or state management across
other APIs.

## Modern boundary

An algebraic idempotent, an idempotent HTTP method, and an application-level
idempotency-key implementation are related but non-identical contracts. None
alone guarantees exactly-once physical execution, identical response bytes, or
success. As this repository's modern engineering boundary rather than a
historical-source claim, retry safety must still be evaluated against the
operation identity and authoritative state used by the concrete system.

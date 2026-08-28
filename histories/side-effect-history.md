---
schema_version: 2
id: side-effect-history
title: History of side effects
summary: Documents distinctions between produced values, changes to program state, and intended versus incidental request effects without asserting a single lineage.
concepts:
  - side-effect
lessons: []
tracks:
  - scientific-ai-platforms
milestones:
  - id: strachey-side-effects-1967
    year: 1967
    month: 8
    day: null
    kind: formalization
    actors:
      - Christopher Strachey
    claim: Christopher Strachey's text, based on lectures given in August 1967, distinguishes functions that produce values from routines that affect the store and documents a function that also alters the store as sometimes said to have side effects.
    subjects:
      - side-effect
    boundaries:
      - Does not establish global priority or that Strachey coined the term.
      - Does not establish modern database or messaging-system semantics.
    evidence_basis: primary-source
    sources:
      - url: https://www.cs.cmu.edu/~crary/819-f09/Strachey67.pdf
        locator: Abstract and Section 3.4.5, journal page 30.
        title: Fundamental Concepts in Programming Languages
        publisher: Higher-Order and Symbolic Computation
        role: primary
        kind: paper
  - id: c-side-effects-2011
    year: 2011
    month: 4
    day: 12
    kind: revision
    actors:
      - ISO/IEC JTC 1/SC 22/WG 14
    claim: WG14's N1570 committee draft defines listed operations as side effects that change execution-environment state and separates value computations from the initiation of side effects.
    subjects:
      - side-effect
    boundaries:
      - Does not by itself classify every database write or message publication.
      - Establishes a C language rule rather than a universal definition for all systems.
    evidence_basis: primary-source
    sources:
      - url: https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf
        locator: Section 5.1.2.3, paragraphs 2-3, document page 14.
        title: ISO/IEC 9899:201x Committee Draft N1570
        publisher: ISO/IEC JTC 1/SC 22/WG 14
        role: primary
        kind: standard
  - id: http-side-effect-boundary-2022
    year: 2022
    month: 6
    day: null
    kind: adoption
    actors:
      - Roy T. Fielding
      - Mark Nottingham
      - Julian Reschke
    claim: RFC 9110 distinguishes the user-requested intended effect used for HTTP idempotence from per-request server effects such as logging or revision history.
    subjects:
      - idempotency
      - side-effect
    boundaries:
      - Does not define all programming-language side effects.
      - Does not guarantee exactly-once execution or identical responses.
    evidence_basis: primary-source
    sources:
      - url: https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2
        locator: Section 9.2.2, Idempotent Methods, paragraphs 1-3.
        title: RFC 9110 - HTTP Semantics
        publisher: Internet Engineering Task Force
        role: primary
        kind: standard
---

## Historical setting

The earliest document included here is Christopher Strachey's
*Fundamental Concepts in Programming Languages*. The published paper states
that it is based on lectures given in Copenhagen in August 1967. It contrasts
functions that produce values with routines that alter the computer's store,
then discusses the mixed case in which a function also changes that store.

## What the sources establish

[Strachey's text](https://www.cs.cmu.edu/~crary/819-f09/Strachey67.pdf)
documents a value-versus-store-change distinction and records `side effects`
as terminology for the mixed case. The
[WG14 N1570 committee draft](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf)
later gives C a more explicit execution model: value computations and the
initiation of side effects are distinct parts of expression evaluation, and
specified changes to the execution environment count as side effects.
[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2)
uses an adjacent systems distinction: HTTP idempotence concerns the intended
effect requested by the user even though a server can perform separate effects
for each request, such as logging it.

## What the sources do not establish

These sources do not establish who first coined `side effect`, who first
recognized the underlying distinction, or a direct intellectual lineage from
Strachey's lectures through C to HTTP. The C draft specifies one programming
language and does not supply a universal catalogue of system effects. RFC 9110
does not redefine the programming-language term and does not promise
exactly-once execution.

## Development

The documents support a comparison across three technical boundaries without
proving that one caused the next:

- a function's returned value versus its changes to the store;
- value computation versus state changes in a language execution model; and
- an HTTP request's intended effect versus incidental effects of processing
  each request.

Across these settings, the useful recurring distinction is between what an
operation returns or denotes and what observable state it changes. The exact
set of observable changes remains a contract of the language or system being
discussed.

## Modern boundary

For this repository's system examples, creating a Job, updating a database,
publishing a message, or writing a result file can be treated as a side effect
because each changes observable state. That classification is a modern
engineering application, not a historical claim supplied by the 1967 source.
Whether repeating such an effect is safe is a separate question governed by
the operation's idempotency, identity, and authoritative state contract.

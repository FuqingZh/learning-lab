---
schema_version: 2
id: web-programming-history
title: Development of Web programming boundaries
summary: Documents selected steps from networked hypertext through scripting, a programmable document interface, static checking for JavaScript, and component-based UI rendering without asserting one direct lineage.
concepts:
  - process
  - program
  - service
  - side-effect
lessons:
  - lessons/scientific-ai-platforms/react-from-document-updates.md
  - lessons/scientific-ai-platforms/web-document-browser-and-server.md
tracks:
  - scientific-ai-platforms
milestones:
  - id: worldwideweb-browser-server-1990
    year: 1990
    month: 11
    day: 12
    kind: formalization
    actors:
      - Robert Cailliau
      - Tim Berners-Lee
    claim: The 1990 WorldWideWeb proposal documents a networked hypertext architecture in which browser processes display and navigate linked nodes while active server processes answer requests for information stored on server machines.
    subjects:
      - process
      - program
      - service
    boundaries:
      - Does not describe JavaScript, DOM, TypeScript, or React.
      - Does not establish modern browser security or application semantics.
    evidence_basis: primary-source
    sources:
      - url: https://www.w3.org/Proposal.html
        locator: Abstract; Introduction; Hypertext concepts; Architecture; Building blocks.
        title: WorldWideWeb - Proposal for a HyperText Project
        publisher: World Wide Web Consortium historical archive
        role: primary
        kind: archive
  - id: ecmascript-host-scripting-1997
    year: 1997
    month: 6
    day: null
    kind: formalization
    actors:
      - Ecma Technical Committee 39
    claim: The first edition of ECMA-262 specifies ECMAScript as a general-purpose cross-platform programming language operating within a host environment and characterizes scripting as exposing an existing system's facilities to program control.
    subjects:
      - program
    boundaries:
      - Does not establish priority for JavaScript or every source that influenced it.
      - Does not standardize the DOM or a component-based UI model.
    evidence_basis: primary-source
    sources:
      - url: https://ecma-international.org/wp-content/uploads/ECMA-262_1st_edition_june_1997.pdf
        locator: Title page; Brief History; Sections 1 and 4, especially 4.1 Web Scripting.
        title: ECMA-262, 1st edition - ECMAScript
        publisher: Ecma International
        role: primary
        kind: standard
  - id: dom-programmatic-interface-1998
    year: 1998
    month: 10
    day: 1
    kind: adoption
    actors:
      - W3C DOM Working Group
    claim: The DOM Level 1 Recommendation defines a platform- and language-neutral interface through which programs and scripts can dynamically access and update document content, structure, and style.
    subjects:
      - program
      - side-effect
    boundaries:
      - Does not define TypeScript or React.
      - Does not establish that all document mutations are safe or desirable.
    evidence_basis: primary-source
    sources:
      - url: https://www.w3.org/TR/1998/REC-DOM-Level-1-19981001/
        locator: Abstract and Introduction.
        title: Document Object Model Level 1 Specification
        publisher: World Wide Web Consortium
        role: primary
        kind: standard
  - id: typescript-application-scale-2012
    year: 2012
    month: 10
    day: 1
    kind: adoption
    actors:
      - Microsoft
    claim: Microsoft's 2012 TypeScript announcement frames growing JavaScript applications as a tooling and maintenance problem and documents optional static checking whose type annotations are erased when JavaScript is emitted.
    subjects:
      - program
    boundaries:
      - Documents Microsoft's public framing rather than a universal diagnosis of JavaScript development.
      - Does not establish runtime validation or freedom from side effects.
    evidence_basis: primary-source
    sources:
      - url: https://learn.microsoft.com/en-us/archive/blogs/somasegar/typescript-javascript-development-at-application-scale
        locator: Opening announcement; Application-Scale JavaScript; TypeScript Starts and Ends with JavaScript.
        title: TypeScript - JavaScript Development at Application Scale
        publisher: Microsoft
        role: primary
        kind: professional-documentation
  - id: react-render-description-2013
    year: 2013
    month: 6
    day: 5
    kind: adoption
    actors:
      - Pete Hunt
      - React project
    claim: A 2013 React project post documents reusable UI components and a render method that returns a lightweight view description which React compares across data changes before applying a minimal set of DOM updates.
    subjects:
      - program
      - side-effect
    boundaries:
      - Documents the 2013 React model rather than every modern React API or runtime behavior.
      - Does not establish global priority for component-based or declarative user interfaces.
    evidence_basis: primary-source
    sources:
      - url: https://legacy.reactjs.org/blog/2013/06/05/why-react.html
        locator: Sections React isn't an MVC framework; React doesn't use templates; Reactive updates are dead simple.
        title: Why did we build React?
        publisher: React project
        role: primary
        kind: professional-documentation
---

## Historical setting

The selected sequence begins with a 1990 proposal for linked information across
incompatible systems, not with a modern web application. It then records a
programming-language standard, a programmable document interface, and later
project documents for TypeScript and React. These sources come from different
organizations and address different technical boundaries.

## What the sources establish

The 1990 WorldWideWeb proposal documents browser and server processes connected
by a network and exchanging linked information nodes. ECMA-262's 1997 first
edition specifies a scripting language executed within a host environment.
The 1998 DOM Level 1 Recommendation provides a standard programmatic interface
to document content, structure, and style. Microsoft's 2012 announcement
documents TypeScript's static-checking and JavaScript-emission boundary. A 2013
React project post documents components, render descriptions, comparison after
data changes, and subsequent DOM updates.

## What the sources do not establish

Their chronological order does not prove a single causal chain. The sources do
not establish who first invented scripting, programmable documents, static
checking for JavaScript, component-based UI, or declarative rendering. Project
announcements establish how Microsoft and the React project described their
work at those dates, not neutral priority histories or every modern behavior.

## Development

The sequence is useful as a set of changing boundaries:

- a browser retrieves and presents linked information from servers;
- a scripting language performs computation within a host environment;
- a standard interface exposes a document to programmatic access and update;
- an optional static layer checks JavaScript programs before runtime; and
- a UI library derives a view description and owns the resulting DOM update.

Each step presupposes knowledge that should be taught before the later one, but
the dossier does not infer that any one document directly caused its successor.

## Modern boundary

For current learning, JavaScript runtime behavior must be understood before
TypeScript's erased type layer, and document/DOM programming must be understood
before React's render model. Bio Plot Platform is then a case laboratory for
those boundaries. Its current dependency versions do not redefine the
historical milestones or the transferable concepts.

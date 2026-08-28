# The Web before JavaScript: document, browser, and server

## Place in the systems map

This is an orientation-to-foundation lesson spanning networks and runtime:

```text
information stored on different machines
  -> server process answers requests
  -> browser process retrieves and presents nodes
  -> links let a user navigate between nodes
```

Its tangible win is a complete first mental model of why a networked information
system needs documents, links, browser behavior, server behavior, and a network
boundary before introducing HTML syntax, JavaScript, TypeScript, or React.

## Advance organizer

The learner does not need prior Web programming knowledge. Start from five
questions and answer them as one connected model:

1. Where does the information remain stored?
2. How does one machine ask another machine for it?
3. Which running program answers that request?
4. Which running program presents the answer to the user?
5. How can one returned information object refer to another?

This lesson is about distributed information retrieval and navigation. It is
not yet about login, a shared user identity, code embedded in a page, or a UI
framework.

## One documented historical increment

On 12 November 1990, Tim Berners-Lee and Robert Cailliau submitted
[*WorldWideWeb: Proposal for a HyperText Project*](https://www.w3.org/Proposal.html).
The proposal describes incompatible platforms and information systems at CERN:
users needed different lookup methods, computers, and interfaces and could not
follow a stable link from one body of information to another.

Before presenting the proposal, explain what was fragmented: information could
already exist in documents and databases, machines could already communicate,
and people could already use individual lookup systems. The missing piece was a
common model for identifying, retrieving, presenting, and linking information
across those systems. A prediction question is optional after this context; it
must not replace the context.

## What the source proposed

The proposal describes a networked hypertext architecture:

- information is represented as nodes connected by links;
- server processes make stored information available and answer requests;
- browser processes run on client machines, display nodes, and traverse links;
- nodes may reside on different machines and may be reached through different
  servers.

In this setting, the browser and server are programs realized by running
processes. A displayed hypertext page is information handled by those programs;
the source does not describe JavaScript executing inside the page.

## Connected walkthrough

Suppose a laboratory manual stays on machine B while a researcher works on
machine A:

1. A document on machine A contains a link that identifies the manual.
2. The browser process on A interprets that link and sends a request across the
   network.
3. A server process on B receives the request and locates the stored document.
4. The server returns the information; it does not need to transfer ownership
   of all user data or merge the two machines' identity systems.
5. The browser presents the returned document. Further links can repeat the
   same pattern with other servers.

The document is information. Browser and server are programs; when they are
running and participating in this exchange, they are processes. The network
carries requests and responses but does not itself own the document's meaning.

## Contrast with an identity-centered design

A common login, one user ID, identity federation, and aggregation of all user
information solve authentication and personalization problems. Those are valid
later system concerns, but they are not required by this minimal linked-document
model. Treating them as prerequisites would centralize data that the early model
allows to remain on independent servers.

## Modern boundary

Modern browsers are much larger host environments and can execute JavaScript,
change a DOM, store local data, and communicate with services. None of those
later mechanisms should be projected backward into the 1990 proposal. The
proposal establishes the selected client/browser, server, network, node, and
link model; it does not establish TypeScript, React, single-page applications,
or modern browser security.

The broader documented sequence is recorded in
[Development of Web programming](../../histories/web-programming-history.md).
Its chronology does not assert that one milestone directly caused the next.

## Bio Plot Platform case boundary

Bio Plot Platform currently has a browser-facing React frontend and an HTTP
backend. That is a later repository case, not the definition of the Web. Before
inspecting its components or routes, the learner should be able to identify the
browser-side program/process, server-side program/process, network request,
and information returned across that boundary.

## End-of-unit evidence

For a user who clicks a link and receives a document from another machine,
state separately:

1. what the document is;
2. what the browser program/process does; and
3. what the server program/process does.

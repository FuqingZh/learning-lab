# Program, process, and service

## Place in the systems map

This lesson sits between software construction and runtime operations:

```text
source and executable instructions
  -> operating-system execution
  -> externally consumed capability

program
  -> process
  -> service
```

The arrows show realization, not identity. One program can be executed by many
processes. One service can be realized by one process, several cooperating
processes, or different process sets over time.

The distinction is needed before studying memory, persistence, supervision,
retries, or distributed state. Otherwise a statement such as "the program is
healthy" silently mixes a static artifact, a running instance, and a user-facing
promise.

## One documented historical increment

In 1965, while analyzing cooperation between sequential computations, Edsger
W. Dijkstra explicitly separated the rules being followed from what happens
during their execution. In
[EWD123](https://www.cs.utexas.edu/~EWD/transcriptions/EWD01xx/EWD123.html),
he called the rules an algorithm or program and the execution a sequential
process.

That source supports a program/process distinction under its own technical
setting. It does not establish the modern POSIX process model, the later UNIX
`fork`/`exec` interface, or a theory of application services. Those later
developments and their evidence boundaries are recorded in
[the linked history dossier](../../histories/program-process-and-service-history.md).

## Modern working model

| Layer | What it is | Typical identity | State and lifetime |
| --- | --- | --- | --- |
| Program | Instructions prepared for execution, together with the artifacts needed to interpret or load them | source revision, package or image digest, executable path plus version | Normally passive; editing or replacing it does not itself create a running computation |
| Process | A running execution instance with an address space, threads, handles, credentials, and other runtime resources | PID only within its host and lifetime; stronger coordinates also include host or namespace and start time | Created, scheduled, blocked, resumed, and terminated |
| Service | A capability exposed under an interface or operational contract | service name, endpoint, API contract, deployment identity, or job type | May persist as a logical identity while its realizing processes start, stop, or are replaced |

These are working systems boundaries, not claims that every platform uses the
words identically. In particular, an operating-system service manager may use
`service` for one managed unit, while an application architecture may use it
for a capability implemented by several replicas.

## The mechanism that connects them

A launcher asks the operating system to create or transform a process so that
it executes a program. The 1974 UNIX paper makes the distinction operational:
`fork` creates a child process, and `execute` replaces what that process is
running with a named program.

A supervisor, scheduler, or orchestrator can then manage one or more such
processes to realize a service:

```text
program artifact v7
  -> process host-a:pid-4102
  -> annotation API service

program artifact v7
  -> process host-b:pid-8821
  -> annotation API service
```

Killing one process does not delete the program. Replacing one replica does not
necessarily change the service identity. Conversely, a live process does not
prove that the service is usable: it may be deadlocked, unable to reach its
database, returning invalid results, or missing its latency objective.

## Failure claims must name their boundary

| Observation | Supported claim | Unsupported promotion |
| --- | --- | --- |
| An executable file exists | A program artifact is present at that location | The program has been successfully executed |
| A process is alive | A runtime instance has not terminated | Its service is healthy or meeting its SLO |
| One process exits | That execution instance terminated | The whole service necessarily failed |
| The endpoint times out | The interface deadline was missed | The worker process necessarily crashed |
| A replacement process serves the same contract | The service may continue across process replacement | The new process has the same runtime identity or volatile state |

## Scientific-system example

For a sequence-annotation system:

- the installed adapter code and tool image are program artifacts;
- each running adapter or external-tool invocation is a process;
- "submit annotation and later retrieve its result" is a service contract.

The executable may be correct while one process is killed for exceeding
memory. The worker process may complete while result publication fails. Several
workers may realize the same service without being the same process or sharing
volatile state. Diagnosis therefore starts by locating the failed boundary,
not by using `program`, `process`, and `service` as synonyms.

## Transfer check

A supervisor reports that one worker process is alive. During the same
five-minute window, every valid API request times out, while the program image
digest is unchanged.

State separately what this establishes about the **program**, the **process**,
and the **service**. Which success claim, if any, remains unsupported?

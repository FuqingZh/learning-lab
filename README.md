# Learning Lab

This is Fuqing Zhang's public, persistent workspace for building transferable
understanding across scientific software and its computing foundations.

The repository records a learning mission, trusted sources, demonstrated
knowledge, reusable lessons, and later review material. It is deliberately
separate from source repositories: its contents are personal learning state,
not authoritative product documentation and not implementation requirements.

## Start here

- [MISSION.md](MISSION.md): workspace-wide learning outcome and boundaries.
- [CURRICULUM.md](CURRICULUM.md): active track index and reading order.
- [RESOURCES.md](RESOURCES.md): source policy and track resource indexes.
- [NOTES.md](NOTES.md): teaching preferences shared by every track.
- [GLOSSARY.md](GLOSSARY.md): professionally established terminology admitted
  through the two-source terminology gate; it is not learner capability state.
- [Knowledge Map](maps/README.md): generated global, track, case-lab, and focal
  dependency views.
- [Interactive Map](site/index.html): self-contained spatial explorer with
  concept, history, and evidence-network views, plus search, reviewed
  capability, review cues, and structured resume.
- [Online Knowledge Space](https://fuqingzh.github.io/learning-lab/): generated
  GitHub Pages projection for access without opening the local HTML file.
- [Workspace documentation](docs/README.md): active implementation plans,
  concept-authoring procedure, and recorded observational reviews. The
  [2026-08-27 learning-method review](docs/reviews/20260827-v1.0-learning-method-review.md)
  is not a teaching contract.

## Content boundaries

- `tracks/`: one independent mission and curriculum per transferable capability
  track. Repositories are anchors and case laboratories, not the top-level
  taxonomy.
- `learning-records/<track>/`: reviewed capability records and readable legacy
  evidence. Only validated structured metadata establishes current capability;
  filenames and legacy prose do not.
- `lessons/<track>/`: reusable teaching artifacts created only when useful.
- `histories/`: evidence-backed development dossiers linked to lessons or
  canonical concepts; schema-v2 milestones project explicit claims, sources,
  locators, and evidence boundaries without treating chronology as causality.
- `concepts/`: canonical transferable concept definitions and typed relations.
- `case-labs/`: thin repository hubs; the existence of a hub does not establish
  concept membership.
- `docs/reviews/`: observational method reviews; not teaching contracts and
  not implementation plans.
- `maps/` and `site/`: generated projections; never edit them as authorities.
- `learning-state/sessions/`: append-only observations and durable resume from
  learning encounters; generated review cues are not curriculum progression or
  reviewed capability.
- `.agents/skills/learning-lab-tutor/`: the history-grounded, map-first learning
  workflow used by compatible AI agents.
- `reference/`: compressed cross-track recall material, created only when real
  reuse exists.

Root files remain stable workspace entrypoints. Track files own track-specific
curricula, sources, and progress; the root indexes link to them rather than
copying their content. Personal learning state is not authoritative product
documentation or an implementation requirement for any source repository.

## Naming and lifecycle

Existing numbered records retain their filenames for history. New records use
`YYYYMMDD-topic-state.md` inside their track directory so concurrent tracks do
not compete for one global counter. Superseded records link to the replacement
file. Lessons use semantic topic names rather than lesson numbers.

Run `bash scripts/check-structure.sh` after changing workspace structure or
adding a record, lesson, or concept. See the
[concept authoring guide](docs/how-to-guides/20260820-v1.0-add-knowledge-concept-how-to-guide.md)
before changing the graph schema or evidence links, and the
[history dossier guide](docs/how-to-guides/20260824-v1.2-add-evidence-backed-history-how-to-guide.md)
before adding historical claims.

## Build and validation

The interactive map is a generated, single-file offline artifact. It requires
Python 3 and Node.js 24.x; install the locked frontend tools once per clean
checkout:

```bash
npm ci
```

Regenerate the published local artifact after changing its canonical inputs or
frontend presentation code:

```bash
python3 scripts/render-knowledge-map-site.py
```

The complete contributor gate is:

```bash
npm ci && bash scripts/check-structure.sh
```

For frontend-only diagnostics, run `npm run frontend:verify`. The renderer and
generated-drift check intentionally fail if Node.js 24.x or the dependencies
installed by `npm ci` are unavailable; they never download browser dependencies
implicitly. GitHub Pages uploads only the generated `site/` directory.

## Ambient learning

Ask a compatible agent to use `$learning-lab-tutor`, or simply say that you
want to continue. The default session restores the last thread briefly, gives
the learner an advance organizer, and teaches a coherent lesson unit before
checking understanding at a natural conceptual boundary. A unit may include
multiple connected concepts when splitting them would remove necessary
context. The tutor records a structured lesson, concept, or track resume point
automatically. The current authority and evidence boundaries are in the
[mission-led learning-loop plan](docs/implementation-plans/20260827-v1.4-mission-led-learning-loop-implementation-plan.md).

## 2026-08-17 migration

The former flat record and lesson paths were retired in favor of track
directories. No duplicate compatibility files are retained because they would
create two apparent authorities; use the indexes above to resolve the new
paths. Root workspace entrypoints and `.teach-workspace.yaml` remain unchanged
for teach-workspace discovery.

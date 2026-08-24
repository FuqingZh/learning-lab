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
- [GLOSSARY.md](GLOSSARY.md): vocabulary added only after demonstrated use.
- [Knowledge Map](maps/README.md): generated global, track, case-lab, and focal
  dependency views.
- [Interactive Map](site/index.html): self-contained spatial explorer with
  search, track lenses, typed relationships, and mastery cues.
- [Online Knowledge Space](https://fuqingzh.github.io/learning-lab/): generated
  GitHub Pages projection for access without opening the local HTML file.
- [Workspace documentation](docs/README.md): active implementation plan and
  concept-authoring procedure.

## Content boundaries

- `tracks/`: one independent mission and curriculum per transferable capability
  track. Repositories are anchors and case laboratories, not the top-level
  taxonomy.
- `learning-records/<track>/`: what the learner has actually demonstrated,
  including superseded intermediate states.
- `lessons/<track>/`: reusable teaching artifacts created only when useful.
- `histories/`: evidence-backed development dossiers linked to lessons or
  canonical concepts; chronology is not treated as proof of causal lineage.
- `concepts/`: canonical transferable concept definitions and typed relations.
- `case-labs/`: thin repository hubs; the existence of a hub does not establish
  concept membership.
- `maps/` and `site/`: generated projections; never edit them as authorities.
- `learning-state/sessions/`: append-only, concept-level evidence from short
  learning encounters; generated due and capability state is not hand-edited.
- `.agents/skills/learning-lab-tutor/`: the low-friction three-minute learning
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

## Ambient learning

Ask a compatible agent to use `$learning-lab-tutor`, or simply say that you
have a few minutes and want to continue. The default session restores the last
thread in at most two short sentences, advances one coherent knowledge
increment, uses at most one retrieval or transfer check, and records the next
resume point automatically. The full design and evidence boundaries are in the
[Ambient Learning implementation plan](docs/implementation-plans/20260821-v1.1-ambient-learning-implementation-plan.md).

## 2026-08-17 migration

The former flat record and lesson paths were retired in favor of track
directories. No duplicate compatibility files are retained because they would
create two apparent authorities; use the indexes above to resolve the new
paths. Root workspace entrypoints and `.teach-workspace.yaml` remain unchanged
for teach-workspace discovery.

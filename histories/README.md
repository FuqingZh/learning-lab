# Historical dossiers

Each `histories/<stable-id>.md` file is an evidence-backed history dossier. It
is separate from the present-day concept graph: a dossier may link one or more
canonical concepts, lessons, and tracks, but concepts do not mirror a history
field.

Run the contract boundary from the repository root:

```bash
python3 scripts/build-knowledge-history.py validate
python3 scripts/build-knowledge-history.py normalized-data
python3 scripts/build-knowledge-history.py normalized-evidence-data
```

The frontmatter must contain exactly `schema_version`, `id`, `title`,
`summary`, `concepts`, `lessons`, `tracks`, and `milestones`. IDs use lowercase
hyphenated stable-id syntax; a dossier filename is its ID plus `.md`.
`concepts` names canonical concept IDs, `lessons` names existing repository
relative Markdown paths under `lessons/`, and `tracks` names existing track
directories. A dossier must link at least one concept or lesson.

Schema v1 remains readable for the timeline projection. Schema v2 additionally
requires each milestone to contain sorted, nonempty `subjects` (existing
canonical concept IDs) and `boundaries` (bounded statements of what the cited
evidence does not establish). Only schema v2 milestones emit evidence-graph
nodes and edges; v1 dossiers are deliberately absent from that projection.

Each v1 milestone contains exactly `id`, `year`, `month`, `day`, `kind`, `actors`,
`claim`, `evidence_basis`, and `sources`; v2 adds `subjects` and `boundaries`. `month` and `day` are nullable
integers; a day requires a month. Milestones sort by date precision and ID.
Valid `kind` values are `terminology`, `problem`, `formalization`, `adoption`,
`popularization`, `revision`, and `critique`.

`evidence_basis` makes the minimum structural evidence explicit:

- `primary-source` requires at least one `primary` source.
- `scholarly-secondary` requires at least one `scholarly-secondary` source.
- `mixed` requires both roles.

Every v1 source contains exactly `url`, `title`, `publisher`, `role`, and `kind`;
v2 adds a nonempty `locator`. URLs must be HTTPS. The evidence projection
canonicalizes a URL by lowercasing scheme and host, removing default HTTPS port
and fragment, while preserving path and query. It derives `source-<first16 sha256>`
from that canonical URL. Occurrences of the same source must agree on title,
publisher, and kind; conflicts or a truncated-hash collision fail closed.
The original occurrence URL, role, and locator stay on its citation edge.
Roles are `primary` and
`scholarly-secondary`; kinds are `monograph`, `paper`, `standard`, `archive`,
and `professional-documentation`.

The Markdown body must contain all of these level-two headings:

```markdown
## Historical setting
## What the sources establish
## What the sources do not establish
## Development
## Modern boundary
```

The validator checks structure, identity, links, dates, source metadata, and
deterministic JSON only. It does not establish that a source supports a claim;
authors and reviewers must audit that evidence separately.

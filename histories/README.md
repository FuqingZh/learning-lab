# Historical dossiers

Each `histories/<stable-id>.md` file is an evidence-backed history dossier. It
is separate from the present-day concept graph: a dossier may link one or more
canonical concepts, lessons, and tracks, but concepts do not mirror a history
field.

Run the contract boundary from the repository root:

```bash
python3 scripts/build-knowledge-history.py validate
python3 scripts/build-knowledge-history.py normalized-data
```

The frontmatter must contain exactly `schema_version`, `id`, `title`,
`summary`, `concepts`, `lessons`, `tracks`, and `milestones`. IDs use lowercase
hyphenated stable-id syntax; a dossier filename is its ID plus `.md`.
`concepts` names canonical concept IDs, `lessons` names existing repository
relative Markdown paths under `lessons/`, and `tracks` names existing track
directories. A dossier must link at least one concept or lesson.

Each milestone contains exactly `id`, `year`, `month`, `day`, `kind`, `actors`,
`claim`, `evidence_basis`, and `sources`. `month` and `day` are nullable
integers; a day requires a month. Milestones sort by date precision and ID.
Valid `kind` values are `terminology`, `problem`, `formalization`, `adoption`,
`popularization`, `revision`, and `critique`.

`evidence_basis` makes the minimum structural evidence explicit:

- `primary-source` requires at least one `primary` source.
- `scholarly-secondary` requires at least one `scholarly-secondary` source.
- `mixed` requires both roles.

Every source contains exactly `url`, `title`, `publisher`, `role`, and `kind`.
URLs must be unique HTTPS URLs within a dossier. Roles are `primary` and
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

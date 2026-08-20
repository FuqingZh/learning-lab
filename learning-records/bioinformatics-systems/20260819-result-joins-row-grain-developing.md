# Result joins and row grain are developing

Superseded by
[the mastered record](20260819-result-joins-row-grain-mastered.md) after the
left-join/no-hit preservation check was completed.

The learner understands one-to-many join multiplication. In unaided
application, the learner correctly predicted that two input records sharing
one `SequenceID`, joined to three native Pfam match rows, produce six
annotation rows. The learner also placed one-row-per-input aggregation at the
outer consumption or presentation layer rather than changing stored native
evidence.

## Boundary still being consolidated

An explicit aggregation must preserve or deliberately summarize the native
match tuples. Suitable representations include a list of structs, a match
count, or a separately specified best-hit rule. Comma concatenation or an
implicit first-row choice can destroy coordinates and evidence relationships.

The canonical `annotations` relation uses a left join from `sequence_map` to
`evidence`. This guarantees that every input remains visible: a `no_hit` input
produces one annotations row whose adapter-evidence fields are null. An inner
join would silently drop no-hit inputs and confuse biological absence of
accepted evidence with absence of the submitted input record.

## Evidence

On 2026-08-19, the learner reconstructed the `2 * 3 = 6` multiplicity and kept
aggregation outside the evidence layer. A left-join/no-hit application remains
before mastery.

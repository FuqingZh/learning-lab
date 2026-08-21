# Learning state

Append-only YAML events in `sessions/` are the source of personal learning
evidence. `scripts/build-learning-state.py` validates them against the
canonical knowledge graph and derives deterministic JSON state.

```bash
python3 scripts/build-learning-state.py validate
python3 scripts/build-learning-state.py normalized-data
python3 scripts/build-learning-state.py list-due --today 2026-08-21
```

`normalized-data` deliberately contains no current-clock-dependent due label.
`list-due` applies the caller-supplied calendar date. A `partial` or `miss`
latest outcome is projected as `lapsed`; `overdue` independently reports
whether the next review date is earlier than the supplied date.

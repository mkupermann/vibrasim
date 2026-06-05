# Archived run-logs

Raw stdout/stderr captures from past experiment runs, moved here from the repo root to keep the top level clean
(see `docs/REPO_STRUCTURE.md`). Grouped by experiment series:

- `bet/` — BET-series substrate/cognition runs
- `g/`   — G-series substrate physics runs
- `geo/` — GeoWorld-series runs
- `jep/` — JEP-series cognition runs
- `misc/` — everything else (autopilot, smoke tests, pip install logs, …)

These are kept for provenance only. **The authoritative record of every experiment is its
`docs/amendments/<id>.md` and the row in `docs/PREDICTION_LOG.md`** — not these logs. New run output should be
redirected here (or to a temp path), never left at the repo root, where `.gitignore` will ignore it.

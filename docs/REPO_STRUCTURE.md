# Repository structure & housekeeping

This repo runs a pre-registered experiment programme, which generates a lot of output. To keep it navigable, the
layout and conventions below are enforced (partly by `.gitignore`). Please follow them so the root stays clean.

## Top-level layout

| Path | Purpose |
|------|---------|
| `world/` | The substrate simulator + cognition stack (the actual library code). |
| `tools/` | Runnable experiment scripts (`run_<id>_<name>.py`) and CLIs (`talk.py`, `web_gui.py`, …). |
| `tests/` | pytest suite (`pytest -m "not slow"` for the fast slice). |
| `docs/` | All written knowledge (see below). |
| `docs/amendments/` | One pre-registered experiment per file: motivation, bars, result, verdict. |
| `docs/patterns/` | Reusable mechanisms surfaced from experiments. |
| `docs/figures/` | Figures referenced by docs (PNG/plots). |
| `renders/`, `data/`, `corpus.*.yaml` | Inputs / configs for runs. |
| `archive/run-logs/` | Raw stdout/stderr captures from past runs, grouped by series (`bet/`, `g/`, `geo/`, `jep/`, `misc/`). Kept for provenance, out of the way. |
| `LOGBOOK.md`, `PREDICTION_LOG.md`, `ANALYSIS.md`, `HANDOFF.md` | Running narrative + prediction ledger. |
| `autopilot*.py`, `Makefile`, `pyproject.toml`, `*.bat`, `setup_windows.ps1` | Entry points / build config. |

## The one rule that keeps it clean: outputs never live at the repo root

Findings belong in `docs/amendments/<id>.md` and a one-line row in `docs/PREDICTION_LOG.md`. **Raw run output does
not belong in the root.** When running an experiment, either:

- redirect to the archive: `... > archive/run-logs/jep/jepNNN_out.txt 2>&1`, or
- redirect to a temp path you don't commit, or
- rely on the amendment doc to capture the result (preferred — the numbers that matter go in the doc).

`.gitignore` root-anchors `*_out.txt`, `*_err.txt`, `*_probe.txt`, `*_flux.txt`, `*.log`, `*.png`, `*.tar.gz` so a
stray output file at the top level is ignored by default. Files intentionally filed under `archive/run-logs/` or
`docs/figures/` are kept (the patterns are root-anchored). If you genuinely need a new top-level artifact tracked,
add a targeted negation to `.gitignore` and say why.

## Naming conventions

- Experiment runner: `tools/run_<id>_<slug>.py` (e.g. `run_jep367_phd_comprehension_gate.py`).
- Amendment: `docs/amendments/<id>_<slug>.md` with pre-registered bars **before** the run.
- Figures: `docs/figures/<id>_<slug>.png`, referenced from the amendment by that path.

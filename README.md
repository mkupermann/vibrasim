# World of Vibrations

A simulated 2D world whose only primitive substance is **vibrations**. Through a small set of natural laws, vibrations bind into electrons, then into pairs, triads, and indestructible atoms. The long-term research goal is to grow brain-like structures from this physical substrate.

## Quick start

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run with default config in a Pygame window
python -m world run

# Headless calibration run, 60 simulated seconds
python -m world run --headless --duration 60 --snapshot-every 5
```

Press `Esc` to quit, `Space` to pause, `R` to reset.

## Project layout

- `world/` — Python package (state, physics, spatial hash, renderer, CLI)
- `tests/` — pytest suite for natural laws + calibration smoke test
- `files/` — source spec documents (English + preserved German originals as `*.de.md`)
- `docs/superpowers/specs/` — design specifications
- `docs/superpowers/plans/` — implementation plans
- `LOGBOOK.md` — research diary

## Documentation

- `files/SPECIFICATION.md` — original world spec (English)
- `files/SKILL.md` — long-term phase plan toward brain-like structures
- `docs/superpowers/specs/2026-05-05-world-of-vibrations-design.md` — design spec for Phase 1 (this build)

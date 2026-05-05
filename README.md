# World of Vibrations

A 2D simulated world whose only primitive is a vibration — frequency, polarity, position, velocity, and that's all. From those, the natural laws of this world build a hierarchy: two vibrations meeting under specific conditions bind into an electron, two electrons into a pair, a pair plus an electron into a triad, a triad plus an electron into an indestructible atom. The long-term research goal, several phases out, is to grow brain-like structures from this substrate.

This is research code. It runs in real time, it produces atoms (eventually), and it is not a product.

## What's in the repo

Phase 1 of the build covers the physics primitives — motion, binding, decay, atom formation — plus a Pygame window for watching the world and a headless mode for hours-long calibration runs. The pytest suite covers each natural law individually, so a regression in one rule is caught before it spreads. A 60-second smoke script asks the world to produce at least one electron, one pair, and one triad before exiting; the calibration sessions that follow are logged in `LOGBOOK.md`.

The defaults in `world/config.py` are taken from the source German spec at `files/SPEZIFIKATION.de.md`. They are documentary, not calibrated. A 60-second run at the defaults produces around twenty electrons and zero pairs — the same picture the source README warned about. The first calibration sweep is logged in `LOGBOOK.md`; a 500×500 box with `r_2 = 20` produced the first pair we have on record.

## Running it

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

python -m world run                                    # window, default config
python -m world run --headless --duration 60 \
                   --snapshot-every 5                  # headless, stats every 5 s
python -m world run --config calibration_v3.toml       # parameter overrides
```

`Esc` quits. `Space` pauses. `R` reseeds.

## Layout

| Path | What's there |
|---|---|
| `world/` | The package — config, state, spatial hash, physics, renderer, CLI |
| `tests/` | Pytest suite plus a standalone calibration smoke script |
| `files/` | Source spec documents in English, German originals preserved as `*.de.md` |
| `docs/superpowers/specs/` | Design specs, including the Phase 1 design doc |
| `docs/superpowers/plans/` | Implementation plans |
| `LOGBOOK.md` | Research diary, manually maintained |

## Where to read further

If you've never seen this project before, start with `files/README.md` — the onboarding written for the first session that built it. The full physical constitution is in `files/SPECIFICATION.md` (translated from `SPEZIFIKATION.de.md`, the original German). The long-term phase plan, all the way to brain-like structures, is in `files/SKILL.md`. The Phase 1 design doc that drove this build is at `docs/superpowers/specs/2026-05-05-world-of-vibrations-design.md`.

## Honest expectations

This is not a weekend project. The source README puts realistic timelines on each phase: weeks for Phase 1, months for molecules and membranes, a year or more for neurons and synapses, indefinite for anything past that. There is no guarantee any given phase is reached. Each phase that is reached is a result on its own.

Two things from experience. Let the world run before you intervene; the interesting behaviour shows up after minutes, not seconds. And trust the world more than your own expectations — if it produces something other than what you imagined, that is often the more interesting thing.

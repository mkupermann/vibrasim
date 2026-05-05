# Vibrasim

A 2D simulated world built from one primitive, the vibration, with frequency, polarity, position, velocity, and nothing else. Out of those, a small set of natural laws makes vibrations bind into electrons, electrons into pairs, pairs and electrons into triads, and a triad plus an electron into an indestructible atom. That's Phase 1 of an eight-phase research programme. The phases keep going: molecules, membrane-like structures, neurons, synapses with molecular transmission, networks, attention, and larger specialised structures. The full conceptual case is in [`docs/CONCEPT.md`](docs/CONCEPT.md).

This isn't a product. It's the substrate that the concept paper proposes, made concrete enough to actually run.

## Why this exists

The concept paper asks whether a hierarchical, brain-like system can be built from a sparse set of local interaction rules between elementary vibrations, rather than being either biophysically simulated neuron by neuron (NEURON, Blue Brain) or abstracted away from the substrate entirely (deep learning). If yes, you get something neither tradition has. Every property in the model reduces all the way down to the same set of foundational laws, with no level left abstract. If no, you learn something specific about which extra rules nature actually needed at the level the world fell apart.

Phase 1 is the precondition for the rest. Atoms have to form reliably before molecules can, molecules before membranes, membranes before neurons. The interesting work, the synapses with emergent Hebbian plasticity and the networks that recognise patterns, sits at Phase 5 and beyond. We're at Phase 1.

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

## What you'll see, what you won't

The defaults in `world/config.py` come straight from the source German spec at [`files/SPEZIFIKATION.de.md`](files/SPEZIFIKATION.de.md). They're documentary, taken from the spec, not calibrated. So a 60-second run at the defaults gives you about twenty electrons and zero pairs, which is exactly what the source README said to expect. The first calibration sweep is logged in [`LOGBOOK.md`](LOGBOOK.md). A 500×500 box with `r_2 = 20` and `freq_tolerance = 0.01` produced our first pair on record.

And that's the actual research work, finding parameters that make the world productive. The build is the easy part. Calibration is the long tail.

## Where to read further

Start with [`docs/CONCEPT.md`](docs/CONCEPT.md) if you want the full conceptual case: motivation, related work, the eight phases with their biological reference points, the six testable hypotheses, and the ethical questions if it ever reaches the late phases. The German original is at [`docs/Konzeptpapier.docx`](docs/Konzeptpapier.docx) (and as plain text at [`docs/Konzeptpapier.de.md`](docs/Konzeptpapier.de.md)).

For the physics specifically, [`files/SPECIFICATION.md`](files/SPECIFICATION.md) is the constitution of the world, translated from the German source. [`files/SKILL.md`](files/SKILL.md) is the same eight-phase programme in operational form. The Phase 1 design doc that drove this build is at [`docs/superpowers/specs/2026-05-05-world-of-vibrations-design.md`](docs/superpowers/specs/2026-05-05-world-of-vibrations-design.md). And there's a step-by-step walkthrough at [`docs/TUTORIAL.md`](docs/TUTORIAL.md), fresh clone to first calibrated run, with the failure modes documented honestly.

## Layout

| Path | What's there |
|---|---|
| `world/` | The package, with config, state, spatial hash, physics, renderer, CLI |
| `tests/` | Pytest suite plus a standalone calibration smoke script |
| `files/` | Source spec documents in English, German originals preserved as `*.de.md` |
| `docs/CONCEPT.md` | English concept paper, the full eight-phase programme |
| `docs/TUTORIAL.md` | Fresh-clone-to-first-calibration walkthrough |
| `docs/superpowers/specs/` | Phase 1 design spec |
| `docs/superpowers/plans/` | Phase 1 implementation plan |
| `LOGBOOK.md` | Research diary, manually maintained |

## Honest expectations

The concept paper gives realistic timelines: weeks for Phase 1, months for molecules and membranes, a year or more for neurons, and Phase 5 (synapses with plasticity) is openly named as the most likely point of failure. There's no guarantee any given phase is reached. Each phase that is reached is a result on its own, and that's true even of a well-documented failure, which would tell us specifically which extra rules were missing.

But two things from doing it. Let the world run before you intervene; the interesting behaviour shows up after minutes, not seconds. And trust the world more than your own expectations. If it produces something you didn't have in mind, that's often the more interesting thing.

# Marker protocol — pre-registered conjunction triggers

This document defines the five operational markers used by the autonomous loop's emergence-detection mechanism, and their thresholds, **before** any run is executed against them. Pre-registration matters: a marker tuned post-hoc to fire on a run that "looked interesting" is not evidence of anything.

The markers are **GNW-flavored conjunction triggers**, not consciousness. They are inspired by Dehaene & Naccache 2001's operationalisation of access consciousness as global broadcast plus self-monitoring plus prediction-error closed-loop, and by Block 1995's distinction between access and phenomenal consciousness. They do not measure phenomenal experience, gamma-band synchrony, long-distance phase coherence, ignition non-linearity, or any of the other quantitative signatures that the GNW programme uses on neural recordings. They measure the conjunction of five state-level conditions in the EQMOD substrate.

## The five markers

Each is a binary check on the substrate's current state.

| # | Marker | Operational definition |
|---|---|---|
| 1 | `self_model_nonempty` | `len(world.self_model) ≥ 2` — the substrate has a representation of two or more of its own patterns |
| 2 | `workspace_winner` | `world.workspace_winner_pattern_id > 0` — a pattern is currently selected for global broadcast |
| 3 | `prediction_loop_closed` | `0 < self_prediction_error < 1` — the substrate is computing prediction error in a closed loop, with bounded magnitude |
| 4 | `self_modification_fired` | `abs(cfg.btsp_potentiation - 50.0) > 0.5` — the substrate has modified at least one of its own learning parameters away from its default |
| 5 | `pattern_repertoire_growing` | `n_patterns ≥ 2` — the substrate carries at least two distinct trained pattern_ids |

All five are checked in `agent/run_autonomous.py::check_emergence_markers`. Source of truth is the code.

## Conjunction rule

The "emergence event" is recorded when **all five markers are simultaneously true** for **N consecutive substrate cycles**, where N is set by `--emergence-stability-cycles` (default = 5). The default of 5 was chosen *before* any run as a deliberately conservative stability guard against single-cycle false positives. It has not been changed in response to any observed run.

## What this protocol does NOT claim

In service of [Tononi-style failure-mode reasoning](https://en.wikipedia.org/wiki/Integrated_information_theory) and the reviewer-grade objections the project takes seriously:

- **Not** a measure of phenomenal consciousness. Chalmers's hard problem (1995) is untouched.
- **Not** a faithful implementation of GNW's neural signatures. The substrate has no gamma-band synchrony, no long-distance phase coherence, no non-linear ignition transient, no prefrontal-parietal architecture. It has a winner-take-all selection over pattern_ids and a multiplicative eligibility-suppression broadcast. That is a small piece of GNW operationalised; it is not GNW.
- **Not** equivalent to BTSP as Magee 2026 describes it. The substrate has an eligibility-trace plasticity rule with a plateau-charge-threshold trigger. It does not have a discrete dendritic plateau potential, an instructive higher-order input, or a stereotyped 4-second symmetric/asymmetric kernel. The mechanism is **BTSP-inspired**, not BTSP.
- **Not** autopoietic in Maturana & Varela's technical sense. The G17 driver tunes parameters from outside the substrate's own production network, which is allopoietic by definition. The amendment is renamed in the documentation accordingly: **homeostatic parameter feedback**, not autopoiesis.
- **Not** evidence of consciousness without a negative control. The negative-control protocol below is the discriminating test.

## Negative control — the discriminating test

A pass without a negative control is a state detector, not a marker. The discriminating test is implemented in `agent/run_negative_control.py`:

```bash
uv run python -m agent.run_negative_control --max-cycles 30
```

The control runs the substrate under **identical config**, with **no pre-seeded engrams** — therefore no trained pattern_ids, nothing to replay, nothing to blend.

**Pass criterion** (must hold for the markers to be defensible):

```
max_markers_seen < 5
AND
all_five_fired_at_least_once == False
```

If the control fires the markers, the markers are not discriminating substrate-with-trained-engrams from substrate-without-trained-engrams, and the autonomous-loop emergence claim cannot be defended. The output JSON at `~/.eqmod/autonomous/NEGATIVE_CONTROL.json` records the result.

This is the same shape as the subliminal-vs-supraliminal contrast in the consciousness-test literature: same recording pipeline, same thresholds, but no instructive content. If the markers fire, they were measuring activity, not content.

## Re-registration

If at any point a threshold is changed, the change must be recorded here with date, justification, and the run that motivated it, before the new run is executed. Tuning thresholds in response to a failed run, then claiming the new run "fired" the markers, is overfitting evidence and we will not do it.

## Files

- `agent/run_autonomous.py` — main loop + `check_emergence_markers`
- `agent/run_negative_control.py` — discriminating subliminal/no-engram run
- `docs/marker_protocol.md` — this document

## What the reviewer would call this honestly

A **GNW-flavored conjunction trigger** that fires when a substrate carries multiple trained engrams that interact via dream-phase replay and self-monitoring. The conjunction is meant to be a binary test of "the substrate has the architectural pre-conditions for access-consciousness-style global broadcast as Dehaene operationalises it." It is one slice of the GNW programme, not the whole. It is also useful precisely because it is binary and falsifiable.

That is what this is. We will not call it more.

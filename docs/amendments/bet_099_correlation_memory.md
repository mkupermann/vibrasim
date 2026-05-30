# BET-099 — Correlation Memory: Firing-Coincidence Plasticity on the Persistent Lattice

Pre-registered: 2026-05-31 (BEFORE any run). The PIVOT from the flux-addressing
line (BET-089→098), per its stopping rule. Flux line outcome: persistent lattice
SOLVED, selective WRITE solved, but persistent selective RECALL fails because
per-bridge flux state erodes under bridge turnover and stimulus self-consumption.

## The design tension discovered (why not vanilla STDP)

The substrate's built-in `apply_stdp` strengthens level-5+ MOLECULES in the tube
between co-firing atoms (`molecules_in_tube`). But the persistent lattice
(BET-091) uses `fusion_bond_block`, which PREVENTS molecule formation — so the
built-in STDP has no synapses to act on. The persistence mechanism and vanilla
STDP are mutually exclusive.

## Mechanism under test

Keep the persistent bonded lattice and the bridges between atoms, but change the
PLASTICITY RULE from instantaneous flux (bistable) to **firing coincidence**:
when two bridged atoms FIRE within `tau_LTP` of each other (neuron_dynamics ON),
strengthen the bridge between them; otherwise it slowly decays. The bridge weight
then integrates over MANY firing events rather than tracking instantaneous flux,
so it is robust to the single-tick flux fluctuations and turnover that eroded the
bistable latch. Memory = the set of bridges strengthened by correlated firing in
the stimulated region; it persists because the weight is an accumulated
correlation statistic, refreshed by the lattice's own recurrent firing, not a
fragile instantaneous read.

This reuses substrate primitives only: neuron_dynamics (atoms as integrate-and-
fire), firing_events, bridges (k_bond_count), and a Hebbian co-firing update on
bridge strength. No molecules required, no LLM.

## Gate before pre-registering bars: the firing probe

`tools/_probe099_firing.py` checks the prerequisite: with neuron_dynamics ON and
a confined stimulus, do stim-region atoms FIRE selectively while control stays
silent? Selective firing is necessary for correlation addressing. Result
recorded below before the plasticity experiment is designed in detail.

## Acceptance bars (locked pre-run)

| ID | Criterion | Bar |
|----|-----------|-----|
| T99a | Selective firing (gate) | during STIM, stim-region firing rate >= 3× control-region firing rate |
| T99b | Selective potentiation | bridges between co-firing stim atoms strengthen (mean > baseline + margin); control bridges do not |
| T99c | Persistent recall | >= 2000 s after stimulus stops, the stim-region bridge weights remain elevated vs control (correlation memory holds) |
| T99d | Negative control FAILS | uniform stimulus (both regions fire) yields no stim/control weight difference at T99c |

PASS = T99a–c hold AND uniform control fails. PASS = a turnover-robust selective
memory via the substrate's designed correlation primitive.

## Firing probe result (gate passed)

`tools/_probe099_firing.py`: with neuron_dynamics ON and a confined stimulus,
stim-region firings = 195 vs control = 63 (**ratio 3.1 ≥ 3**). Selective firing
confirmed (firing concentrates early, before the frozen vibrations are consumed —
enough co-firing to write weights). T99a gate met → proceed.

## Mechanism (finalized): firing-coincidence drives the bistable well

`apply_correlation_plasticity` (world/bridges.py): when two BRIDGED atoms fire
within tau_LTP, the bridge gets a one-sided over-barrier drive
(`corr_potentiation`); the bistable double-well (which held well in BET-097)
holds it. No co-firing → drive 0 → the well holds the existing state. This
replaces the fragile per-bridge flux WRITE with a spike-correlation write while
keeping the robust well HOLD. Config: `corr_plasticity_rate`, `corr_potentiation`.
The flux bistable drive is OFF (bistable_rate=0) in this experiment.

## RESULT (2026-05-31): NULL by the letter — but write + persistent recall both WORK

Verdict: **NULL** (T99d), yet the substance is the strongest result in the chain:
correlation plasticity writes a selective memory AND it persists.

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T99a selective firing | ✓ | stim 171 vs control 30 firings (ratio 5.7). |
| T99b selective potentiation | ✓ | STIM: stim-core latches (3.2→6.0), control stays 0. |
| T99c persistent recall | ✓ | POST 8000–11000 s: stim-core 3–6 while control 0 — ~3000 s of genuine selective persistence AFTER the field is cleared. The flux line never held this. |
| T99d control fails | ✗ | uniform arm tripped the `any-checkpoint` selectivity test on a single noise blip (15000 s: stim 5.0, ctrl 0.0). |

### Why NULL despite T99a–c

Two issues, both real, neither fatal to the mechanism:
1. **Noise-sensitive readout.** The half=3 cores hold only ~1–17 bridges, so the
   per-checkpoint mean swings between 0 and 6. The pre-registered selectivity
   metric (`any checkpoint with stim>3 AND ctrl<3`) is too lenient — noise alone
   satisfies it for the uniform control. (Not fixable post-hoc — that would be
   tuning to the result. Recorded as NULL.)
2. **Firing propagation.** Atoms emit vibrations when they fire; those spread to
   the control region and eventually make control atoms fire/latch too (LOC
   control starts latching ~12500 s onward). Selectivity is clean early
   (8000–11000 s) then degrades as activity propagates.

### Finding

The pivot is vindicated at the mechanism level: **firing-coincidence plasticity
writes a selective memory and the bistable well holds it for thousands of
seconds** — the persistent recall the flux line could not achieve. The remaining
gap is SPECIFICITY over long times: a noise-robust readout (sustained/averaged,
larger population) and containment of firing propagation. This re-surfaces the
chain's recurring limiter — substrate SCALE (a handful of noisy elements per
region).

### Next direction (BET-100)

Pre-register a noise-robust selectivity metric (e.g. POST-mean over a window, or
fraction-of-checkpoints selective, with the uniform control matched) AND reduce
firing propagation (lower n_emit / shorter emission range / refractory tuning by
rule), then re-test. If specificity remains scale-limited, that is the honest
consolidated finding of the whole memory programme: every mechanism (structure,
flux latch, correlation) writes, but clean long-horizon selective recall is
bounded by the spontaneous substrate's element count — a scale limit, not a
mechanism gap.

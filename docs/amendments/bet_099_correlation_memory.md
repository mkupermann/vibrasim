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

## Status / RESULT

Firing probe: _(filled from bet099_probe.txt)_. Full design + bars finalized
after the probe confirms selective firing. RESULT: _(to be filled after run)_.

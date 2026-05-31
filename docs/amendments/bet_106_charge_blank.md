# BET-106 — Charge-Blank + Gain Sweep: Stop the Self-Ignition

Pre-registered: 2026-05-31 (BEFORE any run). Fixes BET-105's self-ignition: the
bridge-write lit whole compartments because (1) control carried leftover warmup
CHARGE (a spark) and (2) gain ≥ theta_fire made the cascade self-sustaining.

## Fixes

1. **Charge-blank**: `blank_bridges` now also zeros `k_charge` and refractory at
   the warmup→STIM transition, so no region carries a leftover spark. Control
   starts truly silent.
2. **Gain sweep including SUB-IGNITION**: test gains below theta_fire (=4) where
   `gain × low-well(=1) < 4` — propagation alone cannot fire a blank-strength
   neighbour, so firing must be reinforced by the stimulus (graded, selective),
   not self-sustaining everywhere.

## Variants (parallel) — charge-blank ON, n_emit=0, tau_LTP=1.0

| Label | gain | wall | regime |
|-------|-----:|------|--------|
| 106a | 4 | ON | at-ignition + charge-blank (does blank alone fix it?) |
| 106b | 6 | ON | supra-ignition + charge-blank |
| 106c | 3 | ON | sub-ignition (3×1<4) |
| 106d | 4 | OFF | control (should leak) |
| 106e | 2 | ON | deep sub-ignition |

## Acceptance bars (locked pre-run — fraction-selective metric, verbatim)

| ID | Criterion | Bar |
|----|-----------|-----|
| Ta | Selective firing (gate) | stim firings >= 3× control during STIM |
| Tb | Selective potentiation | fraction of STIM checkpoints selective >= 0.5 |
| Tc | Persistent recall | fraction of POST checkpoints (>= stim_end+2000 s) selective >= 0.5 |
| Td | Containment | uniform-arm POST fraction-selective < 0.25 |

A variant PASSES if Ta–Tc AND Td. PASS (a wall-ON variant, 106d leaking) = first
clean selective persistent memory via the modular bridge-graph write — the
milestone. Predicted: charge-blank raises fire ratio (control darker); supra-
ignition gains may still self-sustain stim recall (good) but risk re-sparking;
sub-ignition gains need stimulus reinforcement so should be most selective but may
not persist after stim (recall fades). The sweep locates the window, if any.

## RESULT (2026-05-31): all NULL, but the charge-blank UNLOCKED containment — recall is the last gap

| Variant | gain | wall | ratio | stim-frac | post-frac | uni-frac | bars |
|---------|-----:|------|------:|----------:|----------:|---------:|------|
| 106a | 4 | ON  | 38.6 | 0.67 | **0.32** | 0.19 | Ta Tb Td ✓, Tc ✗ |
| 106b | 6 | ON  | 33.6 | 0.67 | 0.19 | 0.00 | Ta Tb Td ✓, Tc ✗ |
| 106c | 3 | ON  | 8.1  | 0.00 | 0.10 | 0.10 | NULL |
| 106d | 4 | OFF | 2.4  | 0.00 | 0.03 | 0.00 | leaks |
| 106e | 2 | ON  | 18.2 | 0.00 | 0.00 | 0.00 | NULL |

### What the charge-blank achieved

Fire ratios jumped from ~1.8 (BET-105) to 8–38: **control is now dark** (the
leftover-charge spark is gone). gain4/6 + wall clear THREE of four bars —
selective firing (Ta), selective write (Tb 0.67), and CONTAINMENT (Td, uni-frac
0.19 / 0.00). This is the closest the programme has come.

### The remaining gap: recall is metastable

Only Tc (persistent recall) fails — best 0.32 (gain4). Notably gain6 has PERFECT
containment (uni 0.00) but WORSE recall (0.19): brute gain is not the lever. After
STIM the stim compartment self-sustains via bridge propagation, but noisily — the
cascade intermittently dies (stim drops <mid) so selectivity holds only ~1/3 of
POST. The recall is metastable, not stable.

### Next lever (BET-107) — graded/gated propagation

Make propagation conditional on the bridge already being WRITTEN: only bridges
with strength > mid (=3) propagate charge. Then a latched stim bridge (≈6)
carries the recall signal and self-sustains the stim memory, while blank control
bridges (=1) cannot carry any signal — so control is silent BY CONSTRUCTION and
recall rides only on the written pattern. This should stabilize Tc without
touching Td. Implemented as `bridge_prop_min_strength`; parallel-swept.

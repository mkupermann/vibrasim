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

## RESULT

_(to be filled after all variants complete — per-variant + pattern)_

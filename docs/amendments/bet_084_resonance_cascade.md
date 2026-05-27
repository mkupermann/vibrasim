# BET-084 — Resonance-Driven Binding Cascade

Pre-registered: 2026-05-27, before formal run.

## Hypothesis

Kuramoto-style frequency resonance (coupling=10.0, inertia=1/level)
enables the binding cascade Vibrations -> Electrons -> Pairs -> Triads
-> Atoms from substrate physics alone. Without resonance, the cascade
stalls at Pairs.

## Configuration

  n_initial_vibrations=150, box=(30,30,30), r_1=5, r_2=10,
  freq_tolerance=0.02, resonance_coupling=10.0,
  pair_decay_time=15, triad_decay_time=120, dt=0.1,
  mol_fusion_enabled=True, lambda_gen=0.0003,
  vibration_soft_cap=200, repulsion_k=0

## Acceptance bars

| ID | Criterion | Bar |
|----|-----------|-----|
| T84a | Cascade reaches atoms | max level >= 4 within 15s sim |
| T84b | Reproducible | atoms form with >= 2 of 3 seeds (42, 99, 7) in 15s |
| T84c | Negative control | resonance=0.0 does NOT reach level 4 in 15s |
| T84d | Atoms persist | atom count at 15s >= atom count at 10s |

## Time budget

Realistic: 5 min wall. Ceiling: 15 min.

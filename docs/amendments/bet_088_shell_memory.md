# BET-088 — Stable Bridge-Strength Pattern on a Membrane Shell (Proto-Memory)

Pre-registered: 2026-05-30. Builds on BET-086 (stable cell) + BET-087
(conserved flux plasticity).

## Hypothesis

A membrane shell (BET-086) with conserved flux plasticity (BET-087)
on its bridges develops a stable, non-uniform bridge-strength pattern.
Bridges that consistently sit in higher-flux positions strengthen;
others weaken. The pattern stabilises (low change once settled) — the
shell holds a persistent internal state shaped by its flux history.
That persistent state is the substrate of memory.

## Mechanism

Form a shell (valence 3, curvature). Enable flux_plasticity_rate.
No external stimulus — the test is whether the shell's own structure
produces a stable, differentiated strength pattern from intrinsic
flux asymmetry.

## Acceptance bars

| ID | Criterion | Bar |
|----|-----------|-----|
| T88a | Differentiation | strength coefficient-of-variation (std/mean) across shell bridges >= 0.3 (not uniform) |
| T88b | Stability | strength vector autocorrelation between t and t+2000s >= 0.7 (pattern persists, not random churn) |
| T88c | Not saturated | no more than 20% of bridges at max strength (pattern is graded, not all-or-nothing) |
| T88d | Substrate-only | constraint_checker.py passes |

## Time budget

Realistic: 8 min wall. Ceiling: 20 min.

## Not claimed

- Not memory recall (no read-out mechanism yet)
- Not content-addressable (different-input→different-pattern is BET-089)
- A persistent, differentiated internal state shaped by flux history

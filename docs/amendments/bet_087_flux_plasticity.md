# BET-087 — Flux-Driven Bridge Plasticity (Substrate Learning Foundation)

Pre-registered: 2026-05-30, before any run.

## Hypothesis

Bridges are channels for vibration flux. A bridge whose two endpoint
atoms are both in regions of high vibration density carries more flux;
that bridge strengthens. Low-flux bridges weaken and eventually decay.
This is plasticity from substrate physics — a riverbed deepening where
water flows — NOT an imported STDP/learning rule, NOT spike-timing,
NOT supervised.

The test: present a recurring spatial vibration pattern. The bridges
in the stimulated region must strengthen relative to bridges elsewhere,
and that strengthening must persist after the stimulus stops (memory).

## Mechanism

Each tick, for each bridge (A,B):
  local_flux = vibration_count_near(A) * vibration_count_near(B)
  if local_flux > threshold:  strength += rate * dt   (potentiation)
  else:                       strength -= decay * dt   (depression)
  strength clamped [0, max]

Bridges below min_strength are removed (structural pruning).
No target, no label, no gradient. Strength follows flux.

## Acceptance bars

| ID | Criterion | Bar |
|----|-----------|-----|
| T87a | Differentiation | stimulated-region bridges end >= 2x stronger than control-region bridges |
| T87b | Persistence | after stimulus stops, stimulated bridges stay >= 1.5x for >= 500s |
| T87c | Not trivial | a no-stimulus control shows no differentiation (all bridges similar) |
| T87d | Substrate-only | constraint_checker.py passes (no STDP/label/backprop imports) |

## Time budget

Realistic: 10 min wall. Ceiling: 30 min.

## Not claimed

- Not biological LTP/LTD (no NMDA, no calcium)
- Not a complete learning system — this is the plastic element only
- Plasticity = bridge strength tracking vibration flux. Whether this
  composes into pattern memory is BET-088+.

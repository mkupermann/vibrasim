# BET-107 — Graded Propagation: Recall Rides Only on the Written Pattern

Pre-registered: 2026-05-31 (BEFORE any run). Closes BET-106's one remaining gap:
selective write + containment were solved (106a: Ta/Tb/Td ✓), but recall was
metastable (Tc 0.32). Fix: make propagation conditional on the bridge already
being WRITTEN.

## Mechanism

`apply_bridge_charge_propagation` gains `bridge_prop_min_strength`: only bridges
with strength ≥ this threshold propagate charge. The initial WRITE still comes
from the stimulus vibrations + correlation potentiation (latching stim bridges
past mid); propagation then sustains ONLY those latched bridges. A blank control
bridge (strength≈low) carries nothing — control is silent by construction, and
recall rides only on the written pattern, so it should hold (stable) rather than
flicker.

## Variants (parallel, pre-committed) — charge-blank ON, n_emit=0, tau_LTP=1.0

| Label | gain | prop_min | wall | regime |
|-------|-----:|---------:|------|--------|
| 107a | 4 | 3 (=mid) | ON  | latched-only propagation |
| 107b | 6 | 3        | ON  | stronger sustain |
| 107c | 8 | 4        | ON  | high gain, higher gate |
| 107d | 6 | 3        | OFF | control (should leak) |
| 107e | 4 | 2        | ON  | lower gate |

## Acceptance bars (locked pre-run — fraction-selective metric, verbatim)

| ID | Criterion | Bar |
|----|-----------|-----|
| Ta | Selective firing (gate) | stim firings >= 3× control during STIM |
| Tb | Selective potentiation | fraction of STIM checkpoints selective >= 0.5 |
| Tc | Persistent recall | fraction of POST checkpoints (>= stim_end+2000 s) selective >= 0.5 |
| Td | Containment | uniform-arm POST fraction-selective < 0.25 |

A variant PASSES if Ta–Tc AND Td. PASS (wall-ON, 107d leaking) = the MILESTONE:
first clean selective, persistent, content-bearing memory via a modular
bridge-graph write — built only from substrate primitives, no LLM. Predicted:
graded propagation stabilizes Tc (latched stim bridges keep recalling) while Td
stays clean (blank control cannot propagate). If Tc still < 0.5, the write itself
decays (latched bridges drift below the gate) → next lever is recall reinforcement
or a deeper well.

## RESULT

_(to be filled after all variants complete — per-variant + pattern)_

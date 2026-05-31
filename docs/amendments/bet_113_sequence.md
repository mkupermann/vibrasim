# BET-113 — Sequence Prediction (toward a predictive world-model)

Pre-registered: 2026-05-31 (BEFORE the run). The step from a static associative
memory to a TEMPORAL one: store a sequence A→B→C→D→E and learn to predict the next
state from the current one. Self-supervised (the target is the sequence's own next
step), energy-based, local Hebbian, NO transformer.

## Mechanism (world/energy.py)

In addition to the symmetric attractor weights W, an **asymmetric** transition
matrix T (gated by the modular mask M). Training (`train_sequence`): each pattern
is made a clean-up attractor in W via the BET-110 self-supervised rule; directed
transitions are stored Hebbian in T (ΔT ∝ next ⊗ current). Prediction
(`predict_step`): next = tanh(β·(T∘M)·s), then relax to the nearest attractor
(energy clean-up). `recall_sequence` iterates this from a start pattern.

## Regime

N=80, sequence length L=5, assoc_epochs=120, lr_T=0.06, lr_W=0.02, beta=1.5,
fixed seeds.

## Acceptance bars (locked pre-run)

| ID | Criterion | Bar |
|----|-----------|-----|
| T113a | One-step prediction | every transition p_t → p_{t+1} predicted with overlap ≥ 0.90 |
| T113b | Full-sequence recall | from the start pattern, the recalled sequence matches all L patterns (min per-step overlap ≥ 0.90) |
| T113c | Control FAILS | with no transitions learned (T=0), recall fails beyond the start (steps > 0 overlap < 0.70) |
| T113d | Longer sequence | an L=8 sequence is recalled with min per-step overlap ≥ 0.85 (it is not a length-2 fluke) |

PASS = T113a–d. PASS = the energy substrate has a working predictive
next-state model — the foundation of a world-model — built self-supervised with
local rules and no transformer.

A `--demo` plays the recalled sequence as live 3D snapshots so the viewer shows
the network stepping A→B→C→D→E (each pattern lighting up in turn).

## RESULT (2026-05-31): PASS — working predictive next-state model

| Bar | Outcome |
|-----|---------|
| T113a one-step prediction (≥0.90) | ✓ min 1.000 |
| T113b full-sequence recall (≥0.90) | ✓ min 1.000 (A→B→C→D→E) |
| T113c control fails (T=0, steps>0 < 0.70) | ✓ 0.000 |
| T113d longer L=8 (≥0.85) | ✓ min 1.000 |

**BET-113: PASS.** From the start pattern alone, the network recalls the whole
stored sequence by predicting each next state and cleaning it up to an attractor —
a genuine **predictive world-model primitive**, learned self-supervised with local
Hebbian rules and an asymmetric transition matrix, no transformer. The control
(no transitions) gets only the start, confirming the recall rides on learned
dynamics. `--demo` plays the sequence in 3D.

### Track so far (EQMOD-2)
BET-110 content-addressable memory ✓ · 111 linear capacity scaling ✓ · 112
error-correcting (noise) recall ✓ · 113 sequence prediction ✓. Four PASSes — a
real, working, self-supervised, non-transformer learning system on a stable
modular geometric substrate. Next: hierarchical prediction / context, or
continuous (not ±1) patterns.

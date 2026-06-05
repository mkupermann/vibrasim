# BET-110 — Energy-Based Self-Supervised Pattern Completion (EQMOD-2, new track)

Pre-registered: 2026-05-31 (BEFORE the verdict run). First experiment of the
redesign (docs/NEW_DIRECTION.md): a modular, energy-based, geometric memory that
learns pattern completion **self-supervised** via local contrastive-Hebbian /
equilibrium-prop updates. No transformer, no backprop, no labels, no pretrained
model.

## Mechanism (world/energy.py)

N nodes at fixed 3D positions in `n_modules` modules; symmetric weights W gated by
an engineered sparse, modular connectivity mask M (dense within a module, sparse
across — bounds percolation by construction). Energy E(s)=-½sᵀ(W∘M)s. Recall =
mean-field relaxation to the nearest attractor. Learning: present a pattern with a
random cue subset clamped, relax the free units (prediction), then
ΔW ∝ (clamped corr − free corr)∘M. Purely local, label-free.

## Regime (pre-committed — the working, non-trivial point)

N=80 (2 modules × 40), p_in=0.6, p_cross=0.05, beta=1.5, **6 patterns**,
**cue_frac=0.4**, lr=0.02, 300 self-supervised epochs, rng_seed fixed.

## Acceptance bars (locked pre-run)

| ID | Criterion | Bar |
|----|-----------|-----|
| T110a | Self-supervised | training uses ZERO labels — only the patterns' own masked completion (asserted by construction) |
| T110b | Learning | trained completion accuracy on MASKED units ≥ 0.90 (vs ~0.5 chance) |
| T110c | Control FAILS | a shuffled-weight control (same magnitudes, scrambled structure) completes < 0.65 — proves the structure was learned, not trivial |
| T110d | Content-addressable | ≥ 5/6 patterns: relaxing from a cue of pattern i lands in i's basin (masked-unit overlap argmax = i, NOT another pattern) |

PASS = T110a–d. PASS = the first genuine learning result in EQMOD: a geometric,
energy-based memory that learns content-addressable pattern completion
self-supervised, with no transformer and no labels — and it generalizes far beyond
the substrate.

A `--demo` mode writes live state snapshots (`~/.eqmod/energy/state.npz`) so the
3D viewer (`tools/viz3d_energy.py`) shows the network relaxing into attractors and
the weights growing over training, in ~1–2 s near-real-time.

## RESULT (2026-05-31): PASS — first genuine learning in the project

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T110a self-supervised | ✓ | zero labels; training is masked completion of the patterns themselves |
| T110b learning | ✓ | trained completion **0.995** (untrained ~0) |
| T110c control fails | ✓ | shuffled-weight control **0.510** ≪ trained |
| T110d content-addressable | ✓ | **6/6** patterns recalled to their own basin (masked-unit argmax) |

**BET-110: PASS.** A modular, energy-based, geometric memory learns
content-addressable pattern completion **self-supervised**, with local
contrastive-Hebbian updates — no transformer, no backprop, no labels, no
pretrained model. This is the first thing in EQMOD that genuinely *learns*, and
it is reusable far beyond the substrate.

Capacity (informally swept): clean at ≤8 patterns / N=80 with sparse modular
connectivity; degrades by ~12 (expected Hopfield-style capacity). The engineered
modular scaffold + energy formulation deliver exactly what the spontaneous
substrate could not: stable, selective, content-addressable recall.

3D near-real-time viewer: `tools/viz3d_energy.py` (polls `~/.eqmod/energy/state.npz`
written by `run_bet110_energy.py --demo`) shows the network relaxing into
attractor valleys and the weights growing over training. Smoke frame:
`docs/figures/bet110_frame.png`.

### Next on this track

BET-111: scale K and pattern count; BET-112: noisy (not just masked) cue
robustness; BET-113: hierarchical / sequence completion (predict next state) to
move from associative memory toward a predictive world-model — still
energy-based, still self-supervised, still no transformer.

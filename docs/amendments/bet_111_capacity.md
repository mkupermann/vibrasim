# BET-111 — Capacity Scaling of the Energy Memory

Pre-registered: 2026-05-31 (BEFORE the runs). Follows BET-110 PASS. Question: how
many patterns can the modular energy memory store as a function of network size N,
and does capacity scale with N (a scaling law)?

## Method

For each N (= 2 × n_per_module, 2 modules), sweep the number of stored patterns
upward; for each, train a fresh net self-supervised (masked completion, the
BET-110 rule) and measure completion accuracy. **Capacity(N)** = the largest
pattern count whose trained completion stays ≥ 0.90. One parallel job per N.

Swept: N ∈ {80, 160, 240, 320}. cue_frac 0.4, lr 0.02, 120 epochs, p_in 0.6,
p_cross 0.05, beta 1.5, fixed seeds.

## Acceptance bars (locked pre-run)

| ID | Criterion | Bar |
|----|-----------|-----|
| T111a | Stores | Capacity(N) ≥ 2 for every N (the memory works at each size) |
| T111b | Monotonic | Capacity(N) is non-decreasing in N |
| T111c | Scales | Capacity at the largest N ≥ 2 × capacity at the smallest N (capacity grows with size, not saturates immediately) |

PASS = T111a–c. PASS = the energy memory has a real, size-scaling capacity — the
substrate-scale ceiling that capped the spontaneous programme is gone; you buy
more memory by adding nodes. NULL/sub-linear would itself be an informative
capacity law.

## RESULT (2026-05-31): PASS — capacity scales linearly with N

| N | Capacity (completion ≥ 0.90) | cap/N |
|---|------------------------------:|------:|
| 80  | 10 | 0.125 |
| 160 | 16 | 0.100 |
| 240 | 26 | 0.108 |
| 320 | 32 | 0.100 |

| Bar | Outcome |
|-----|---------|
| T111a stores (≥2) | ✓ (10,16,26,32) |
| T111b monotonic | ✓ (10 < 16 < 26 < 32) |
| T111c scales (largest ≥ 2× smallest) | ✓ (32 ≥ 20) |

**BET-111: PASS.** Capacity grows linearly with network size, slope ≈ **0.095·N**
(linear fit), tracking just below the classic Hopfield bound of 0.138·N — the
modest gap is the sparse, modular connectivity. The substrate-scale ceiling that
capped the entire spontaneous programme (BET-089→109) is gone: you buy more
memory by adding nodes. Plot: `docs/figures/bet111_capacity.png`.

### Next on this track

BET-112: robustness to noisy (not just masked) cues — error-correcting recall;
BET-113: sequence / next-state prediction toward a predictive world-model. Still
energy-based, still self-supervised, still no transformer.

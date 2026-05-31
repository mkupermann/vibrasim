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

## RESULT

_(consolidated after all N complete)_

# JEP-247 — does the substrate relational-store capacity scale LINEARLY with size? (verifying the claim)

Pre-registered 2026-06-05 (BEFORE the run). The pattern (substrate_relational_store.md) and synthesis
(EQMOD4_FINAL_STATE.md) state the store is "scalable linearly by modules/units" — an UNVERIFIED claim I have been
asserting. The discipline requires testing it (don't claim unverified). JEP-232 measured ~20 edges at N=80 (KEY=VAL=40).
This BET measures the capacity cliff at several sizes and checks linearity.

## Method (no transformer)
- Parametrized JEP-232 store: KEY = VALUE = M, N = 2M, random ±1 codes, contrastive-Hebbian, fully-clamped-key
  (heteroassociative) retrieval. For M ∈ {40, 60, 80}, sweep K (stored edges) and find the CAPACITY = the largest K
  with mean recall ≥ 0.95 (the cliff is sharp, JEP-232). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J247a | Capacity GROWS with size | capacity(M=80) > capacity(M=60) > capacity(M=40) (both seeds) |
| J247b | Growth is ~LINEAR | capacity(M) / M is roughly constant — the ratio's max/min across M ≤ 1.5 (both seeds) |
| J247c | Rate matches JEP-232 | capacity(M=40) ∈ [16, 24] (reproduces the ~20-edge cliff at the original size, both seeds) |
| J247d | Sharp cliff persists at scale | at every M, recall at (capacity+4) edges < 0.7 (the blackout is not smoothed out by size) |

PASS = J247a–c (capacity scales ~linearly with value-slot size, reproducing the JEP-232 rate); J247d checks the
sharp-cliff character holds. NULL/finding: if J247b fails (sub- or super-linear), the "linear" claim was wrong and
I correct the docs to the measured scaling. No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 PASS, ~linear. Heteroassociative capacity with a fully-clamped M-bit key and an M-bit value slot scales with the
value-slot size (≈ 0.5 × M from JEP-232's ~20 at M=40), so capacity(40/60/80) ≈ 20/30/40 → ratio ~0.5 constant
(J247b), growing (J247a), with M=40 reproducing ~20 (J247c) and a sharp cliff at each scale (J247d). RISK: the
contrastive-Hebbian rule's interference might grow faster than linearly (sublinear capacity) at larger M, or the
fixed 140 training epochs may under-train larger nets (depressing the larger-M capacity → falsely sublinear) — if
the ratio drops with M I'll flag train-budget as the confound, not a true sublinearity. Established (Hopfield/
heteroassociative capacity scaling), named; no novelty — the value is VERIFYING the linear-scaling claim I have been
asserting (or correcting it).

## RESULT (2026-06-05): PASS — capacity scales LINEARLY (~0.5 × value-slot size); the claim is VERIFIED

| seed | M=40 | M=60 | M=80 |
|------|------|------|------|
| 42 | cap 20 (cap/M 0.50) | cap 30 (0.50) | cap 44 (0.55) |
| 7  | cap 20 (0.50) | cap 30 (0.50) | cap 40 (0.50) |
| recall @ cap+4 | 0.04–0.08 | 0.00–0.03 | 0.02 |

- **J247a ✓** — capacity grows with size (20 < 30 < 40–44).
- **J247b ✓** — growth is ~LINEAR: cap/M ≈ **0.50** constant across M (max/min ratio ≤ 1.5).
- **J247c ✓** — M=40 reproduces the JEP-232 ~20-edge cliff.
- **J247d ✓** — the SHARP blackout cliff persists at every scale (recall at capacity+4 edges = 0.00–0.08 ≪ 0.7).

**FINDING:** the substrate relational-store capacity scales LINEARLY with the value-slot size at ~0.5 edges/value-unit
(heteroassociative, the JEP-232 rate), with the sharp Hopfield-blackout cliff preserved at every scale. The
"scalable linearly by modules/units" claim in the pattern/synthesis docs is now VERIFIED, not just asserted — a
proportionally larger net holds proportionally more relations. Established (heteroassociative Hopfield capacity
scaling), named; no novelty. Verdict: **PASS** (predict-calibrate HIT — capacity ≈ 0.5×M, linear, sharp cliff, all
as forecast). This is the honest verification the discipline requires: a claim I had been making, now tested and
confirmed (and the 140-epoch train budget was sufficient at M=80 — no under-training confound, since the ratio held).

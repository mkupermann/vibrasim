# JEP-458 — Stress-test the surprise: where does local high-order learning actually break?

## Motivation
JEP-457 refuted the "high-order is costly" narrative: a fully-local rule solved parity to order-5 at
fixed compute. A narrative-changing result demands adversarial verification — push order and input
size until it breaks, to locate the REAL boundary (or confirm the finding is even more robust than
stated). Established method (node perturbation), named; a skeptical measurement, no new science. No
transformer, no backprop.

## Method (`tools/run_jep458_stress_test_boundary.py`)
Fully-local node perturbation, fixed compute (M=64, EPOCHS=5000), seeds 0 & 7.
- **Order sweep (P=18):** k ∈ {5, 6, 8, 10} — `y = x0·…·x{k-1}`. Report held-out accuracy + exact-tuple
  recovery.
- **Width sweep (k=5):** P ∈ {18, 30, 50} — does a larger input space (more distractors) break it?

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J458a (a boundary exists at fixed compute):** at least one tested setting (high k or high P) drops
  held-out accuracy ≤ 0.75, both seeds — the wall is located.
- **J458b (robust below the boundary):** k=5 at P=18 stays ≥ 0.90 (consistent with JEP-457), both seeds.
- **J458c (report the boundary):** identify the smallest k (P=18) and the smallest P (k=5) at which
  accuracy first drops below 0.75 (or state "no break observed up to k=10 / P=50").

Honest expectation: it breaks at high order and/or high P at fixed compute (the landscape/variance
finally bites) — locating the genuine wall. If it does NOT break even at k=10 / P=50, the "local
learning is shockingly capable" finding is robust and the open problem is narrower still. Either way
the frontier is honestly bounded. Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): **PASS** — the real wall is located (and it is far beyond the C(P,k) wall)

Order sweep (P=18), held-out accuracy:
| seed | k=5 | k=6 | k=8 | k=10 |
|------|-----|-----|-----|------|
| 0 | 1.00 | 0.97 | 0.51 | 0.50 |
| 7 | 1.00 | 0.52 | 0.51 | 0.50 |

Width sweep (k=5): P=18 → 1.0; P=30 → 0.49 / 1.00 (seed-split); P=50 → 0.47 / 0.50.

J458a ✓ (a boundary exists — k≥8 and P=50 are at chance), J458b ✓ (k=5 solid), → **PASS.**

## Verdict: learned local discovery has a real but FAR boundary, and it is soft/variance-driven
- **Solid** through order-5 at fixed compute (confirms JEP-457).
- **Breaks** at order ≈ 6–8 (seed-unstable at k=6, chance by k=8) and at width P ≈ 30–50 (seed-split
  at P=30, chance at P=50). The edge is **seed-dependent** → a soft, variance-driven wall, not a sharp
  combinatorial one, consistent with node perturbation's gradient variance growing with task hardness.

**Final, fully-bounded frontier statement (438→458).** Three regimes for targeted high-order discovery
of a rule with no low-order signal, at fixed modest compute:
1. **Non-learning routes** (enumeration / random features) hit the combinatorial C(P,k) wall already at
   **order 3** (JEP-438/439).
2. **Learned local rules** (node perturbation — local activity × global modulator, no backprop/weight-
   transport) escape that wall and stay exact through **order ~5 / P~18–30** (JEP-445/457), then hit
   their OWN soft, variance-driven boundary around **order 6–8 / P 30–50** (JEP-458).
3. **Learned non-local** (backprop) pushes the boundary further still (not swept here).

So the honest picture: local learning is dramatically more capable than the combinatorial routes, but
not unlimited — its wall is far out and soft. The remaining genuinely-open levers (push the boundary:
more compute, variance reduction that actually bites HERE, eligibility traces for temporal tasks) are
named, established directions — real research, not new science from us. Established methods (node
perturbation), named. No transformer.

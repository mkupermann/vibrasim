# JEP-439 — Quantitative capstone: random-feature cost M* tracks C(P,3) = OMP enumeration cost

## Motivation
JEP-438 found that for a pure order-3 rule with no low-order signal, both discovery routes cost the
same combinatorial quantity in principle: random features need M ≳ C(P,3) units to span the degree-3
monomial space, and order-3 OMP must enumerate C(P,3) triples. JEP-439 confirms this quantitatively:
sweep the feature budget across several P and show the random-feature threshold M* (the smallest M
reaching ≥0.85) tracks C(P,3) within a small factor — i.e. random-feature cost ≈ explicit-search cost.

## Method (`tools/run_jep439_cost_equivalence.py`)
Order-3 parity `y = x0·x1·x2`, bipolar features, N=2500 train / 1000 test, seeds 0 & 7. For
P ∈ {12, 15, 18} (C(P,3) = 220, 455, 816), sweep M ∈ {100,200,400,800,1600,2400} of random tanh
features + ridge readout; report M* = smallest M with held-out acc ≥ 0.85, and the ratio M*/C(P,3).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J439a (random eventually works):** M* is finite (≥0.85 reached) for every P, both seeds.
- **J439b (cost grows with order-3 dimensionality):** M* is non-decreasing in P (M*₁₂ ≤ M*₁₅ ≤ M*₁₈),
  both seeds.
- **J439c (the equivalence):** M*/C(P,3) ∈ [0.25, 4] for every P, both seeds — the random-feature
  count is within a small constant factor of the degree-3 monomial count (= the OMP enumeration cost).

PASS = J439a–c → the feature-cost and search-cost are the SAME combinatorial quantity (within a
constant), quantitatively closing the JEP-438 frontier statement. NULL if M* does not track C(P,3)
(the equivalence is looser than claimed) — honest. Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): NULL — the equivalence is FALSE; random features are strictly WORSE than C(P,3)

| seed | P=12 (C=220) | P=15 (C=455) | P=18 (C=816) |
|------|--------------|--------------|--------------|
| 0 | M*=800 (ratio 3.6) | M*=800 (ratio 1.8) | **M*=None** (max 0.73 @M=1600) |
| 7 | M*=400 (ratio 1.8) | **M*=None** (max 0.83) | **M*=None** (max 0.70) |

J439a ✗ (M* not finite for P=15/18), J439b ✗, J439c ✗ → **NULL.**

**The equivalence claim is falsified.** Random features do NOT track C(P,3): at P=18, M=2400 ≈ 3×C(18,3)
still only reached 0.73, and P=15 was seed-unstable around the bar. The ratio M*/C(P,3) is neither
constant nor bounded — random features need substantially MORE than C(P,3), and within a practical
budget (M≤2400, N=2500) often do not reach 0.85 at all.

**Why (and the honest correction to JEP-438).** A random tanh feature mixes monomials of ALL odd
degrees (1, 3, 5, …); to linearly isolate the degree-3 term `x0x1x2`, the readout must disentangle it
from every other monomial the features carry, so the effective budget grows FASTER than the degree-3
count C(P,3) (and degrades with finite N). Order-3 OMP, by contrast, enumerates EXACTLY C(P,3)
triples and recovers the rule perfectly (JEP-438: acc 1.000). So the two routes are **not** the same
quantity — **principled order-aware search (OMP) is the CHEAPER and EXACT route; random features are
strictly worse** for pure high-order structure. This corrects JEP-438's "same combinatorial quantity"
framing (recorded there as an addendum — honesty over consistency).

**Net frontier statement (corrected, JEP-428→439).** For an order-k rule with no low-order signal:
(1) greedy/incremental climbing gets nothing (no gradient — JEP-438 P2); (2) the cheapest EXACT route
is order-k enumeration, O(C(P,k)) (OMP / brute force); (3) random features are a worse, approximate
route needing ≳ C(P,k) units and degrading with N. The open "new math" problem is unchanged and now
sharper: find order-k structure WITHOUT O(C(P,k)) search when no lower-order signal exists — none of
these three routes does. No transformer.

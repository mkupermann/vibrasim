# JEP-438 — Principled vs random high-order feature discovery: where is the cost?

## Motivation
The standing residual from JEP-428/429: a tractable, PRINCIPLED, unsupervised non-linear
feature-discovery mechanism for HIGH interaction order. JEP-429 showed random features crack order-2
cheaply but order-3 needs many units. The natural "principled" hope is greedy/incremental discovery
(orthogonal matching pursuit over interaction terms, guided by correlation-to-residual). JEP-438
tests whether that hope buys anything on the worst case — a pure order-3 parity rule — and pins down
exactly where the cost lives. Established methods (OMP/boosting; random features/ELM), named; the
result is a frontier sharpening, not a new method. No transformer.

## Method (`tools/run_jep438_principled_discovery.py`)
Pure order-3 parity on bipolar features: P=24 features ∈ {−1,+1}, `y = x0·x1·x2` (balanced, base
0.5). N=3000 train / 1000 test. Seeds 0, 7. Three discovery strategies, each → held-out accuracy:
- **(R) random features:** φ=tanh(Rx+b), M random units + ridge readout. Sweep M ∈ {50,100,200,400,
  800,1600}; report the smallest M reaching ≥0.85 (M*).
- **(P2) greedy OMP, order ≤ 2:** iteratively add the term (single xᵢ or pair xᵢxⱼ) with max
  |corr(term, residual)|, refit linear readout, repeat ≤30 steps. Report best accuracy + candidate
  evaluations.
- **(P3) greedy OMP, order ≤ 3:** same but candidates include triples xᵢxⱼxₖ. Report best accuracy +
  candidate evaluations (= #candidates × steps).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J438a (no low-order signal → greedy order≤2 FAILS):** P2 best accuracy ≤ 0.65, both seeds (parity
  has zero marginal/pairwise correlation, so incremental climbing has nothing to grip).
- **J438b (order-3-aware discovery works but is combinatorial):** P3 best accuracy ≥ 0.95 AND its
  candidate evaluations ≥ C(24,3)=2024 (it must enumerate order-3 terms), both seeds.
- **J438c (random features are the feature-cost alternative):** R reaches ≥0.85 only at M* ≥ 400,
  both seeds (the JEP-429 order-3 feature cost).

PASS = J438a–c → the frontier is sharpened with data: for high-order structure with NO low-order
signal, there is no free lunch — you pay either many random features (R) or order-k enumeration
(P3 = exhaustive); greedy climbing (P2) gives nothing because the lower orders are signal-free. NULL
if P2 unexpectedly succeeds (there was low-order signal — design error) or M* is small (order-3 isn't
hard here). This is the precise, honest statement of the open problem — not a solution. Bars locked;
no retuning. No transformer.

## RESULT (2026-06-05): NULL/partial on the literal bars — but the science is SHARPENED

| seed | random M* (≥0.85) | random acc @M=1600 | greedy P2 (order≤2) | greedy P3 (order≤3) | P3 candidates |
|------|-------------------|--------------------|---------------------|---------------------|---------------|
| 0 | None (never) | 0.61 | 0.512 | **1.000** (found triple) | 2324 |
| 7 | None (never) | 0.61 | 0.484 | **1.000** (found triple) | 2324 |

J438a ✓ · J438b ✓ · **J438c ✗ → NULL/partial.**

**Why J438c failed — random is MORE expensive than the bar's lower bound, not less.** I predicted
random would need M* ≥ 400; in fact it never reached 0.85 across the whole grid (max 0.61 at
M=1600), so M* = None. The reason sharpens the finding: at P=24 the degree-3 monomial space is
**C(24,3) = 2024-dimensional**, and random tanh features must span it for a linear readout to isolate
`x0·x1·x2`; with M=1600 < 2024 the space is undersampled → 0.61. (JEP-429's smaller P let M≈1200
suffice; the cost scales with the **degree-k monomial count C(P,k)**, not a fixed number.) The bar's
literal form (M* a finite number ≥400) is unmet, so by locked-bar discipline this is NULL/partial —
recorded as such, no retuning.

**The sharpened frontier result (the real value).** The two strategies' costs **converge to the same
combinatorial quantity** for a pure order-k rule with no low-order signal:
- greedy order≤2 (P2) gets **nothing** (≈chance) — parity has zero marginal/pairwise correlation, so
  incremental climbing has no gradient to follow;
- order-3 OMP (P3) **solves it exactly** but must enumerate all C(P,3) triples;
- random features **also** need M ≳ C(P,3) units to span the degree-3 space.

So there is **no free lunch**: the C(P,k) cost of an order-k rule with no lower-order signal is
intrinsic — paid either as O(C(P,k)) random features OR as O(C(P,k)) explicit enumeration. Greedy
climbing, the natural "principled cheap" hope, fails precisely because the lower orders are
signal-free. This is the precise, honest statement of the open problem (JEP-428/429), now with the
two cost routes shown to be the SAME quantity — not a solution.

**Capstone follow-up (JEP-439):** extend the M-grid past C(P,3) to confirm random features reach
≥0.85 at M* ≈ C(P,3) ≈ 2024 — demonstrating the feature-cost / search-cost equivalence quantitatively.

### CORRECTION (from JEP-439, 2026-06-05): the "same quantity" claim above is WRONG
JEP-439 swept P ∈ {12,15,18} and found random features do NOT track C(P,3): they need substantially
MORE (P=18 at M≈3·C(18,3) reached only 0.73) because a tanh feature mixes ALL monomial orders, so the
readout must disentangle degree-3 from everything else. So the two routes are NOT equal — **order-3
OMP (exact, C(P,3) enumeration) is the CHEAPER route; random features are strictly worse** for pure
high-order parity. The robust part of the JEP-438 finding stands (greedy order≤2 gets nothing; some
O(C(P,k)) search is required), but "feature-cost == search-cost" is retracted. Honesty over
consistency — see docs/amendments/jep439_cost_equivalence.md.

# JEP-457 — Measure the high-order cost: node perturbation vs interaction order

## Motivation
The frontier statement repeatedly asserts that high-order discovery is costly for a local rule, but
JEP-456 showed node perturbation is efficient at order-3 — so the "high-order cost" is still an
UNMEASURED claim. JEP-457 measures it directly: hold compute fixed and sweep the interaction order k
of the parity rule (y = product of the first k features). If accuracy degrades with k, the high-order
cost is real and quantified; if it stays high, the concern is unfounded at this scale (another honest
correction). Established method (node perturbation), named; this is a measurement, not new science.
No transformer, no backprop.

## Method (`tools/run_jep457_order_scaling.py`)
Fully-local node perturbation (as JEP-445/456), P=18, M=64, N=2500/1000, EPOCHS=5000, seeds 0 & 7.
Sweep k ∈ {2, 3, 4, 5}: `y = x0·x1·…·x{k-1}` (balanced parity). Report held-out accuracy per k and
whether the true k-tuple is recovered (permutation importance).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J457a (high-order cost manifests):** accuracy at k=5 ≤ accuracy at k=2 − 0.15, both seeds (the
  local rule degrades with order at fixed compute).
- **J457b (low order solid):** accuracy at k=2 and k=3 ≥ 0.90, both seeds.
- **J457c (monotone-ish):** accuracy is non-increasing from k=2 to k=5 (report the curve).

Honest expectation: degrades with k (each extra order multiplies the search/variance burden). PASS =
the high-order cost is real and quantified. NULL if accuracy stays ≥0.90 through k=5 (the cost is not
visible at this scale — correct the frontier statement) OR if even k=2 fails (instrument problem).
Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): NULL — and it REFUTES the "high-order is costly" narrative

| seed | k=2 | k=3 | k=4 | k=5 | exact tuple found? |
|------|-----|-----|-----|-----|--------------------|
| 0 | 1.00 | 1.00 | 1.00 | 1.00 | every k ✓ |
| 7 | 1.00 | 1.00 | 1.00 | 1.00 | every k ✓ |

J457a ✗ (no degradation — k=5 = k=2 = 1.00), J457b ✓, J457c ✓ → **NULL.**

**The high-order cost does NOT materialize for a learned local rule (major honest correction).** Node
perturbation solves parity from order-2 to order-5 at fixed modest compute (M=64, 5000 epochs, P=18),
and recovers the EXACT k-tuple every time. So the claim I leaned on across JEP-438→445 — "high-order
discovery is the hard, costly part" — is **wrong at this scale for LEARNED rules**. The combinatorial
C(P,k) cost is specific to the NON-learning routes:
- enumeration (OMP) must list C(P,k) terms (JEP-438), and
- random features must span the degree-k space, needing ≳C(P,k) units (JEP-439).
A **learned** rule — even a zeroth-order, fully-local one — does NOT enumerate; it directly optimizes,
and the interaction order does not make the landscape proportionally harder here. So local LEARNING
escapes the combinatorial wall across orders, not just order-3.

**Reframed open problem (corrected, stronger-positive).** It is no longer "can a local rule do
targeted high-order discovery efficiently" — it demonstrably can, up to k=5 at this scale, cheaply.
The genuinely open questions are narrower: does it hold at MUCH higher order / much larger P (where
the landscape may finally bite), with what SAMPLE efficiency, and on TEMPORAL high-order tasks (where
eligibility traces / e-prop would matter)? My earlier framing overstated the difficulty; this is the
self-correcting record. Established methods, named; the finding is a measurement + correction, not new
science. No transformer.

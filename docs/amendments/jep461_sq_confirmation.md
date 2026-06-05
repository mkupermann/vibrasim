# JEP-461 — Confirm the wall is SQ-hardness: a non-SQ algorithm cracks parity trivially

## Motivation
JEP-459/460 showed the order-8 wall is not compute and not width — a learnability limit, attributed to
the statistical-query (SQ) hardness of parity (Kearns 1998). That attribution makes a SHARP, falsifiable
prediction: the wall is a property of the ALGORITHM CLASS (local/correlational/SQ), NOT of the problem.
Parity is trivially learnable by a NON-SQ algorithm — Gaussian elimination over GF(2) recovers the
parity set from O(P) samples, for ANY order k. If GF(2) elimination cracks order-8/10/12 with ~40
samples while node perturbation failed with thousands, the SQ attribution is decisively confirmed and
the "wall" is precisely located: it is the local/SQ method's barrier, not the problem's.

## Method (`tools/run_jep461_sq_confirmation.py`)
Map parity to GF(2): x∈{−1,+1} → bit (1 iff x=−1); y=∏x → XOR of the selected bits. Generate N samples,
solve `X_bit · s = y_bit (mod 2)` by Gaussian elimination over GF(2) to recover the indicator s of the
parity set; test on held-out. Orders k ∈ {8, 10, 12}, P=18, N_train=40, seeds 0 & 7. Contrast with
node perturbation (JEP-460: order-8 at chance with N=3000, M up to 512).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J461a (GF(2) cracks order-8 trivially):** GF(2) elimination held-out accuracy = 1.00 with N=40,
  both seeds, and recovers the EXACT parity set {0..7}.
- **J461b (order-independent — the contrast is the algorithm):** GF(2) also = 1.00 on order-10 and
  order-12 with N=40 (O(P) samples regardless of k), both seeds — where local/SQ methods would fail
  even harder.
- **J461c (the decisive contrast):** node perturbation (JEP-460) was at chance on order-8 with N=3000;
  GF(2) solves it with N=40 → the wall is the local/SQ algorithm class, not the problem.

Predicted PASS → the order-8 wall is rigorously confirmed as the SQ-hardness of parity (a property of
local/correlational learning), with parity itself trivially learnable by the right (algebraic) method.
This precisely bounds the energy model: local energy-driven learning has this barrier; algebraic
structure does not. NULL if GF(2) fails (the setup is wrong). Bars locked; no retuning. No transformer,
no new science — a decisive demonstration of a KNOWN result.

## RESULT (2026-06-05): **PASS** — SQ-hardness decisively confirmed

| seed | order-8 | order-10 | order-12 | (N=40) |
|------|---------|----------|----------|--------|
| 0 | 1.00 (exact set ✓) | 1.00 (✓) | 1.00 (✓) | — |
| 7 | 1.00 (exact set ✓) | 1.00 (✓) | 1.00 (✓) | — |

J461a ✓ · J461b ✓ → **PASS, both seeds.**

## Verdict: the wall is the local/SQ algorithm class, NOT the problem — rigorously shown
Gaussian elimination over GF(2) — a NON-SQ (algebraic) algorithm — recovers the EXACT parity set and
solves order-8, 10, and 12 at 1.00 with only **N=40 samples**, order-INDEPENDENTLY. The same parity at
order-8 was at CHANCE for node perturbation with N=3000 and width up to 512 (JEP-459/460). So the
"hard wall" is decisively located: it is the **statistical-query / local-correlational barrier**
(Kearns 1998) — a property of local energy-driven learning, NOT a property of the problem. Parity is
trivially learnable by the right (algebraic) method.

**Final, fully-attributed frontier statement (438→461).** For targeted high-order discovery of a rule
with no low-order signal: (1) non-learning routes (enumeration / random features) wall at order-3;
(2) learned LOCAL rules (node perturbation — the substrate's own kind) discover exactly through
~order-5–6 and hit a HARD wall by order-8 that is (3) NOT compute (459), NOT width (460), but the
**SQ-hardness of parity** (461) — the same barrier that makes algebraic methods (GF(2) elimination)
solve it trivially while local/correlational methods cannot. This precisely bounds Michael's energy
model: local energy-driven learning is fundamentally limited on high-order structure with no
lower-order signal — an ALGORITHM-CLASS limit, escapable only by an algebraic (non-local, non-SQ)
method, not by more compute/width. **No new science** — but the best "unexplained" candidate is now
rigorously resolved to a famous known barrier, and the boundary is exactly characterized. Established
results (Kearns 1998 SQ-hardness; GF(2) parity learning), named. No transformer.

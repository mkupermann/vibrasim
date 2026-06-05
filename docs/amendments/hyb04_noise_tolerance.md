# HYB-04 — Does the algebraic escape survive noise? (the LPN boundary)

## Motivation
HYB-01/03 showed an algebraic (GF(2)) module lets the energy model escape the SQ wall on clean parity.
But real data is NOISY, and noisy parity (Learning Parity with Noise, LPN) is a famously HARD problem —
conjectured intractable even for algebraic methods, the basis of LPN cryptography. GF(2) Gaussian
elimination is an EXACT solver: a single flipped label makes the linear system inconsistent and the
recovered set garbage. So the honest question that bounds the whole constructive architecture: how much
label noise does the algebraic discovery module tolerate, and does a simple robustification (majority
vote over many small subset-solves) extend it — before the LPN barrier bites?

## Method (`tools/run_hyb04_noise_tolerance.py`)
Order-8 parity, P=18, seeds 0 & 7. Flip a fraction ε of labels, ε ∈ {0, 0.02, 0.05, 0.10}. Two discovery
methods, each → did it recover the exact parity set {0..7} + held-out accuracy:
- **exact GF(2):** single Gaussian elimination on N=40 noisy samples.
- **robust GF(2):** solve on 200 random subsets of P+2 samples each, majority-vote each bit of s (some
  subsets are noise-free, so the vote can recover the true set at moderate ε).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **HYB04a (clean baseline):** at ε=0, both methods recover the exact set, accuracy = 1.00, both seeds.
- **HYB04b (exact GF(2) is noise-fragile):** exact GF(2) FAILS to recover the set at ε=0.02 (recovered
  set ≠ {0..7}), both seeds — a single error breaks exact elimination.
- **HYB04c (robust voting extends tolerance but hits the LPN wall):** robust GF(2) recovers the exact set
  at ε=0.05 (both seeds) AND fails by ε=0.10 (recovered set wrong, both seeds) — bounding where the
  algebraic module works.

PASS = the algebraic module's noise tolerance is characterized: exact solve is brittle, robust voting
extends it to moderate noise, and the LPN barrier ends it — an honest, useful boundary on the
constructive architecture (it works on clean/low-noise structure, not the LPN regime). NULL if the
pattern differs (report it). Bars locked; no retuning. Established results (LPN hardness), named; not new
science. No transformer.

## RESULT (2026-06-05): NULL/partial — robustification beats my pessimistic prediction

| ε | exact GF(2) set_ok (acc) s0/s7 | robust GF(2) set_ok (acc) s0/s7 |
|---|--------------------------------|----------------------------------|
| 0.00 | ✓/✓ (1.0/1.0) | ✓/✓ (1.0/1.0) |
| 0.02 | ✓/✗ (1.0/0.48) | ✓/✓ (1.0/1.0) |
| 0.05 | ✓/✓ (1.0/1.0) | ✓/✓ (1.0/1.0) |
| 0.10 | ✗/✗ (0.49/0.51) | **✓/✓ (1.0/1.0)** |

HYB04a ✓, **HYB04b ✗ (exact GF(2) is ERRATICALLY fragile — seed-dependent, not a clean ε=0.02
threshold), HYB04c ✗ (robust voting did NOT fail at ε=0.10 — it recovered the exact set at ALL ε tested)
→ NULL/partial.**

**Honest finding — the robust module is MORE noise-tolerant than I predicted (a good surprise).** (1)
exact GF(2)'s fragility is erratic, not a clean threshold — with N=40 and ε=0.02 the sample sometimes
has zero flips (solves) and sometimes ≥1 (garbage), so it's seed-dependent. (2) The robust subset-voting
(200 subsets of P+2, majority-vote each bit) recovers the exact parity set cleanly through ε=0.10 — at
10% noise ~12% of size-20 subsets are still noise-free, the noisy subsets produce *uncorrelated* garbage
that doesn't concentrate on any wrong bit, so the clean minority wins each per-bit vote. So the algebraic
escape module **tolerates moderate label noise well** — better than the LPN-pessimism suggested. The
true LPN barrier lies at HIGHER noise (ε → 0.5), not at the ε ≤ 0.1 I bracketed.

**What this means.** The constructive hybrid architecture is more robust to real-data noise than feared:
the algebraic structure-discovery module, with simple subset-voting, survives moderate label noise — an
honest correction of my own pessimistic prediction (the LPN barrier is real but further out than I
guessed). Recorded NULL against the locked bars; no retuning. Established results (LPN; majority-vote
robustification), named. No transformer.

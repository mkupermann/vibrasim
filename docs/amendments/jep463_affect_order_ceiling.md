# JEP-463 — The real energy model's affect-complexity ceiling over VSA clouds

## Motivation
The SQ frontier (JEP-457→461) was measured on raw bit-vectors (local learning solved parity to ~order
5–6). The actual energy model operates over VSA energy-CLOUDS (bundled feature vectors), which add
superposition noise. JEP-433 showed the reservoir learns ORDER-2 balanced parity affect over real
clouds (0.88–0.91). The open, uncertain question that bounds Michael's energy model on its REAL
representation: how high an affect ORDER can it learn over clouds before it breaks, and is that ceiling
LOWER than the raw-bit boundary (because the cloud adds noise)? This locates the real energy model's
affect-complexity ceiling.

## Method (`tools/run_jep463_affect_order_ceiling.py`)
Concepts = VSA clouds: a normalized sum of [one of {slot_i^0, slot_i^1} for i=1..k binary slots] +
K_fill filler features (D=4096, atom_vector). Balanced parity affect: valence = parity of the k slot
choices (50/50, genuinely order-k). `ValenceReservoirLearner(D, n_features=600)` trained on UNSEEN
clouds (disjoint filler), held-out accuracy vs k ∈ {2,3,4,5}. Seeds 0 & 7.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J463a (low-order works — reproduces JEP-433):** k=2 held-out ≥ 0.85, both seeds.
- **J463b (a ceiling exists over clouds):** held-out at the highest k tested (k=5) ≤ k=2 − 0.15, both
  seeds — affect complexity has a real ceiling over the cloud representation.
- **J463c (report the ceiling):** the smallest k at which held-out first drops below 0.70 (the
  affect-order ceiling for the real energy model over clouds).

Honest expectation: degrades with k; the cloud-noise + SQ-hardness compound so the ceiling is LOWER
than the raw-bit boundary (order ~5) — likely around k=3–4. PASS = the real energy model's affect
ceiling over clouds is located. NULL if it stays high through k=5 (clouds do NOT lower it — the SQ
boundary is representation-independent here; also informative). Bars locked; no retuning. Established
methods (VSA/HRR + reservoir/RLS), named; a measurement, not new science. No transformer.

## RESULT (2026-06-05): **PASS** — the real energy model's affect ceiling over clouds is order ~2

| seed | k=2 | k=3 | k=4 | k=5 |
|------|-----|-----|-----|-----|
| 0 | 0.955 | 0.612 | 0.540 | 0.517 |
| 7 | 0.943 | 0.635 | 0.517 | 0.503 |

J463a ✓ (k=2 ≥ 0.85, reproduces JEP-433), J463b ✓ (k=5 ≪ k=2), ceiling (first < 0.70) = **order 3** both
seeds → **PASS.**

## Verdict: a precise, useful bound on Michael's actual energy model
The deployed energy model (`ValenceReservoirLearner` — fixed random features + online RLS) learns
balanced affect rules up to **order 2** over real VSA energy-clouds (0.95), then breaks SHARPLY at
order 3 (0.61–0.64) and is at chance by order 4. This ceiling is much LOWER than the raw-bit boundary
(node perturbation reached ~order 5, JEP-457) for two compounding reasons: (1) the VSA cloud adds
superposition noise (each feature is only noisily present in the bundle), and (2) the actual model uses
FIXED random features (weaker than node perturbation's learned features — random features need ~C(P,k)
units for order-k).

**The honest, constructive takeaway for the energy model.** Real affect is almost entirely LOW order —
"predators are bad", "clean sounds feel good" are order-1; even a sharp/smooth-style rule is order-1–2 —
so the order-2 ceiling is ADEQUATE for the affect the model actually needs (JEP-446/447 confirm it works
on real perceptual affect). Genuinely high-order affect logic (rare) is beyond it, and THAT is exactly
the regime where the algebraic hybrid module (HYB-01/03) is the escape. So the whole arc closes
coherently: the real energy model's capability and its precise ceiling are now located, the SQ frontier
explains the ceiling, and the hybrid is the characterized path past it. Established methods (VSA/HRR +
reservoir/RLS), named; a measurement that bounds the deployed model, not new science. No transformer.

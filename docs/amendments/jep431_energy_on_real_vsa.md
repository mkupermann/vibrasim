# JEP-431 — Does the energy model learn non-linear affect over REAL VSA energy-clouds?

## Motivation
JEP-430 built the valence-reservoir learner and showed it learns a non-linear (XOR) affect rule
from a scalar energy signal — but on TOY clean bit-vectors. Michael's model is that concepts are
distributed **energy clouds** (the substrate's VSA bundles, `world/substrate_memory.atom_vector` +
superposition), not clean bit strings. The honest open question before claiming any transfer: does
the same learner still recover a non-linear affective rule when the input is a REAL VSA bundle —
features superposed into one high-D cloud, where each feature is only noisily present? If yes, the
energy model works on the substrate's actual representation, not just a toy. Established methods
(VSA/HRR — Plate, Kanerva; reservoir/ELM — Rahimi-Recht, Huang; RLS), named; the only new thing is
running them on THIS substrate's clouds. No transformer.

## Method (`tools/run_jep431_energy_vsa.py`)
- **Concepts as energy clouds.** Each concept = a normalized SUM (bundle) of K=4 feature
  hypervectors drawn from a vocabulary of F=12 semantic features (atom_vector, D=4096) — a real
  distributed VSA cloud, exactly the substrate's `add_fact` superposition.
- **Non-linear affect rule.** valence = −1 (dark) iff `featA ∈ concept XOR featB ∈ concept`, else
  +1 (bright) — a genuinely non-linear (XOR) affect over two designated features, embedded in a
  cloud full of other features (noise to the rule). Base rate 0.5.
- **Learner.** `ValenceReservoirLearner(n_inputs=D, n_features=600)` experiences TRAIN concepts
  online (cloud → valence), then predicts held-out UNSEEN concepts. Compare to (a) a raw linear
  least-squares readout on the cloud, and (b) a SHUFFLED-valence negative control (labels permuted
  → no learnable rule). Seeds 0 and 7; ~600 train / 400 test concepts.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J431a (energy model transfers to real clouds):** valence-reservoir held-out accuracy ≥ 0.80 on
  UNSEEN concept clouds, both seeds.
- **J431b (it is genuinely non-linear):** raw-linear readout ≤ 0.65 on the same clouds (the XOR
  affect is not linearly separable in the bundle), both seeds.
- **J431c (negative control fails):** shuffled-valence reservoir ≤ 0.60 (≈ chance) — the learner is
  fitting real structure, not memorizing, both seeds.

Predicted: J431a PASS, J431b raw fails, J431c control fails — the energy model learns non-linear
affect over the substrate's real VSA clouds. NULL if J431a < 0.80 (the bundle noise destroys the
rule — the toy result does NOT transfer; honest). Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): NULL/partial — and a self-caught design flaw

| seed | reservoir held-out | raw-linear | shuffled control |
|------|--------------------|------------|------------------|
| 0 | 1.000 | 0.900 | 0.475 |
| 7 | 1.000 | 0.863 | 0.545 |

J431a ✓ (reservoir ≥ 0.80), J431c ✓ (control ≈ chance), **J431b ✗ (raw-linear 0.86–0.90, not ≤ 0.65)
→ NULL/partial.**

**The flaw (honest).** The concept space is far too small: with F=12 features choosing K=4 there are
only **C(12,4) = 495 distinct concepts**. A 600-sample train draw covers essentially all of them, so
the 400 "held-out" test concepts are almost all ALSO in train — this is **memorization, not
generalization**. Both the reservoir (1.000) and the raw-linear readout (0.86–0.90) are partly
reading back concepts they have already seen, which is exactly why raw-linear did far better than my
predicted ≤ 0.65. The J431b bar correctly flagged that the experiment did NOT isolate the
reservoir's non-linear advantage over real clouds. The bar stays as locked; recorded as NULL/partial
(no retuning).

**What DOES survive:** J431c (the shuffled-valence control fails at chance) confirms the learners fit
real label structure, not noise — but with train/test overlap that is a weak statement. The clean
question (does the energy model recover NON-LINEAR affect over UNSEEN real VSA clouds?) is
**re-opened**, not answered.

**Corrected follow-up pre-registered as JEP-432:** enlarge the feature vocabulary so the concept
space dwarfs the sample count (F=64, K=6 → C(64,6) ≈ 7.4×10⁷ distinct concepts), guaranteeing
train and test are genuinely disjoint, then re-test transfer (J431a) AND the non-linear advantage
(J431b) on truly unseen clouds.

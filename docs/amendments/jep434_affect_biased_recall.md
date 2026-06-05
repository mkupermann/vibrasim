# JEP-434 — Affect → cognition: does learned valence disambiguate confusable recall?

## Motivation
JEP-433 showed the energy model learns the valence of real VSA clouds and generalizes to unseen,
noisy ones. The next question closes the loop back to cognition: can that learned valence *help the
substrate think* — specifically, disambiguate two concepts that are nearly identical in semantic
(VSA) space but opposite in affect? A "bright" concept and its "dark twin" can share almost all
features (high cosine similarity → confusable under noise) yet carry opposite valence. If a dedicated
learned-valence channel recovers the affect-relevant distinction that raw similarity drowns, then
affect provides a retrieval channel cognition alone lacks. Established methods (VSA/HRR; reservoir/
ELM + RLS), named — NOT new science; the test is whether the integrated energy model is *useful* to
recall. No transformer.

## Method (`tools/run_jep434_affect_recall.py`)
- **Confusable twins.** Each concept-pair shares K=6 semantic features (pool S=100) and differs only
  in ONE polarity feature: bright = shared+`P_bright`, dark = shared+`P_dark`. Twin cosine ≈ 6/7 —
  highly confusable. Valence = +1 if `P_bright` present, −1 if `P_dark`.
- **Energy model** `ValenceReservoirLearner(D=4096, n_features=600)` trained on 300 train pairs
  (clean clouds → valence), then predicts valence of NOISY test probes.
- **Recall task (100 fresh test pairs).** Probe = a bright cloud + Gaussian noise (σ=1.0, fixed
  pre-run). Candidates = {its bright twin, its dark twin}. Target = the bright twin.
  - **semantics-only:** argmax cosine(probe, candidate).
  - **affect-augmented:** predicted_val = sign(energy.feel(probe)); restrict candidates to those whose
    (known) valence == predicted_val, then argmax cosine within (fall back to all if empty).
  - **shuffled-energy control:** same, but the energy model was trained on permuted valence labels
    (predicts garbage) — affect must then NOT help.
- Seeds 0 and 7.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J434a (confusion is real):** semantics-only accuracy ≤ 0.80 (the noisy twins genuinely confuse
  raw similarity), both seeds.
- **J434b (affect helps cognition):** affect-augmented accuracy ≥ semantics-only + 0.15 AND ≥ 0.85,
  both seeds.
- **J434c (it is the LEARNED valence):** shuffled-energy control ≤ semantics-only + 0.05 (a garbage
  valence channel does not help), both seeds.

Predicted PASS: the learned valence channel disambiguates confusable opposites that raw VSA
similarity cannot, and a shuffled valence channel does not — affect feeds back into recall. NULL if
J434a fails (no confusion → uninformative) or J434b fails (valence doesn't help). Bars locked; σ
fixed pre-run; no retuning. No transformer.

## RESULT (2026-06-05): NULL — mis-scaled noise; the instrument had no signal

| seed | semantics-only | affect-augmented | shuffled control |
|------|----------------|------------------|------------------|
| 0 | 0.590 | 0.380 | 0.670 |
| 7 | 0.710 | 0.710 | 0.520 |

J434a ✓ (technically), **J434b ✗, J434c ✗ → NULL.**

**The flaw (honest).** σ=1.0 per-component Gaussian noise destroys the signal entirely. The concept
cloud is **unit-normalized (norm 1)**, but `N(0,1)` noise over D=4096 has norm ≈ √4096 = **64**, so
the probe = normalize(cloud + noise) is ~98% noise. Neither cosine nor the energy model had any
signal — the three columns (0.38–0.71) are just noise variance around chance 0.5, and the
"semantics ≤ 0.80" bar passed for the wrong reason (total obliteration, not subtle confusion). The
experiment never actually probed the hypothesis. My pre-registered σ was a bad instrument choice
(I misjudged the noise scale against a unit-normalized cloud), exactly like G96's frozen-vibration
seal being inert against the real channel.

**Corrected follow-up (JEP-435):** scale the probe noise to a controlled signal-to-noise ratio
(noise norm = r × signal norm, primary r = 0.5 fixed pre-run) so the twins are genuinely confusable
but signal is present, then re-run the identical recall test with the SAME acceptance bars. This is
an instrument fix (the noise scale was broken), not bar-tuning — analogous to the JEP-427 base-rate
0.4→0.5 correction.

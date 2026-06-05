# JEP-446 — Perceive the energies of the environment: affect grounded in perception, not identity

## Motivation
Michael's vision: "we perceive the energies of the environment." The energy model so far predicts the
affect of symbolic concepts (JEP-436). JEP-446 grounds it in PERCEPTION: a stimulus arrives as a
perceptual feature vector (the same kind `world/active_learner.py` uses to ground symbols), and the
energy model predicts its valence ("first impression") directly from those features. The strong claim
to test: affect generalizes from a perceptual feature (e.g. "sharpness") even to an object the system
does NOT recognize — affect is grounded in perception, independent of symbolic identity. Established
methods (prototype perception + reservoir/RLS), named; the value is the substrate-native grounding of
affect in perception. No transformer.

## Method (`tools/run_jep446_perceptual_affect.py`)
Perceptual feature space R^64. Each percept = `symbol_prototype + sharp_dir·(±1) + noise` where the
sign of the sharp/smooth component sets valence (sharp = dark −1, smooth = bright +1), INDEPENDENT of
which symbol it is. Noise scaled to norm = 0.5·signal (the JEP-435 SNR lesson). Train on 5 symbols
{S0..S4}: `active_learner.teach('vision', symbol, percept)` AND `energy.experience(percept, valence)`.
Test on (a) held-out percepts of the trained symbols and (b) percepts of a NOVEL symbol S5 never
taught. Seeds 0 & 7; ~300 train / 150 test.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J446a (perceptual affect generalizes):** energy valence accuracy on all test percepts ≥ 0.85,
  both seeds.
- **J446b (affect ⟂ identity — generalizes to UNRECOGNIZED objects):** on the NOVEL-symbol (S5)
  subset, valence accuracy ≥ 0.80, both seeds, while `active_learner` flags those percepts as
  lower-confidence than trained-symbol percepts (identity uncertain, affect confident).
- **J446c (it is the learned rule):** shuffled-valence control ≤ 0.60, both seeds.

Predicted PASS: the energy model reads affect straight from perceptual features and generalizes to
novel, unrecognized stimuli — "perceiving the energy of the environment" independent of recognizing
the object. NULL if J446b fails (affect does not transfer to novel-symbol percepts → it was riding
identity, not perception). Bars locked; noise fixed pre-run; no retuning. No transformer.

## RESULT (2026-06-05): **PASS** (prediction HIT)

| seed | affect acc (all) | novel-object affect | shuffled control | conf trained / novel |
|------|------------------|---------------------|------------------|----------------------|
| 0 | 1.000 | 1.000 | 0.540 | 0.31 / 0.02 |
| 7 | 1.000 | 1.000 | 0.407 | 0.30 / 0.02 |

J446a ✓ · J446b ✓ · J446c ✓ → **PASS, both seeds.**

## Verdict: "perceive the energies of the environment" — affect grounded in perception, not identity
The energy model reads a percept's valence straight from its perceptual feature vector (1.000) and
generalizes to percepts of an object it was **never taught** (novel-object affect 1.000) — while
`active_learner` reports it does NOT recognize that object (confidence 0.02 vs 0.31 for trained
objects). Identity and affect **dissociate cleanly**: *"I don't know what this is, but it feels
dark."* This is the substrate-native realization of Michael's phrase — the system perceives the
affective "energy" of a stimulus from perception itself, independent of recognizing it, and a
shuffled-valence control fails (it is the learned rule).

**Honest scope.** The perceptual features are synthetic and the affect-bearing direction
(sharp/smooth) is engineered and low-order (linearly readable — JEP-432), so this demonstrates
GROUNDING + identity-dissociation + noise-robustness (noise norm 0.5·signal, the JEP-435 SNR lesson),
not non-linear affect (already shown in JEP-433). Established methods (prototype perception +
reservoir/RLS), named — the contribution is grounding affect in perception, not the methods. No
transformer. A real-sensor version (audio FFT / webcam Gabor features already in the repo) is the
natural extension.

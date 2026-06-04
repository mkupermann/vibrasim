# EQMOD-4 (JEPA / EBM / MPC) — programme summary

Michael's directive: "model predictive control and energy based models in joint based embedding" + "We will
find a way for Human level understanding." This is the honest synthesis of the JEP rungs. Charter:
docs/JEPA_PROGRAMME.md. Substrate-benefit analysis: docs/SUBSTRATE_FOR_JEPA.md.

## What was asked
Pursue JEPA (LeCun: predict in representation space), Energy-Based Models (LeCun/Hinton: inference = argmin
energy), and Model Predictive Control (plan by rolling a model forward to a low-energy goal), and find how the
vibrasim SUBSTRATE is a genuine benefit for this.

## Rungs (all pre-registered; honest verdicts)
| rung | verdict | finding |
|------|---------|---------|
| JEP-1 | PARTIAL | toy JEPA predicts masked rep 0.20 > baselines ~0, but weak standalone. |
| JEP-2 | NULL (informative) | energy-based MPC with a RANDOM encoder fails (0.07 ~ random): random rep -> uninformative energy. The reason JEPA must LEARN representations. |
| JEP-3 | PARTIAL | hand-rolled backprop-free predictor too weak to plan (next-cell acc 0.30). |
| JEP-4 | **PASS** | substrate-native EBM: LOCAL Hebbian learning + RELAXATION inference (no backprop/optimizer); recall 0.905@load0.1N, energy monotone, capacity ~0.14N (Hopfield). |
| JEP-5 | **PASS** | a LOCALLY-LEARNED rep (contrastive temporal-coherence, no backprop) makes energy meaningful (Spearman 0.88) -> energy-based MPC 0.08 -> 0.90. Confirms JEP-2 diagnosis. |
| JEP-6/6b/6c | PARTIAL/NULL | PC tracks backprop on easy regression (0.19/0.19, 0.12/0.12) but grid task confounds (extrapolation; classification=memorization, held-out 0.00; PC lags on hard softmax). |
| JEP-6d | **PASS** | on a well-posed iid task (two-moons), local predictive coding MATCHES backprop (test 0.97 vs 0.98). The substrate-compatible local-learning path for the JEPA predictor is validated. |
| JEP-7 | **PASS** | END-TO-END: contrastive-learned encoder + PC-learned predictor + energy-MPC reaches 0.97 of goals (untrained-predictor ablation 0.05, random 0.25). Nuance: exact prediction only 0.23 — planning needs correct ACTION RANKING, not exact prediction; world model accurate ENOUGH to plan. |

## The honest bottom line
- The SUBSTRATE'S genuine benefit is ARCHITECTURAL: its native primitives are the backprop-free versions of
  what JEPA/EBM/MPC need. Demonstrated, both halves: EBM inference == physical relaxation + local Hebbian
  (JEP-4); learning (representation AND predictor) == local rules that match/enable the digital versions
  (JEP-5 rep-learning -> EBM/MPC works; JEP-6d local predictor == backprop). Bridge = predictive coding /
  active inference.
- NOT shown / honest limits: toy scale; CPU (no speed or accuracy advantage over digital JEPA today - the
  benefit is realized only on physical/neuromorphic hardware); the substrate MEMORY thread closed NEGATIVE
  (G88-96), so "substrate as the long-term world-model STORE" is unsupported - the defensible claim is
  "substrate as the energy ENGINE + local learner". Human-level understanding remains an OPEN research program;
  nothing here closes it.
- Everything used (Hopfield, EBM, predictive coding, slow-feature/contrastive learning, MPC, active inference)
  is an ESTABLISHED method, named as such. No novelty claimed. The contribution is a coherent, pre-registered,
  honestly-bounded demonstration that the substrate has a principled (backprop-free, relaxation-based) job in
  the JEPA/EBM/MPC program - instead of bolting a neural net onto it.
- Open next work (JEP-7+): scale the local-learning rep + PC predictor; couple them (learn rep AND transition
  with local rules jointly); test on the REAL substrate dynamics, contingent on progress on the persistent-
  memory blocker (substrate memory thread).

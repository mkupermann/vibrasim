# JEP-7 — end-to-end substrate-native JEPA+EBM+MPC (fully local learning, no backprop)

## Claim under test
Integrate the three demonstrated pieces into ONE system and test whether a FULLY backprop-free, locally-learned
latent world model supports planning:
- encoder learned by the LOCAL contrastive temporal-coherence rule (JEP-5),
- transition predictor learned by PREDICTIVE CODING on the learned embeddings (JEP-6d) — JEPA's "predict in
  representation space",
- planning by ENERGY-BASED MPC: roll the learned predictor forward in latent space, energy = latent distance
  to the goal embedding, act greedily/receding-horizon (MPC over the EBM).

## Pre-registration (locked BEFORE run)
- Grid world. Encoder via contrastive rule; PC predictor P(E[s],a)->E[s'] trained on observed transitions.
- MPC: at state s pick action minimizing ||P(E[s],a) - E[goal]||; execute in the true env; repeat to budget.
- Metric: fraction of held-out start/goal pairs reached. Ablations: (i) UNTRAINED PC predictor (random
  weights) + same MPC; (ii) random actions.
- Bars: trained-system reached >= 0.7 AND >= untrained-predictor + 0.3 AND >> random. PASS = the complete
  substrate-native (backprop-free, local-learning, relaxation-based) JEPA+EBM+MPC loop plans successfully at
  toy scale. NULL if the locally-learned predictor is too inaccurate to plan with. All methods established
  (contrastive learning, predictive coding, EBM, MPC) - named as such.

## Result — PASS (with an honest nuance about WHY it works)
| planner | goals reached |
|---------|---------------|
| trained system (contrastive encoder + PC predictor + energy-MPC) | 0.97 |
| untrained predictor (ablation) | 0.05 |
| random actions | 0.25 |
| (PC predictor exact next-cell accuracy) | 0.23 |

**VERDICT: PASS — and instructive.** The complete backprop-free loop reaches 0.97 of goals; the untrained-
predictor ablation (0.05) proves the locally-learned predictor is NECESSARY (not the encoder alone). The honest
nuance: exact next-cell prediction is only 0.23, yet planning is 0.97 — because MPC needs only the correct
ACTION RANKING (which action's predicted latent sits closer to the goal embedding), NOT exact next-state
prediction. The contrastive encoder gives a smooth energy gradient toward the goal, and the predictor need only
preserve each action's rough DIRECTION in latent space. So I do NOT claim an accurate world model — I claim a
world model accurate ENOUGH to rank actions, which suffices for greedy energy-based planning. That robustness
(planning tolerates an inaccurate predictor) is a genuine, honest finding. No leak: action selection uses ONLY
the predictor + goal embedding; the true env is used only to execute. All methods established, named as such.

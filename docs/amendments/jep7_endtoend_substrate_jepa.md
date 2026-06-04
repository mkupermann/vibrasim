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

# JEP-78 — the four-pillar capstone: regularized JEPA (VICReg) + latent MPC, with a collapse negative control

## Motivation (Michael's steer: joint-embedding · energy-based · REGULARIZED methods · model-predictive control)
The pillar under-served so far is REGULARIZED methods — the variance/covariance regularization (VICReg; Bardes,
Ponce & LeCun 2022) that prevents JEPA's defining failure mode, representational COLLAPSE (encoder maps everything
to a constant, prediction loss trivially 0, embedding useless). This rung builds all four pillars together:
JEPA (encoder + latent predictor), EBM (prediction error = energy), REGULARIZED (VICReg var+cov), MPC (plan in the
learned latent). Per CLAUDE.md negative-control discipline, the UNREGULARIZED variant MUST collapse for the result
to be defensible.

## Setup
- Latent system: true state s in R^2; action a in [-0.3,0.3]^2; dynamics s' = clip(s+a, -1,1) (2D point mass).
- Observation o in R^32 = tanh(P s) + noise (P random 32x2): a nonlinear high-dim view of the 2D state.
- JEPA: encoder enc: R^32->R^8; predictor pred(enc(o_t), a) -> enc(o_{t+1}). Loss = prediction(invariance) +
  VICReg variance(push per-dim std->1) + covariance(decorrelate). CONTROL: same net, regularizer weights = 0.

## Pre-registration (locked BEFORE run)
- Metrics: (a) embedding per-dim std (collapse if ~0); (b) state-probe R^2 (linear decode true s from z);
  (c) MPC: plan H=10 actions in the LEARNED latent to reach a goal embedding; final true-state distance to goal.
- PASS (all): REGULARIZED -> embedding std >= 0.30 AND state-probe R^2 >= 0.80 AND MPC final-dist <= 0.30 and <
  random-action baseline; AND CONTROL collapses -> std <= 0.05 OR probe R^2 <= 0.30 (negative control fails).
- Honest scope stated up front: encoder trained by gradient descent (torch), not substrate-native plasticity here
  — the substrate-native training of such predictors was shown separately (predictive coding, JEP-19); this rung's
  point is the regularized-JEPA + latent-MPC integration and the collapse control. Established (VICReg, JEPA, MPC),
  named; NO novelty.

## Result — PASS (four pillars together; control collapses)
| variant | emb-std | state-R^2 | MPC-dist | random-baseline |
|---------|---------|-----------|----------|-----------------|
| REGULARIZED (VICReg) | 0.982 | 0.983 | 0.078 | 1.084 |
| CONTROL (no regularizer) | 0.010 | 0.016 | 1.301 | 1.073 |

**VERDICT: PASS.** Regularized JEPA yields a non-collapsed (std 0.98), state-decodable (R^2 0.98) latent that
supports MPC to goals (final dist 0.078 vs 1.08 random). The UNregularized control COLLAPSES (std 0.01, R^2 0.02;
its MPC is worse than random, 1.30 — a collapsed predictor gives no usable gradient). VICReg variance/covariance
regularization is precisely what prevents collapse. All four pillars demonstrated together: joint-embedding +
energy(prediction) + REGULARIZED + MPC. HONEST SCOPE: encoder trained by gradient descent here (substrate-native
predictor training shown separately, JEP-19 predictive coding); toy 2D system. Established (VICReg = Bardes-Ponce-
LeCun 2022; JEPA = LeCun 2022; MPC), named; NO novelty. The discipline (collapse negative control) is the point.

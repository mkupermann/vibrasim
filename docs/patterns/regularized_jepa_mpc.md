# Pattern: the four-pillar world model — regularized JEPA + latent MPC (JEP-78)

LeCun's recipe, assembled and verified end-to-end with a collapse negative control.

## The recipe
1. **Joint-Embedding (JEPA):** encoder enc:obs->z, predictor pred(z_t,a)->z_{t+1}. Predict in LATENT space, not
   pixel space (avoids modelling unpredictable detail).
2. **Energy-Based:** the prediction error ||pred(enc(o_t),a) - enc(o_{t+1})||^2 IS the energy; low energy = a
   compatible (state, action, next-state). Training shapes the energy landscape.
3. **Regularized methods (THE crucial pillar):** latent prediction alone has a trivial zero-energy solution -
   enc -> const (COLLAPSE). VICReg (Bardes-Ponce-LeCun 2022) prevents it with two batch-statistic terms:
   - VARIANCE: push each embedding dim's std toward 1 (relu(1-std)) - stops dims dying.
   - COVARIANCE: drive off-diagonal covariances to 0 - stops dims duplicating.
   These use only batch statistics (no labels, no negatives) - self-supervised and local-ish.
4. **MPC:** plan in the learned latent - sample candidate actions, roll the predictor forward, pick the action
   minimizing distance to the goal embedding. Reaches goals when the latent is faithful.

## The non-negotiable check (negative control)
Train the SAME net with the regularizer OFF. It MUST collapse (embedding std ~0, state-probe R^2 ~0, MPC worse
than random). If it doesn't collapse, your task is too easy to be evidence that the regularizer did anything.
Measured (JEP-78): regularized std 0.98 / R^2 0.98 / MPC 0.08; unregularized 0.01 / 0.02 / 1.30. The gap IS the
regularizer's contribution.

## Honest bounds
Toy 2D system; encoder trained by gradient descent (substrate-native predictor training is separate - predictive
coding, JEP-19, matches backprop at depth). All methods established and named; the transferable output is the
assembled recipe + the discipline of proving collapse in the control.

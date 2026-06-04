# JEP-6 — predictive coding (LOCAL updates, no backprop) trains the JEPA predictor as well as backprop

## Claim under test
JEPA's predictor is normally trained by backprop. Predictive coding (Rao-Ballard; Whittington & Bogacz 2017)
trains the SAME network with LOCAL error-driven updates and relaxation inference — substrate-compatible. If a
PC-trained predictor matches a backprop-trained one on the JEPA next-state prediction task, the substrate's
local-learning path to "predict in representation space" is demonstrated.

## Pre-registration (locked BEFORE run)
- Task: smooth encoder enc(cell) (random Fourier features -> neighbours close). From (enc(cell), action-onehot)
  predict enc(next cell). Held-out cells for test. Metric: nearest-cell hits@1 + MSE.
- Three predictors, SAME 2-layer architecture (Din->H->D, tanh hidden):
  (1) BACKPROP MLP (global gradient); (2) PREDICTIVE CODING (local error nodes + hidden relaxation, no
  backprop); (3) RANDOM-init (untrained control).
- Bars: PC hits@1 >= backprop - 0.10 (matches within tolerance) AND both >> random AND PC >= 0.7 absolute.
  PASS = local predictive-coding learning trains the JEPA predictor comparably to backprop (substrate path
  validated). NULL if PC fails to match backprop. Predictive coding is an established method - named as such.

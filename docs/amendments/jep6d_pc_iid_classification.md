# JEP-6d — fair PC-vs-backprop test: iid nonlinear classification (two-moons)

## Motivation
The grid-transition task (JEP-6/6b/6c) confounded PC-vs-backprop with pathological generalization. The canonical
Whittington-Bogacz demonstration uses iid train/test on a nonlinear classification. JEP-6d does that: two-moons
binary classification, train and test drawn from the SAME distribution, so generalization is well-posed.

## Pre-registration (locked BEFORE run)
- Two-moons (noisy), 2D -> binary. Train N=600, test N=400 iid from same generator. 2-layer net (2->H->2).
- Inference iterations for PC set to 50 (method requirement, decided before run, on a new task - NOT bar tuning).
- Predictors: backprop (softmax+CE), predictive coding (local), random.
- Bars: backprop >= 0.90 (task learnable + generalizes) AND PC >= backprop - 0.07 AND both >> 0.5. PASS = local
  PC learning matches backprop on a well-posed generalizing task -> the substrate local-learning path is valid.
  NULL if PC fails to match. Predictive coding (Rao-Ballard; Whittington-Bogacz 2017) = established, named so.

# JEP-6b — clean PC-vs-backprop comparison on a learnable (interpolation) split

## Motivation
JEP-6 held out whole cells (extrapolation) and BOTH backprop and PC scored 0.19 — they matched, but the task
tested generalization neither method does. JEP-6b isolates the real claim ("local predictive-coding learning
matches backprop") on an interpolation split both can learn.

## Pre-registration (locked BEFORE run)
- Same smooth encoder + JEPA next-state task. Split: hold out 20% of (cell,action) PAIRS at random; every cell
  appears in training with its other actions. Tests interpolation.
- Same 2-layer arch; three predictors: backprop, predictive coding (local), random.
- Bars: backprop and PC BOTH >= 0.7 held-out hits@1 AND |PC - backprop| <= 0.10 AND both >> random. PASS =
  local PC learning matches backprop on the learnable task (substrate path validated). NULL otherwise.
  Predictive coding = established (Rao-Ballard; Whittington-Bogacz) - named as such.

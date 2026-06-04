# JEP-6c — PC vs backprop with a classification readout (where backprop demonstrably succeeds)

## Motivation
JEP-6/6b: PC tracked backprop both times (0.19/0.19, 0.12/0.12) but the embedding-regression+nearest readout
kept BOTH low, masking whether PC truly matches a SUCCESSFUL backprop run. JEP-6c uses a 64-way softmax head
(cross-entropy) where backprop reaches high accuracy, to cleanly test PC == backprop at a level that matters.

## Pre-registration (locked BEFORE run)
- Task: from (enc(cell), action-onehot) classify next-cell (64-way softmax). Interpolation split (hold out 20%
  of (cell,action) pairs). 2-layer net.
- Predictors: backprop (softmax+CE), predictive coding (local, softmax output error), random.
- Bars: backprop >= 0.7 (confirms the task is learnable) AND PC >= 0.7 AND |PC-backprop| <= 0.10 AND both >>
  random. PASS = local PC learning matches a SUCCESSFUL backprop predictor. NULL if backprop can't learn it
  (task/readout still wrong) or PC fails to match. Predictive coding = established, named as such.

## Result — NULL (classification framing = memorization; PC lags backprop on harder optimization)
| metric | backprop | predictive coding | random |
|--------|----------|-------------------|--------|
| TRAIN acc | 0.83 | 0.47 | — |
| held-out acc | 0.00 | 0.00 | 0.02 |

**VERDICT: NULL (informative).** Two findings: (1) held-out 0.00 for BOTH — a 64-way classification of next-cell
is pure MEMORIZATION; held-out (cell,action) pairs map to classes the net never associated with that input, so
no generalization (the embedding-regression of JEP-6b at least carried spatial structure -> 0.12). (2) On TRAIN
fit, backprop (0.83) BEATS PC (0.47): with limited inference iterations PC only APPROXIMATES backprop and lags
on harder softmax optimization (consistent with the literature - PC approximates backprop under conditions, not
identically). The grid-transition task confounds the PC-vs-backprop question with a pathological generalization
structure. Fair test = iid nonlinear classification (JEP-6d). Bars locked, not retuned.

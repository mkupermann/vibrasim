# G144 — RBM features on REAL digits: do they beat raw-pixel linear?

## Result (sklearn handwritten digits, 8x8 binarized, 70/30 split)
| model | held-out accuracy |
|-------|-------------------|
| raw-pixel linear (logistic regression) | 0.933 |
| RBM(128) unsupervised features + linear | 0.946 (delta +0.013) |

**VERDICT: NULL (tie)** — the RBM features are within noise of raw-pixel linear; no representation-learning
benefit on this dataset.

## Finding — on real data the pattern holds: standard ML does the work, the energy-based part is decorative
The stack DOES classify real digits well (94.6%), but the RBM (the physical/energy-based component) adds
essentially nothing over a plain linear classifier — the linear readout already reaches 93.3% on this easy
dataset. This echoes the recurring theme of the whole investigation: across the physical substrate (G133),
the cognition reservoir (a numpy random matrix), and now RBM pretraining, the GENERIC ML component (linear
classifier / random features) carries the result, and the physics/energy-based addition is decorative.
(Consistent with the established record: RBM pretraining gives only modest gains and was superseded.)

## Net
The buildable no-LLM stack's useful capabilities are real but come from STANDARD ML (linear classifiers,
random features, the established optimize/recall/learn/generate primitives) — not from anything the
physical substrate uniquely contributes. The honest map is unchanged and now also holds on real data.

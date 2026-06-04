# EQMOD-4 — JEPA / Energy-Based Models / MPC toward understanding (charter)

User directive (2026-06): pursue Joint-Embedding Predictive Architectures (JEPA), Energy-Based Models (EBM),
and Model Predictive Control (MPC) toward HUMAN-LEVEL UNDERSTANDING. Autonomous, pre-registered, honest.

## Honest framing (named as established, per the charter)
- **JEPA** (LeCun 2022; I-JEPA, V-JEPA): learn by PREDICTING IN REPRESENTATION SPACE — predict the embedding
  of a masked/future part from context, NOT the raw tokens/pixels. Avoids wasting capacity on unpredictable
  detail; learns abstract, predictive representations self-supervised.
- **EBM** (LeCun/Hinton): a scalar ENERGY E(x,y); low energy = compatible. Train to push energy down on real
  (x,y), up elsewhere; inference = find y minimizing E (this IS planning / MPC).
- **MPC**: plan by rolling the learned world model forward and optimizing actions to reach a goal (low energy).
These are ESTABLISHED methods — the contribution here is honest PC-scale demonstration + a precise map of what
the principles do and don't deliver, NOT new algorithms.

## Honest stance on "human-level understanding"
This is a research PROGRAM, not a solved path. LeCun's own position: world-model JEPA is a hypothesis, years
from human-level. I will demonstrate the PRINCIPLES (representation-space prediction, energy-based
compatibility, model-predictive planning) and measure what they genuinely achieve at PC scale — and say
plainly where they fall short of "understanding". No overclaiming; this is the same discipline as EQMOD-3
(which honestly bottomed out at "lookup + computation, not inference").

## Rungs (JEP-numbered, pre-registered)
- JEP-1: toy JEPA — predict masked element EMBEDDING from context in a structured world; does it learn the
  world's structure (generalize to held-out)? vs baselines (mean, raw-autoencoder).
- JEP-2: EBM — energy over (context, candidate); low energy for the true continuation; inference by argmin.
- JEP-3: MPC — plan a path to a goal by rolling the learned model + minimizing energy.
- (chain as findings warrant; PASS/NULL/PARTIAL honest, controls collapse).

The prior EQMOD-3 toolkit (grounded retrieval + symbolic) is the deployable result; EQMOD-4 explores whether
the world-model paradigm reaches further toward understanding. Honest verdicts throughout.

# JEP-81 — putting the SUBSTRATE back in the chain: the EBM + predictor pillars on world.energy.EnergyNet

## Why (Michael's question: "Where is the substrate in the chain?")
Honest audit: of 108 tools/run_jep*.py experiments, ZERO import the substrate; 107 are pure numpy/torch. The
EQMOD-4 chain demonstrated JEPA/EBM/MPC capabilities in ABSTRACTED form, motivated by the substrate's primitives
(relaxation=EBM inference, local plasticity=learning) but never EXECUTED on the project's own engine. This rung
fixes that: it runs the EBM + world-model-predictor pillars on world.energy.EnergyNet — the project's engineered,
backprop-free Hopfield energy engine (EQMOD-2): E(s) = -1/2 s^T (W∘M) s - b^T s, relaxation = inference,
contrastive-Hebbian = local learning, asymmetric T = the predictive (transition) world-model.

## Pre-registration (locked BEFORE run)
On world.energy.EnergyNet (N=80, 2 modules), patterns from make_patterns:
- (a) EBM INFERENCE: during relax(), energy is monotone non-increasing (relaxation = energy-minimizing inference).
- (b) LOCAL LEARNING (no backprop): contrastive-Hebbian train_epoch raises masked-unit completion accuracy to
  >= 0.90 at load 5 patterns, vs an UNTRAINED control ~0.50 (chance). Learning works without backprop.
- (c) PREDICTOR/world-model: train_sequence (asymmetric T) then recall_sequence reproduces a stored length-5
  sequence at per-step accuracy >= 0.90, vs untrained control ~chance.
- PASS = all three on the ACTUAL substrate engine. This places the substrate concretely in the chain as the EBM
  inference engine + local learner + predictive world-model. HONEST scope: EnergyNet is the ENGINEERED energy
  layer (world/); the spontaneous-matter physics layer's long-term MEMORY thread closed NEGATIVE separately
  (G88-96) — so the defensible claim is "substrate as energy engine + local learner + short predictor", not
  "spontaneous substrate as long-term store". Established (Hopfield EBM, contrastive Hebbian), named; no novelty.

## Result — PASS (the substrate, executed)
- (a) EBM inference: energy over 30 relax steps -61.1 -> -87.8, non-increasing fraction **1.00**.
- (b) Local Hebbian learning (no backprop): completion accuracy untrained 0.00 -> trained **0.986**.
- (c) Predictor/world-model: sequence recall per-step accuracy trained **1.00** vs untrained 0.00.

**VERDICT: PASS.** Run on world.energy.EnergyNet — the FIRST of 109 JEP experiments to import the substrate. The
substrate engine performs, on its own dynamics, all three things the EQMOD-4 chain had only demonstrated in
numpy/torch abstraction: energy-minimizing inference by relaxation, backprop-free local (contrastive-Hebbian)
learning, and predictive sequence modelling via the asymmetric transition matrix. The substrate IS the backprop-
free EBM + predictor the chain abstracted. HONEST SCOPE: this is the ENGINEERED energy layer (EQMOD-2, world/);
the spontaneous-matter physics layer's long-term MEMORY thread closed NEGATIVE separately (G88-96), so the
defensible claim is "substrate as energy engine + local learner + short predictor", not "spontaneous substrate as
long-term store". Established (Hopfield EBM, contrastive Hebbian / equilibrium-prop), named; no novelty. This rung
exists because Michael asked the right question — "where is the substrate in the chain?" — and the honest audit
(0/108) demanded the reconnection.

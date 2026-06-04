# JEP-2 — Integrated JEPA world model + Energy-Based Model + MPC planning (the user's full request)

## Motivation
The user's directive: MODEL PREDICTIVE CONTROL + ENERGY-BASED MODELS in JOINT-EMBEDDING. JEP-2 builds LeCun's
full architecture: (1) a JEPA WORLD MODEL learns to predict the next-state EMBEDDING from (state-emb, action)
self-supervised; (2) an ENERGY E(state, goal) = distance in representation space (EBM); (3) MPC planning rolls
the learned world model forward over action sequences and picks the sequence minimizing energy-to-goal, then
acts. Test: does the agent REACH goals using its learned latent world model + energy-based planning?

## Pre-registration (locked BEFORE run)
- Grid world (e.g. 10x10), 4 actions. States embedded by a fixed encoder (representation). JEPA predictor
  trained self-supervised on random-walk transitions (predict next-state embedding from state-emb + action).
- Planning: from a start, MPC does receding-horizon search (rollouts via the JEPA model) minimizing energy
  (embedding distance) to the GOAL's embedding; execute first action; repeat until goal or step budget.
- Test on HELD-OUT start/goal pairs the planner never trained on. Metric: fraction of goals REACHED within a
  step budget. Baselines: random actions; greedy on TRUE coords (oracle upper bound).
- Bars: MPC-with-learned-JEPA reaches >= 0.7 of goals AND >> random. PASS = JEPA world model + EBM + MPC plans
  successfully (the integrated paradigm works at PC scale). NULL if the learned model is too inaccurate to plan.

## Result — NULL (informative): random representation breaks energy-based planning
| planner | goals reached |
|---------|---------------|
| MPC w/ learned JEPA model + embedding-distance energy | 0.07 |
| random actions | 0.05 |

**VERDICT: NULL — but it reveals the KEY JEPA insight.** With a FIXED RANDOM encoder, embedding-distance does
NOT correlate with grid-distance, so the energy E(state,goal)=embedding-distance is UNINFORMATIVE — minimizing
it doesn't guide toward the goal, and MPC ~ random (0.07 vs 0.05). This is exactly why JEPA must LEARN
representations: the whole point is a learned representation where prediction AND distance/energy are
meaningful. A random representation breaks both the world model's usefulness and the energy landscape. Fix in
JEP-3: (a) make energy informative — either learn a metric representation (distance=task-distance) or use the
model as a SIMULATOR (roll forward, check if the predicted state decodes to the goal cell); (b) ensure the
JEPA model's next-state prediction is accurate enough to plan with.

## JEP-3 Result — PARTIAL (root cause: backprop-free manual predictor + random encoder both weak)
| metric | value |
|--------|-------|
| JEPA model next-cell accuracy | 0.30 |
| simulation-MPC goals reached | 0.17 |

**VERDICT: PARTIAL.** Even the diagnostic shows the learned model predicts the correct next-cell only 0.30 of
the time — too inaccurate to plan with. Two compounding causes: (1) the fixed RANDOM encoder gives no smooth
structure for the predictor to exploit; (2) a hand-rolled regression-to-embedding predictor is weak. The
digital lesson is clear (use a learned encoder + real optimizer). But this also surfaced the deeper question
Michael asked: **what is the SUBSTRATE'S genuine benefit here?** Answered in docs/SUBSTRATE_FOR_JEPA.md and
tested in JEP-4 (substrate-native energy-based inference: local Hebbian learning + relaxation = EBM argmin).

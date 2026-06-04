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

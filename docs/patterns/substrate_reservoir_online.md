# Pattern — Substrate-as-Reservoir: emergent generalization + online learning

**Surfaced by:** BET-124 (PASS). **Status:** reusable substrate primitive.

## Problem it solves
Memorization mechanisms (n-gram, least-squares transition tables, Hebbian
outer-products) cannot generalize to inputs they never saw (BET-117). VSA gives
composition but is HAND-DESIGNED. We need generalization that EMERGES from the
substrate itself, and that updates ONLINE from every interaction — no transformer,
no backprop, no pretraining.

## The mechanism
The substrate's random, sparse, modular connectivity + nonlinear activation IS a
random nonlinear feature map (a reservoir):

    phi(x) = tanh(R x + b)        R = random projection (the substrate's own wiring)

On top of phi, a single LINEAR readout generalizes (random features tile the input
space) and is learnable ONLINE in closed form via Recursive Least Squares:

    phi = features(x)
    P_phi = P @ phi
    g     = P_phi / (1 + phi @ P_phi)
    Wout += outer(y - Wout @ phi, g)      # one example, O(D^2), no replay
    P    -= outer(g, P_phi)

`P` is the running inverse-covariance — RLS is exact incremental ridge regression,
so each new example refines the SAME solution batch least-squares would reach, with
no catastrophic forgetting of earlier examples. That is the "learns from every
conversation turn" property, mathematically.

## Why it's substrate-native, not a bolt-on
- R is not trained — it is the substrate's fixed random projection. No learned
  hidden layer = no transformer, no backprop through depth.
- The nonlinearity (tanh) is the substrate's neuron activation, already in
  world/energy.py.
- Only a linear readout is fit, and it is fit in CLOSED FORM, online.

## When to reach for it
Any time the substrate must map inputs -> outputs and generalize beyond stored
examples while updating live: classification, regression, next-token readout over
composed codes, value heads. Pair with world/vsa.py to feed it STRUCTURED
(role-filler-bound) inputs when systematic/symbolic generalization is required —
the reservoir then generalizes over compositions, not just interpolations.

## Honest limit
Random-feature reservoirs give INTERPOLATIVE generalization. Systematic symbolic
generalization (novel STRUCTURE, not novel points) needs structured inputs
(VSA-composed) or a substrate whose features are themselves compositional — the
open BET-125+ line.

## Code
world/reservoir.py :: SubstrateReservoir (features / predict / learn_online)

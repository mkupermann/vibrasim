# JEP-445 — The fully-local rung: does node perturbation (3-factor Hebbian) escape the order-k wall?

## Motivation
The locality ladder so far: backprop escapes order-3 parity (JEP-442), and feedback alignment — no
weight transport — also escapes (JEP-444). Both still use a backprop-style derivative through the
hidden layer. The final rung toward a substrate-plausible rule removes that too: **node perturbation**
(Williams REINFORCE / Fiete-Seung), a 3-factor Hebbian rule where the hidden weights update from
`pre-synaptic activity × hidden-node perturbation × a single GLOBAL scalar error/reward modulator` —
no derivative, no weight transport, only local signals + one neuromodulator. JEP-445 asks whether
this fully-local rule discovers the order-3 interaction. If yes, the substrate's own local primitives
could in principle do targeted high-order discovery; if no, the gap to local is real (perturbation is
too high-variance). Established method, named; reference probe, substrate path unchanged. No
transformer.

## Method (`tools/run_jep445_node_perturbation.py`)
Order-3 parity `y = x0·x1·x2`, P=18, M=64, N=2500/1000, seeds 0 & 7.
- hidden `h = tanh(X·W1+b1)`, output `o = h·w2+b2`.
- **w2 (output):** local delta rule `dw2 = mean((o−y)·h)`.
- **W1 (hidden):** node perturbation — perturb each sample's hidden preactivation by `σ·ξ` (ξ∼N(0,1)),
  `ΔL = (o_pert−y)² − (o−y)²` (the global scalar), update
  `dW1 = −lr · mean_n[ x_n ⊗ (ξ_n · ΔL_n) ] / σ²`. No backprop, no weight transport.
- σ=0.1, lr=0.05, grad-norm clipping, EPOCHS=20000. Compare to matched random features.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J445a (fully-local rule escapes the wall):** node-perturbation held-out ≥ 0.90, both seeds.
- **J445b (it finds the interaction):** top-3 permutation-importance = {0,1,2}, both seeds.
- **J445c (gap is learning):** ≥ matched-random + 0.20, both seeds.

Honest expectation: genuinely uncertain and the hardest call yet — node perturbation is an unbiased
but HIGH-VARIANCE gradient estimator, so it may learn slowly and stall on parity (no low-order signal
to bootstrap). PASS = the substrate-plausible local rule discovers high-order structure (the ladder
completes). NULL = perturbation too high-variance at this scale → the gap to a usable local rule is
real, and faster local rules (e-prop with eligibility traces) are the open direction. Bars locked; no
retuning. No transformer.

## RESULT (2026-06-05): **PASS** (prediction HIT) — the locality ladder completes

| seed | node-perturbation (M=64) | matched random | top-3 features |
|------|--------------------------|----------------|----------------|
| 0 | 1.000 | 0.534 | [0, 1, 2] ✓ |
| 7 | 1.000 | 0.547 | [0, 1, 2] ✓ |

J445a ✓ · J445b ✓ · J445c ✓ → **PASS, both seeds.**

## Verdict: a fully-local rule discovers the order-3 interaction
Node perturbation — a 3-factor Hebbian rule using only `pre-synaptic activity × hidden-node
perturbation × one global scalar error/reward modulator` (no backprop, no weight transport, no
derivative through the hidden layer) — cracks order-3 parity perfectly with M=64 and concentrates on
exactly the true triple {0,1,2}. The locality ladder now completes:

| route | order-3 parity | locality |
|-------|----------------|----------|
| flat / deep random features | ≈ chance (JEP-439/441) | — (no learning) |
| order-3 OMP | exact, but O(C(P,3)) enumeration (JEP-438) | global search |
| backprop | 1.000, M=64 (JEP-442) | non-local (weight transport) |
| feedback alignment | 1.000, M=64 (JEP-444) | no weight transport |
| **node perturbation (3-factor)** | **1.000, M=64** | **fully local + 1 global modulator** |

So **targeted high-order discovery is achievable with a fully-local rule** — exactly the kind the
substrate already has primitives for (STDP-style local plasticity + a global neuromodulatory signal).

**Honest caveat (the real remaining open problem).** Node perturbation is an unbiased but
HIGH-VARIANCE gradient estimator: it works here at small scale (M=64, P=18, 20 000 epochs) but its
variance grows with network size, so it does NOT scale efficiently. This is a **proof of principle**
that local rules CAN do targeted high-order discovery — not an efficient solution. The remaining open
problem is therefore narrower and sharper than "is it possible locally" (it is): it is **EFFICIENT**
local targeted discovery at scale — which is exactly what eligibility-trace methods (e-prop) add to
the 3-factor rule. Established methods (node perturbation — Williams REINFORCE / Fiete-Seung), named;
reference probe, substrate path unchanged. No transformer.

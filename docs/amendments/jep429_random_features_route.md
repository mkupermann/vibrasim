# JEP-429 — Is there a tractable route past the discovery wall? Random nonlinear features

## Motivation
JEP-428 showed exhaustive conjunction search is combinatorial. The honest follow-up: is there a TRACTABLE (non-brute-
force) route that lets the energy/valence signal learn the non-linear rule? Test the project's own established trick —
RANDOM nonlinear features (reservoir / Extreme Learning Machine; Rahimi-Recht 2007, Huang 2006), already used in the
EQMOD-2 thread. Random nonlinear projection can make a low-order non-linear rule LINEARLY separable, so a linear
valence readout recovers it WITHOUT enumerating conjunctions. Honest expectation: it cracks XOR tractably, but the
number of random features needed grows with interaction order — pushing the wall, not removing it. Established method,
named; no claim of novelty. No transformer.

## Method
XOR stream (good iff prop0 XOR prop1, base 0.5, noise). (a) linear least-squares readout on the RAW property bits →
should be ~chance for XOR; (b) random features φ(x)=tanh(Rx+b), R random M×P, then linear readout on φ → should recover
XOR. Report accuracy vs M, and the M needed for a 3-way (XOR-like) rule.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J429a (raw linear = chance):** linear readout on raw properties ≤ 0.60 accuracy on the XOR rule, both seeds (0, 7).
- **J429b (random features crack it tractably):** random-feature (M=200) + linear readout ≥ 0.85 accuracy on XOR — a
  tractable, non-enumerative route, both seeds.
- **J429c (residual cost):** a higher-order (3-way) rule needs materially MORE random features to reach the same
  accuracy — the wall is pushed, not removed (report the M-curve).

Predicted: J429a (raw fails), J429b (random features succeed) — a partial, established route; J429c shows the residual
scaling. Bars fixed; no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J429a (raw linear = chance): PASS** — raw linear readout on properties = 0.50-0.52 on XOR (chance). Both seeds.
- **J429b (random features crack it): PASS** — random nonlinear features (M=200) + linear valence readout = **0.89-0.90**
  on XOR — tractable, no enumeration. Both seeds.
- **J429c (residual cost): confirmed** — M-curve: order-2 XOR reaches ~0.85 at M≈100-300; order-3 XOR needs more
  (M=100→0.70, M=300→0.85). Higher order needs more features (and beyond M≈n it overfits without regularization: M=1000
  drops to ~0.81). The wall is PUSHED, not removed.

## Verdict: **PASS — a tractable partial route exists (random features), but the open problem remains**
Completing the 426→429 frontier map with a constructive result: a scalar energy/valence signal learns LINEAR rules (426),
is at chance on NON-LINEAR XOR (427), brute-force conjunction discovery is combinatorial (428) — BUT random nonlinear
features (the project's own reservoir/ELM trick; Rahimi-Recht 2007) make low-order non-linearity LINEARLY separable, so
the valence readout cracks XOR TRACTABLY without enumeration (429). This is a genuine, established, tractable route that
pushes the wall significantly. Its residual cost: the number of random features grows with interaction order (and
overfits past M≈n), so it does not by itself SOLVE high-order unsupervised feature discovery — that remains the open
problem (a PRINCIPLED, sample-efficient discovery, vs random-then-readout). Honest, constructive: there is a partial
route (named, established — NOT new science), and the precise residual is quantified. Ties to the EQMOD-2 reservoir
thread. No transformer.

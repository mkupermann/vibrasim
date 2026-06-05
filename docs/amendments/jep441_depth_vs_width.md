# JEP-441 — Depth vs width for high-order discovery: do deep random features beat flat ones?

## Motivation
JEP-438/439 left the frontier: for an order-k rule with no low-order signal, flat random features
need ≳ C(P,k) units and degrade with N (P=18 order-3 maxed at 0.73, M=2400). The natural
ethos-respecting question (no backprop, no enumeration): does **composition** help? A 2-layer random
feature network (deep ELM / deep reservoir — established) builds features-of-features, which can
represent higher-order interactions more compactly than one flat layer. JEP-441 tests whether depth
beats width at a MATCHED unit budget on the exact case flat features struggle with. Established
methods (deep random features), named; the result is a frontier data point, not a new method. No
transformer, no backprop.

## Method (`tools/run_jep441_depth_vs_width.py`)
Order-3 parity `y = x0·x1·x2`, bipolar, P=18, N=2500 train / 1000 test, seeds 0 & 7. At each total
unit budget T ∈ {1200, 2400}:
- **flat (1-layer):** M=T random tanh features + ridge readout.
- **deep (2-layer):** h1 = tanh(X·R1+b1) with m1=T/2; h2 = tanh(h1·R2+b2) with m2=T/2; ridge readout
  on h2. Total units = T (matched).
Report held-out accuracy for each. Order-3 OMP (exact, from JEP-438) is the reference.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J441a (depth helps at matched budget):** deep accuracy ≥ flat accuracy + 0.10 at T=2400, both seeds.
- **J441b (depth reaches a usable level flat could not):** deep accuracy ≥ 0.85 at T ≤ 2400, both seeds.
- **J441c (flat baseline confirms the gap):** flat accuracy ≤ 0.80 at T=2400, both seeds (reproduces
  JEP-439's flat shortfall at P=18).

Honest expectation: genuinely uncertain. Depth MAY help (composition compounds order) or MAY NOT
(a random layer-2 of random layer-1 does not specifically construct x0x1x2). PASS = J441a–c → depth
is a cheaper-than-flat, backprop-free partial route to high-order discovery. NULL if J441a fails
(depth ≈ flat — composition of random layers does not target the interaction) — equally informative:
it would say random composition is not the escape, and the open problem stands. Bars locked; no
retuning. No transformer, no backprop.

## RESULT (2026-06-05): NULL — random depth does NOT beat width

| seed | T=1200 flat / deep | T=2400 flat / deep |
|------|--------------------|--------------------|
| 0 | 0.680 / 0.584 | 0.673 / 0.657 |
| 7 | 0.724 / 0.609 | 0.653 / 0.648 |

J441a ✗ (deep ≈ or < flat, never +0.10), J441b ✗ (deep never ≥0.85), J441c ✓ → **NULL.**

**Depth (random composition) is not the escape.** A 2-layer random feature network is no better than
a flat one at matched units — slightly worse, because a random layer-2 of a random layer-1 adds
another *untargeted* nonlinearity rather than constructing `x0·x1·x2`, and splitting the budget makes
each layer narrower. Composition helps only when the layers are *learned* to build the interaction
(backprop) — which is the non-local credit-assignment route the substrate ethos avoids.

**This closes the cheap-route search.** Across JEP-438→441 every backprop-free / non-enumerative
route to high-order discovery with no low-order signal has been ruled out: greedy climbing (no
gradient), flat random features (need ≳C(P,k), degrade with N), random depth (no targeting). Only
*targeted* routes work — order-k enumeration (OMP/brute force, O(C(P,k))) or *learned* features
(backprop, non-local). The open problem is now sharply bounded: **tractable, LOCAL, targeted
high-order feature discovery** — none of the cheap routes provides it. See
docs/amendments/ENERGY_FRONTIER_SUMMARY.md.

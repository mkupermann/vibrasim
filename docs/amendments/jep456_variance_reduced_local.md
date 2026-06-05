# JEP-456 — Toward EFFICIENT local discovery: does variance reduction speed up node perturbation?

## Motivation
JEP-445 showed a fully-local rule (node perturbation) CAN discover an order-3 interaction, but is
high-variance and inefficient (needed 20 000 epochs). The honest open problem is EFFICIENT local
discovery. JEP-456 tests the first established lever: ANTITHETIC sampling (perturb +ξ and −ξ, use the
difference) — an unbiased, ~half-variance estimator that stays fully local (local activity + one
global scalar). If it solves the same task in far fewer epochs than plain node perturbation, variance
reduction is a real efficiency gain on the path to e-prop. Established methods (node perturbation;
antithetic variates), named; not new science. No transformer, no backprop, no weight transport.

## Method (`tools/run_jep456_variance_reduced_local.py`)
Order-3 parity `y=x0·x1·x2`, P=18, M=64, N=2500/1000, seeds 0 & 7, REDUCED budget EPOCHS=5000 (vs
JEP-445's 20 000). Two fully-local rules (output weights by local delta rule in both):
- **plain node perturbation:** perturb hidden by σξ once; modulate by ΔL.
- **antithetic node perturbation:** perturb by +σξ and −σξ; modulate by (L₊−L₋)/(2σ²)·ξ.
Report held-out accuracy + whether the true triple {0,1,2} is found (permutation importance).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J456a (variance reduction speeds convergence):** antithetic held-out ≥ 0.90 at 5000 epochs AND
  ≥ plain + 0.10, both seeds.
- **J456b (antithetic finds the interaction):** antithetic top-3 importance = {0,1,2}, both seeds.
- **J456c (honest — still not free):** even antithetic needs ≫ a handful of epochs (report epochs;
  it is a constant-factor speedup, not an asymptotic fix — the fundamental cost remains).

Honest expectation: antithetic should converge materially faster (lower-variance gradient), so it
clears 0.90 at a budget where plain does not. PASS = variance reduction is a real efficiency lever for
local discovery. NULL if antithetic ≈ plain (the variance was not the bottleneck here). Bars locked;
no retuning. No transformer.

## RESULT (2026-06-05): NULL — and it CORRECTS the JEP-445 efficiency caveat

| seed | plain node-pert (5000 ep) | antithetic (5000 ep) | anti top-3 |
|------|---------------------------|----------------------|------------|
| 0 | 1.000 | 1.000 | [0,1,2] |
| 7 | 1.000 | 1.000 | [0,1,2] |

J456a ✗ (no advantage — both at ceiling), J456b ✓, → **NULL.**

**Why NULL, and the honest correction.** I predicted plain node perturbation would struggle at 5000
epochs (JEP-445 used 20 000), leaving headroom for antithetic to win. It did NOT — **plain already
solves at 5000 (1.000)**. So antithetic can't show a +0.10 advantage; variance reduction helps only
when the plain rule is variance-LIMITED, and at P=18/M=64 it is not. Two honest consequences:
1. **JEP-445's "high-variance, doesn't scale efficiently" caveat was OVERSTATED at this scale.** Node
   perturbation solves order-3 parity in ≤5000 epochs here (the 20 000 was overkill) — more efficient
   than I implied. I'm flagging this as a correction (honesty over consistency), same as the JEP-439
   retraction.
2. **The scaling claim remains UNTESTED.** Node perturbation's variance is known to grow with network
   size (theory), but I never measured the practical inefficiency at LARGER M/P — so "it doesn't scale"
   is a theoretical expectation I have not demonstrated. Manufacturing headroom by shrinking the budget
   post-hoc to make antithetic win would be exactly the bar-tuning the protocol forbids; I won't.

Net: variance reduction is not the bottleneck at this scale, and local discovery is cheaper than the
earlier caveat suggested. The genuinely open question (does it stay tractable as scale/order grows,
and does an eligibility-trace rule beat node perturbation on a TEMPORAL high-order task) is unchanged —
and is real research, not a quick budget tweak. Established methods, named; no new science.

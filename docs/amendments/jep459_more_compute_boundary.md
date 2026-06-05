# JEP-459 — Does MORE compute push the local-learning boundary outward?

## Motivation
Michael offered a larger compute budget (modern CPU, 64 GB RAM, optionally GPU). JEP-458 located the
fully-local rule's wall AT FIXED MODEST compute (M=64, 5000 epochs): solid to order-5, seed-unstable
at order-6, chance by order-8. The directly-motivated question his offer unlocks: is that wall
**compute-bound** (movable with a bigger network / more epochs / more data) or **fundamental**? JEP-459
throws materially more compute at the exact settings that broke and measures whether the boundary
moves. Established method (node perturbation), named; a scaling measurement, no new science. No
transformer, no backprop.

## Method (`tools/run_jep459_more_compute_boundary.py`)
Same fully-local node perturbation, but scaled up: **M=192** (vs 64), **EPOCHS=20000** (vs 5000),
**N_train=5000** (vs 2500). P=18, seeds 0 & 7. Test the orders that were unstable/broken at modest
compute: k ∈ {6, 8, 10}. Report held-out accuracy + exact-tuple recovery. (Baseline for comparison:
at M=64/5000ep, k6 was 0.52–0.97, k8 ≈ 0.51, k10 ≈ 0.50.)

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J459a (compute fixes the soft edge):** k=6 ≥ 0.90 on BOTH seeds (was seed-unstable at modest
  compute) — the variance-driven instability is bought off with compute.
- **J459b (boundary moves outward):** k=8 ≥ 0.85 on both seeds (was ≈ chance 0.51 at M=64/5000ep) —
  more compute pushes the wall past order-8.
- **J459c (report the new edge):** state k=10's accuracy and whether a wall remains even at this
  budget.

Honest expectation: more compute moves the boundary out (k=6 solid, k=8 solved); k=10 is the test of
whether a wall remains. PASS = the local-learning wall is compute-bound (movable), strengthening the
"local rules are capable" picture. NULL if k=8 stays ≈ chance despite 4×M and 4× epochs (the wall is
harder than compute alone fixes). Bars locked; no retuning. No transformer.

## Result: ABORTED (not a result) — reprioritized per Michael's directive

The scaled-compute run (M=192, 20000 ep) was still in progress when Michael redirected the work to a
new-science hunt ("don't work with known"). JEP-459 is a known-methods scaling measurement, so it was
stopped mid-run to free compute for the native-substrate exploration (NSH-01+). This is an honest
ABORT, not a NULL/PASS — the high-M boundary question (does more compute push the order-6-8 wall of
JEP-458 outward?) remains open and can be resumed later. No bars claimed either way.

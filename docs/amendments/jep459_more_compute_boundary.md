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

## CORRECTION + RESULT (2026-06-05): it actually COMPLETED — my abort attempt failed

I tried to stop this run to reprioritize, but the kill did not take and it ran to completion. So the
earlier "ABORTED" note was wrong — there IS a real result, recorded honestly here (honesty over the
convenience of the abort story):

| seed | k=6 | k=8 | k=10 |
|------|-----|-----|------|
| 0 | 1.00 (found) | 0.48 | 0.49 |
| 7 | 1.00 (found) | 0.50 | 0.49 |

J459a ✓ (k=6 → 1.00 both seeds — compute FIXES the soft edge), **J459b ✗ (k=8 still ≈ chance despite
3×M and 4× epochs), J459c k=10 ≈ chance → NULL/partial.**

**Finding — the boundary has TWO regimes.** The order-6 instability JEP-458 saw (0.52–0.97 at
M=64/5000ep) was **variance/compute-limited** — 4× compute makes it solid (1.00). But the order-8 wall
does NOT move with 4× compute (still chance). So the local-learning boundary is partly compute-bound
(the soft edge near k=6) and partly a **harder limit** (k≥8) that more compute alone does not crack at
this budget. This sharpens JEP-458: the wall is not a single soft edge — there is a genuine hard
boundary beyond the compute-movable one. Established method (node perturbation); measurement, not new
science.

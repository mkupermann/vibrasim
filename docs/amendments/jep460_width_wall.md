# JEP-460 — Is the order-8 "hard wall" genuinely new, or the known exponential parity-width law?

## Motivation
My most honest "genuinely unexplained" candidate is JEP-459's order-8 hard wall: more compute (4×) did
not move it. But a sharp KNOWN hypothesis explains it: a 2-layer net needs ~2^k hidden units to
REPRESENT order-k parity (classic circuit-complexity / Hastad-type result). The data already fits:
order-5 solved at M=64 (2^5=32<64), order-6 at M=192 (2^6=64<192), order-8 FAILED at M=192
(2^8=256>192). So the wall may be a WIDTH (representational) limit, movable by M, not epochs — which
would mean it is EXPLAINED, not new science. JEP-460 tests this directly: sweep width M at fixed k=8.
If solving crosses near M~256, the "hard wall" is the textbook exponential-width law and the
new-science candidate is honestly closed. If even large M fails, the anomaly is deeper.

## Method (`tools/run_jep460_width_wall.py`)
Order-8 parity (y = x0·…·x7), P=18, N=3000 train / 1000 test, fully-local node perturbation, 8000
epochs, seeds 0 & 7. Sweep M ∈ {128, 256, 384, 512}. Report held-out accuracy + exact-tuple recovery.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J460a (below 2^k fails):** M=128 accuracy ≤ 0.65, both seeds (128 < 2^8=256).
- **J460b (above 2^k solves):** M=512 accuracy ≥ 0.85, both seeds — the wall is WIDTH, moved by M.
- **J460c (crossing near 2^k):** M=256 accuracy > M=128 accuracy + 0.15, both seeds (the threshold is
  near the 2^k=256 scale, not far above it).

Predicted PASS → the order-8 wall is the KNOWN exponential parity-width requirement (explained, NOT
new science); the honest close of the new-science candidate. NULL if M=512 also fails (the wall is not
mere width — a deeper, possibly genuinely-unexplained limit worth chasing). Bars locked; no retuning.
No transformer.

## Result
(filled after the run)

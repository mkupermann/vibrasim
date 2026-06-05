# JEP-315 — Repair noise robustness (fixes JEP-313 NULL)

## Motivation
JEP-313: recall under a corrupted query cue fell below 0.90 at only ~10% key bit-flips (f* ≈ 0.05–0.10), worse than
predicted — a superposed store's signal per fact is ~1/√K, so corruption eats the cleanup margin fast. Two
substrate-native levers to restore tolerance: (a) WIDER vectors (larger D shrinks the untaught/noise floor ~1/√D,
widening the margin); (b) REDUNDANT encoding (store R independent permuted copies, average the retrievals — classic
redundancy-for-recall). Measure both vs the JEP-313 baseline. No transformer.

## Pre-registered bars (BEFORE the run)
- **J315a (width helps):** at D=8192 and D=16384, recall at f=0.10 ≥ 0.90 both seeds; report the f* shift vs
  D=4096 (0.05–0.10 baseline).
- **J315b (redundancy helps):** with R=5 redundant copies (averaged) at D=4096, recall at f=0.10 ≥ 0.90 both seeds.
- **J315c:** report which lever is more dimension-efficient (recall-at-f per unit storage).

Predicted most-likely failure: redundancy via the SAME atom vectors doesn't add independent noise channels (the
corruption is on the shared key, not the storage) — averaging identical retrievals won't help. If J315b fails,
that's the diagnosis (need independent KEY encodings per copy, not just independent storage), reported not tuned.
Width (J315a) should reliably help. If even D=16384 misses 0.90 at f=0.10, the bottleneck is the (1−2f) signal
correlation itself, not the floor — a fundamental finding.

## Result (seeds 0, 7): **PASS** (width fixes it; redundancy confirmed not to — as predicted)
Recall at key-flip fraction f:

| D | f=0.05 | f=0.10 | f=0.15 | f=0.20 | f=0.30 |
|---|--------|--------|--------|--------|--------|
| 4096 (baseline) | 0.95/0.97 | **0.88/0.92** | 0.84/0.85 | 0.73/0.75 | 0.35 |
| 8192 | 1.0 | **1.00** | 0.97/0.98 | 0.97 | 0.65/0.75 |
| 16384 | 1.0 | **1.00** | 1.00 | 1.00 | 0.92/0.96 |

- **J315a (width helps): PASS** — D=8192 and 16384 both give recall **1.0** at f=0.10 (vs 0.88 baseline); f* shifts
  from ~0.10 → ~0.25 (8192) → >0.30 (16384). Doubling D roughly doubles the tolerated corruption.
- **J315b (redundancy helps): FALSE** — R=5 copies gave **0.83/0.80** at f=0.10, *worse* than baseline. Exactly the
  predicted failure: corruption is on the SHARED cue (`e·e_corrupt` is identical across copies), so averaging can't
  undo it — and the copy-modifier vectors add crosstalk. Redundancy is a RECALL/crosstalk tool, not a
  shared-cue-noise tool (cf. calibration lesson #11).
- **J315c:** width is the dimension-efficient lever for noisy cues; redundancy is not.

## Verdict: **PASS**
Wider vectors restore noise robustness (D=8192 tolerates ~20% cue corruption at ≥0.97; D=16384 ~30%) — the lever is
dimension, set per the cue-noise expected. Closes the JEP-313 NULL. The redundancy result is a HIT on the
pre-registered prediction (it shouldn't help shared-cue corruption, and didn't). Established analysis (HRR noise
scaling), named as such.


# G63 — Filter bank: frequency discrimination by membrane size

Pre-registered: 2026-06-02 (BEFORE the run). G61 showed the low-pass cutoff is tunable by membrane
size (τ ∝ R). Two different-sized membranes therefore form a two-channel FILTER BANK: a mid-frequency
input passes the small membrane (higher cutoff) more than the large (lower cutoff) → the two channels
discriminate frequency. A first step toward substrate-level spectral analysis.

## Method
Drive a mid-frequency modulated foreign influx (period 600) into the small (box-22, R≈11, τ≈80) and
large (box-33, R≈16.5, τ≈123) membrane. Measure interior response amplitude (single-bin DFT) in each.
Discrimination = amp(small)/amp(large). Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G63a | Frequency discrimination | amp(small)/amp(large) ≥ 1.3 at the mid frequency, both seeds |

PASS = G63a → two membrane sizes form a filter bank that discriminates frequency (the smaller
membrane passes the mid-frequency more): substrate-level spectral discrimination from the tunable
analog filter. NULL: ratio < 1.3 → the two cutoffs (only ~1.5× apart) are too close to discriminate
this frequency cleanly. Honest either way. No post-hoc threshold tuning.

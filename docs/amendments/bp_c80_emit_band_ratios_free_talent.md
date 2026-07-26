# BP-C80 — Free dual talent with emit_band_ratios (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C79; `emit_band_ratios` never BP free dual  
**Discipline:** **new mechanism** = decade-skewed `emit_band_ratios` under fire emission (`n_emit>0`) free dual + wall vs default ratios. Budget-fit T=500 N=250.

## Hypothesis

Wall ON. Neuron dynamics ON. Both arms fire-emit with `n_emit=8`.  
Treatment: free dual L-low R-high with `emit_band_ratios=(0.01, 1.0, 100.0)` (decade-spaced emission bands).  
Control: same inject + `n_emit=8` with default `emit_band_ratios=(0.08, 1.0, 12.5)`.

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction (L mean decade < R) | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {6801,6811} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Negative control

Default band ratios (control) must not pass B1-class order at ≥0.90 while treat does (B2≤0.80 and B4≥0.15).

## What is NOT claimed

Not multi-trial port curriculum. Not C16 strength-decay. Not retune of C31 n_emit alone (both arms share n_emit; only ratios differ).

## Prediction

?? LEAN NULL. Emission band multipliers affect post-fire spawn freqs; free dual order is mostly inject-driven; decade-skewed emit unlikely to unlock specialisation over default emit.

## RESULT

*(filled after run)*

# BP-E3 — ILW write order (which side last)

**PRE-REGISTERED 2026-07-20 before data**

## Hypothesis
Write L then R (or R then L) with N_write each; idle; readout of which side has **higher mean strength per node** (or total strength) decodes **last-written side** ≥0.85. Control: simultaneous equal writes → imbalance ≤0.25 (same as E2 B3).

## Bars
B1 order decode ≥0.85 · B2 equal-write imbalance ≤0.25 · B3 both sides populated after sequence ≥0.90

Protocol: seeds {231,241}, trials 10, N_write=15/side, T_idle=150, midplane+ILW.

## RESULT
*(after)*

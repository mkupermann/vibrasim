# BP-E3 — ILW write order (which side last)

**PRE-REGISTERED 2026-07-20 before data**

## Hypothesis
Write L then R (or R then L) with N_write each; idle; readout of which side has **higher mean strength per node** (or total strength) decodes **last-written side** ≥0.85. Control: simultaneous equal writes → imbalance ≤0.25 (same as E2 B3).

## Bars
B1 order decode ≥0.85 · B2 equal-write imbalance ≤0.25 · B3 both sides populated after sequence ≥0.90

Protocol: seeds {231,241}, trials 10, N_write=15/side, T_idle=150, midplane+ILW.

## RESULT
**NULL** (2026-07-20). B1_last=**0.450** (≥0.85 fail), B2_eq_imb=**0.000** (≤0.25 pass), B3_pop=**1.000**.

### Finding
Equal *N_write* sequential ILW L→R or R→L leaves **symmetric strength** after idle. Strength sum does **not** encode last-written side (~chance 0.45). Same fixed `ilw_delta_strength` per event → mass matches count, not recency. No bar retune of 0.85.

### Boundary
**Order-from-equal-strength-ILW is CLOSED** as a mechanism family. Next order claim needs a *new* mechanism (e.g. inter-write decay gap, eligibility, or distinct order channel) under a new ID — not E3 bar lowering.

### Next (not E3 retry)
Cross-port **content association** (E4): L band predicts R partner after joint write — different question from recency.

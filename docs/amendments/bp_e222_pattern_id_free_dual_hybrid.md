# BP-E222 — Pattern-id G12 + free dual hybrid (C16 strength-decay class)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** C16 PARTIAL strength-decay unlock; G12 E194–E197; open hybrid  
**Discipline:** free dual L-low R-high + wall + `ilw_strength_decay_tau=30`. Treat: `firing_eligibility_gate=True` (ambient). Ctrl: gate OFF. Same bars as free dual talent; tests whether G12 breaks C16-class unlock.

## Hypothesis
1. Treat (decay+gate) ordered ≥0.90  
2. Ctrl (decay only) ordered ≥0.90  
3. Treat pop ≥0.80  
4. |treat−ctrl| ≤0.20 (gate does not destroy unlock)

## Bars
B1 treat ≥0.90 · B2 ctrl ≥0.90 · B3 treat pop ≥0.80 · B4 |delta| ≤0.20  

Seeds {6511,6521} trials 2. T=500 N=250. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN NULL on B1/B2: budget-fit T=500 may not reach C16 unlock (C16 used T=1200 N=400). If both NULL, hybrid not informative at this budget; if both PASS, gate no-ops with ambient (E197).

## RESULT
**NULL** (2026-07-26). B1=0.25 B2=0.25 B3=0.25 B4=0.0. Budget-fit T=500 does not reach C16-class unlock; G12 ambient gate no-op (equal treat/ctrl). Hybrid not informative at this budget; no bar retune.

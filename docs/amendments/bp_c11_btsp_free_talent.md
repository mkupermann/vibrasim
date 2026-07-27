# BP-C11 — Free dual talent with BTSP eligibility (new mechanism)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C1–C10 closed dual-inject classes; BTSP G14 primitive  
**Discipline:** not band/period retune — **BTSP + neuron dynamics** on free dual inject (new primitive class)

## Hypothesis
Dual regional free inject (C1b density: N=400/side, r_2=28, midplane wall).  
**Treatment:** `btsp_enabled=True`, `neuron_dynamics_enabled=True` (eligibility + plateau potentiation).  
**Control:** same world, `btsp_enabled=False`, neuron dynamics still ON (fire without BTSP weight).

BTSP should bias within-region engram consolidation so decade specialisation hits 0.90 where pure free failed (~0.78).

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | BTSP ON: mean_decade_L < mean_decade_R ∧ both n≥1 | ≥0.90 |
| B2 | BTSP OFF control same measure | ≤0.80 |
| B3 | BTSP ON both regions populated | ≥0.80 |
| B4 | BTSP ON success − control success | ≥0.15 |

Seeds {1741,1751,1761} trials 3 each. T=1200. Budget ~15 min, hard cap 30 min.

## Prediction
🔮 LEAN NULL (BTSP needs plateau fire on level-4 atoms; free bind may not drive enough firing for eligibility). Still maps whether BTSP class unlocks C.

## RESULT
**NULL** (2026-07-20). B1=0.778 B2=0.778 B3=1.0 B4=0.0.  
BTSP ON matches control exactly at C1b-class specialisation; no unlock. Free dual inject + BTSP eligibility does not lift talent to 0.90.

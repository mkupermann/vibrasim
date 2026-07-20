# BP-C16 — Free dual talent with ILW strength decay (new mechanism)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C1–C15 closed free dual classes; PRIM3 ilw_strength_decay  
**Discipline:** not band retune — **ilw_strength_decay_tau** recency filter (new class)

## Hypothesis
Dual regional free inject (C1b density).  
**Treatment:** `ilw_strength_decay_tau=30` (strength leaks toward baseline; recency structure dominates).  
**Control:** tau=0.

Recency decay should prune stale cross-structure and lift decade specialisation ≥0.90.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Decay ON: mean_decade_L < mean_decade_R ∧ both n≥1 | ≥0.90 |
| B2 | Decay OFF control | ≤0.80 |
| B3 | Decay ON both populated | ≥0.80 |
| B4 | Decay − control success | ≥0.15 |

Seeds {2271,2281,2291} trials 3. T=1200. Budget ~15 min, hard cap 30 min.

## Prediction
🔮 LEAN NULL (decay may not act on free-formed node strengths the way ILW port writes do). Maps decay class.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=0.778 B3=1.0 B4=0.222.  
**First free dual talent unlock at pre-registered 0.90** with `ilw_strength_decay_tau=30`. Control remains ~C1b ceiling (0.778). Decay class opens free talent without engineered ports.

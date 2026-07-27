# BP-C15 — Free dual talent with bridge consolidate (new mechanism)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C1–C14 closed free dual classes; BET-108 bridge_consolidate  
**Discipline:** not band retune — **bridge_consolidate_threshold** locks strong bridges (new class)

## Hypothesis
Dual regional free inject (C1b density).  
**Treatment:** `bridge_consolidate_threshold=0.5` (locks bridges that reach threshold).  
**Control:** threshold=0 (no lock).

Consolidation should stabilize within-region structure and lift specialisation ≥0.90.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Consol ON: mean_decade_L < mean_decade_R ∧ both n≥1 | ≥0.90 |
| B2 | Consol OFF control same | ≤0.80 |
| B3 | Consol ON both populated | ≥0.80 |
| B4 | Consol − control success | ≥0.15 |

Seeds {2101,2111,2121} trials 3. T=1200. Budget ~15 min, hard cap 30 min.

## Prediction
🔮 LEAN NULL (same C1b ceiling; consolidate may not bias decade structure). Maps consol class.

## RESULT
**NULL** (2026-07-20). B1=0.778 B2=0.667 B3=1.0 B4=0.11.  
Consol slightly above control but fails 0.90 and delta≥0.15 bars. No talent unlock.

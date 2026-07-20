# BP-C21 — Free dual talent with atom valence constraint (new mechanism)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C16 family CLOSED PARTIAL (decay not locked)  
**Discipline:** not dual-inject+decay retune — **atom_valence=2** (linear chain topology) on free dual inject

## Hypothesis
Dual regional free inject (C1b density, midplane wall, dual bands).  
**Treatment:** `atom_valence=2` (max 2 bonds per atom → linear chains).  
**Control:** `atom_valence=0` (unlimited).

Linear valence should reduce messy cross-links and lift decade specialisation ≥0.90.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Valence=2: mean_decade_L < mean_decade_R ∧ both n≥1 | ≥0.90 |
| B2 | Valence=0 control same measure | ≤0.80 |
| B3 | Valence=2 both populated | ≥0.80 |
| B4 | Valence − control success | ≥0.15 |

Seeds {2861,2871,2881} trials 3. T=1200. Budget ~15 min, hard cap 30 min.

## Prediction
🔮 LEAN NULL (valence may starve L4 formation or not affect decade structure). Maps valence class for free talent.

## RESULT
**NULL** (2026-07-20). B1=0.556 B2=0.889 B3=1.0 B4=−0.33.  
atom_valence=2 **hurts** specialisation vs unlimited; valence class closed for free dual talent unlock.

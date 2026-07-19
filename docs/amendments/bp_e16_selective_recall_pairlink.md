# BP-E16 — Selective cross-port recall with PRIM5 pair-link

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Depends on:** PRIM5-D0 PASS; E15 NULL (all-to-all)  
**Not** E15 bar retune — **new graph**: exclusive pair links only (`atom_valence=0`, pair_link ON)

## Hypothesis

Store pairs 0 and 1 via `apply_ilw_pair_write` (multislot + pair_link).  
Force-fire L atoms of class 0 only.  
Peak charge on R class-0 > peak on R class-1 in ≥ **0.80** trials.  
Control force-fire all L: fraction R0>R1 ≤ **0.60**.  
Both exclusive bridges present ≥ **0.90**.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Selective fire L0: peak_R0 > peak_R1 | ≥ **0.80** |
| B2 | Fire-all: peak_R0 > peak_R1 | ≤ **0.60** |
| B3 | Two cross bridges after store | ≥ **0.90** |

Seeds {541, 551}, trials 12. Budget 150s / hard 300s.

## Prediction
🔮 PASS lean: exclusive edges route charge only along matched pair.

## RESULT
**PASS** (2026-07-20 night). B1=1.0 B2=0.0 B3=1.0. Selective L0→R0 charge with PRIM5 exclusive links. E15 boundary stands for all-to-all.

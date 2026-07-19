# BP-E12 — No generative partner (boundary)

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Depends on:** E9/E11 association = co-presence  
**Discipline:** locks what association is **not**

## Hypothesis

**H-E12.** After dual ILW of exclusive pair c, **kill all R-side L4**, then re-write **L only** with L-band of c:

1. R does **not** repopulate with partner band (fraction trials with R partner present ≤ **0.15**).  
2. L still decodes class-c L-band ≥ **0.90**.  
3. Control dual-write without kill: R partner present ≥ **0.90**.

PASS means: association is **co-presence / co-write**, not generative completion from L alone.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | After kill+R-rewrite-L: R has partner band | ≤ **0.15** |
| B2 | After kill+rewrite-L: L band == c | ≥ **0.90** |
| B3 | Control no-kill: R partner present | ≥ **0.90** |

Seeds {441, 451}, trials 10; N_write=15; T_idle=100; multislot ON; valence=4; r_2=45.

## Prediction
🔮 PASS (boundary): no generative partner; L persists; control has R.

## RESULT
**PASS** (2026-07-20 night). B1_R_after_kill=0 B2_L=1.0 B3_ctrl=1.0. Association is co-presence, not generation.

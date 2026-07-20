# BP-E27 — Curriculum map overwrite (last map wins)

**PRE-REGISTERED 2026-07-20 before data (scheduler)**  
**Depends on:** E25/E21/PRIM5; E6 content overwrite for single ports  
**Discipline:** multi-trial **relearning** of associations; not free talent; not E3

---

## Hypothesis

**H-E27.** Two exclusive maps on the same L bands:

| class | Map A (fL,fR) | Map B (fL,fR) |
|-------|---------------|---------------|
| 0 | 400, 7000 | 400, 2500 |
| 1 | 1500, 2500 | 1500, 7000 |

Train Map A (multi-sample slots), then Map B (same slots, PRIM5 pair_link overwrites/replaces links). Latch end-state partner decode (table used **only for scoring**):

1. After A→B: fraction routes match **Map B** ≥ **0.85**  
2. After A→B: fraction routes match **Map A** ≤ **0.25** (first map residual)  
3. After A only: match Map A ≥ **0.85**  
4. Bridged L ≥1 in ≥ **0.90** of A→B trials  

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | A→B match Map B | ≥0.85 |
| B2 | A→B match Map A | ≤0.25 |
| B3 | A-only match Map A | ≥0.85 |
| B4 | A→B has bridged L | ≥0.90 |

Seeds {871,881} trials 10. Smoke 1×3. Budget 200s / hard 400s.

## Prediction
🔮 LEAN NULL or borderline: PRIM5 strengthens same L atoms but may create **extra** bridges to both R partners (multislot R) so residual A stays high. Most-likely miss B2.

## RESULT
**NULL** (2026-07-20 scheduler). B1_match_B=**0.500**, B2_residual_A=**0.500**, B3_A_only=**1.000**, B4=**1.000**.

### Calibration
🔮 lean NULL on B2 — **HIT**. After A→B both partners remain; latch routing ~chance between A and B maps. Multislot+pair_link **adds** links rather than replacing the curriculum. A-only still solid (B3).

### Boundary
Curriculum overwrite of exclusive pair maps is **not** achieved under current PRIM4/5. First and second maps coexist.

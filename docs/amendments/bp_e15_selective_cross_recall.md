# BP-E15 — Selective cross-port recall (dictionary + charge)

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Depends on:** E11 dual pairs, E14 peak charge, PRIM4 multislot

## Hypothesis

Store **two** exclusive pairs (class 0 and 1) with multislot + valence=4.  
Force-fire only L atoms whose freq is nearest class-0 L-band.  
During prop window, **peak charge on R atoms nearest class-0 R-band** exceeds peak charge on R atoms nearest class-1 R-band in ≥ **0.80** of trials (selectivity).  

Control: force-fire **all** L atoms → class-0 R peak not systematically > class-1 (fraction class0>class1 ≤ **0.60**).  

Both pairs still co-resident (bridge-class set contains 0 and 1) ≥ **0.80**.

## Bars
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treat: fraction peak_R0 > peak_R1 | ≥ **0.80** |
| B2 | Fire-all control: fraction peak_R0 > peak_R1 | ≤ **0.60** |
| B3 | Both pairs co-resident after store | ≥ **0.80** |

Seeds {501, 511}, trials 12; N_write=12; T_prop=60. Budget 120s / hard 240s.

## Prediction
🔮 LEAN NULL or borderline: bridges may cross-link all L–R pairs (complete bipartite), so firing L0 also charges R1. Most-likely miss B1 if graph is fully connected across bands.

## RESULT
**NULL** (2026-07-20 night). B1_selective=**0.000**, B2_fireall=**0.000**, B3_both=**1.000**.

### Calibration
🔮 lean NULL — **HIT**. Complete bipartite cross-bridges: firing L0 charges all R partners equally (or R1 ≥ R0). Selective recall needs **exclusive pair links**, not all-to-all cross graph.

### Next
PRIM5: dual-write creates bridge only between the two slots just written (band-matched exclusive link).

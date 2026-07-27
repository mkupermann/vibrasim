# BP-E9 — Pair class from cross-port bridge endpoints

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Depends on:** E8 PASS (cross bridges exist)  
**Discipline:** readout uses **bridge endpoints only** (graph-native object); still uses known pair centroids (honest: not unsupervised learning)

---

## Hypothesis

**H-E9.** After dual ILW of exclusive pair class c (E5 table, K=3) with valence=4, r_2=45, idle:

1. Every trial with ≥1 cross-mid bridge: mean endpoint freqs (f on L-end, f on R-end) nearest-match to a pair in the table equals true class c ≥ **0.85** of trials.  
2. Control: independent L/R classes → bridge endpoint pair matches *some* exclusive-table row ≤ **0.45** (false “legal pair”).  
3. Dual write still has ≥1 cross bridge ≥ **0.90**.

## Bars

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treat: bridge-endpoint pair class == true c | ≥ **0.85** |
| B2 | Ctrl indep: endpoints match any exclusive pair row | ≤ **0.45** |
| B3 | Treat: ≥1 cross bridge | ≥ **0.90** |

## Protocol
Seeds {361, 371}, trials 12; N_write=15; T_idle=300. Budget 90s / hard 180s.

## Prediction
🔮 PASS: endpoints are the ILW-seeded atoms with written freqs; bridge just links them.  
Most-likely miss: mean over multiple bridges / freq drift confuses mid class.

## RESULT
**PASS** (2026-07-20 night). B1=**1.000**, B2_ctrl=**0.250**, B3=**1.000**.

Bridge + endpoint freqs recover exclusive pair class; independent L/R rarely look like legal pairs. Still uses table centroids (honest).

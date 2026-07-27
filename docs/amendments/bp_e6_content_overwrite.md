# BP-E6 — Sequential content overwrite (last joint pair wins)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E5 K=3 storage  
**Discipline:** not E3 order (strength); **content** replacement via sequential dual ILW. Not another K-farm without mechanism.

---

## Hypothesis

**H-E6.** ILW freq nudge on existing port atoms causes a **second** joint write of a *different* exclusive pair to dominate centroid decode after idle:

1. Write pair class **first** (N_write/side), then pair class **last** ≠ first (N_write/side), idle T_idle.  
2. L and R nearest-centroid both equal **last** ≥ **0.85**.  
3. Fraction of trials where L still decodes as **first** ≤ **0.20** (residual first wiped).  
4. Control: write class A then class A again → decode A ≥ **0.90** (no false flip).

Uses E5 pair table (3 classes). first/last sampled distinct.

---

## Bars (locked)

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treat: L decode == last | ≥ **0.85** |
| B2 | Treat: R decode == last | ≥ **0.85** |
| B3 | Treat: L decode == first (residual) | ≤ **0.20** |
| B4 | Control same-class twice: L decode == A | ≥ **0.90** |

## Protocol
Seeds {291, 301}, trials 12; smoke 1×4. N_write=20, T_idle=150. Pairs as E5. Budget 60s / hard 150s.

## Prediction (locked BEFORE run)

🔮 **PASS** lean: repeated strengthen+nudge (0.85 old + 0.15 seed)×20 after first block drives mean freq to last centroid.  
Most-likely miss: residual first still >0.20 if first block seeds a *second* atom that is not re-targeted, leaving mixed means.

## NOT claimed
Temporal order from strength (E3 closed); free talent; multi-trial learning without joint rewrite.

## RESULT
**PASS** (2026-07-20). B1_L_last=**1.000**, B2_R_last=**1.000**, B3_residual_first=**0.000**, B4_ctrl=**1.000**.

### Calibration
🔮 predicted PASS — **HIT**. Sequential ILW on same port atoms overwrites band identity; residual first wiped.

### Scope
Curriculum rewrite of port content works under engineered ILW nudge. Not temporal order-from-strength (E3); not learning.

# BP-E5 — Associative capacity K=3 (exclusive pairs)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E4 PASS (2-class write-time pairing)  
**Discipline:** capacity climb, not E4 bar retune; engineered ILW named as such

---

## Hypothesis

**H-E5.** With midplane + ILW, a **3-class exclusive map**

| class | seed_freq L | seed_freq R |
|-------|-------------|-------------|
| 0 | 400 | 7000 |
| 1 | 1500 | 2500 |
| 2 | 5000 | 800 |

written jointly (N_write/side), idle T_idle, then:

1. Nearest-centroid decode of mean **L** freq among {400,1500,5000} recovers true class ≥ **0.85**  
2. Nearest-centroid decode of mean **R** freq among partner centroids {7000,2500,800} recovers true class ≥ **0.85**  
3. Control: R class drawn **independent** of L → fraction of trials where (L-decode == R-decode) ≤ **0.45** (no forced pairing)  
4. Both sides populated ≥ **0.90** of treatment trials

B1+B2 = both ports hold their class structure; B3 = without write-time pairing the two decodes do not systematically match.

---

## Bars (locked)

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treatment: L nearest-centroid class accuracy | ≥ **0.85** |
| B2 | Treatment: R nearest-centroid class accuracy | ≥ **0.85** |
| B3 | Control indep: fraction L-decode == R-decode | ≤ **0.45** |
| B4 | Treatment both sides ≥1 L4 | ≥ **0.90** |

**PASS** iff all four. Protocol: seeds {271, 281}, trials 12; smoke 1×4. N_write=20, T_idle=150. Budget est 60s / hard 150s.

## Prediction (locked BEFORE run)

🔮 **PASS** lean: centroids well-separated (400 / 1500 / 5000 vs partners far). Treat B1/B2 ≈0.95–1.0; ctrl ≈0.33.  
Most-likely miss: mid-band 1500 collapses toward neighbor under ILW freq nudge; B1 or B2 <0.85.

## NOT claimed
Learned multi-trial association; free talent; temporal order.

## RESULT
**PASS** (2026-07-20). B1_L=**1.000**, B2_R=**1.000**, B3_ctrl_match=**0.333**, B4_pop=**1.000**.

### Calibration
🔮 predicted PASS — **HIT**. Three exclusive ILW bands remain separable on both halves; independent L/R match ≈1/3.

### Scope (honest)
K=3 write-time multi-band **storage** under engineered seed_freq + experimenter centroids. Not multi-trial learning; association map is external to the substrate (see pattern `write_time_map_not_learning`).

# BP-E4 — Cross-port content association (write-time pair)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM2 ILW, PRIM1 midplane, E2 port presence  
**Discipline:** engineered dual write named as such; not free talent; not E3 bar retune  
**Question (new):** After a *joint* dual-port ILW of a correlated frequency pair, does **left-side mean frequency alone** predict the **right-side band class**?

---

## Hypothesis

**H-E4.** With midplane wall + ILW:

- **Treatment:** On each trial, sample association class `c ∈ {0,1}`:
  - `c=0`: write L with seed_freq **500**, R with **5000**
  - `c=1`: write L with **5000**, R with **500**  
  N_write events per side, then idle T_idle.  
  **Readout:** mean `k_freq` of level≥4 nodes with x < mid → `band_L` (low if mean < geometric mid √(500·5000)≈1581 else high).  
  Predict R class as **opposite** of L band (paired association).  
  Accuracy vs true R write class ≥ **0.90**.

- **Control (uncorrelated):** L and R seed_freq drawn **independently** uniform from {500, 5000}. Same N_write, idle. Same L→predict-R rule. Accuracy ≤ **0.60** (near chance; association broken).

- **Sanity:** both sides populated (n≥1 level≥4) in ≥ **0.90** of treatment trials.

This is **write-time structural pairing preserved across ports**, not multi-trial learning or free emergence. Honest §4.8 port curriculum step after E2.

---

## Mechanism

- midplane ON, ILW ON  
- No free-vib inject  
- Read only left half frequencies for prediction; ground truth = which band was written on R  
- Geometric mid threshold: `F_MID = sqrt(500*5000) ≈ 1581.1`

---

## Bars (locked)

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Treatment: L-band → predicted R-class accuracy | ≥ **0.90** |
| B2 | Control uncorrelated: same decoder accuracy | ≤ **0.60** |
| B3 | Treatment: both sides have ≥1 level≥4 | ≥ **0.90** of trials |

**PASS** iff B1∧B2∧B3.  
**NULL** if any bar fails but protocol clean.  
**FAIL** if crash / budget overrun / control trivially invalid.

---

## Protocol

- Seeds `{251, 263}`, trials/seed = **12** (full); smoke: 1 seed × 4 trials  
- N_write = **20** per side; T_idle = **150**  
- Box 80×50×50, mid=40, ports (20,25,25)/(60,25,25)  
- Time budget: estimate ~45 s; hard ceiling **120 s**

## Prediction (locked BEFORE run)

🔮 **PASS** expected: treatment ≈1.0 (ILW seeds distinct freqs per side and holds under idle as in C5/E2); control ≈0.50 (independent L/R → L cannot predict R).  
Most-likely miss: control >0.60 if decoder or RNG accidentally correlates, or treatment <0.90 if mean-freq collapses under idle/nudge.

## NOT claimed

- Learned association over many exposures without writing both sides  
- Free dual-band talent (C5 FREE still NULL)  
- Temporal order (E3 closed)  
- Brain / understanding

## RESULT

**PASS** (2026-07-20). B1_treat=**1.000**, B2_ctrl=**0.417** (≤0.60), B3_pop=**1.000**. Smoke matched full.

### Calibration
🔮 predicted PASS (treat≈1, ctrl≈0.5) — **HIT**. Write-time dual ILW freqs hold under idle; uncorrelated L/R breaks L→R rule.

### Scope (honest)
Engineered joint write preserves a 2-class opposite-band pairing. Not multi-trial learning; not free talent; not order (E3).

# BP-C7 — Attractor seeds vs scrambled seeds (free dual-band)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** C6 NULL (hybrid specs 1.0; free-only 0.778 broke ≤0.75 control)  
**Discipline:** **not** C6 B2 retune — **new control** = ILW seeds with **swapped** frequencies (wrong side)

---

## Hypothesis

**H-C7.** Under midplane + free dual-band inject:

1. **Correct seeds** (L ILW 500, R ILW 5000) then free inject → `md_L < md_R` in ≥ **0.90** of trials.  
2. **Scrambled seeds** (L ILW **5000**, R ILW **500**) then same free inject → `md_L < md_R` in ≤ **0.55** of trials (wrong attractors break or reverse decade order).  
3. Correct-seed arm both sides populated ≥ **0.80**.  
4. Correct-seed mean χ ≤ **0.15**.

If B1∧B2: attractor polarity **causally** shapes free specialisation.  
If B1 only: free field specialises regardless of seed polarity (seeds decorative).

## Bars

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Correct-seed: md_L < md_R rate | ≥ **0.90** |
| B2 | Scrambled-seed: md_L < md_R rate | ≤ **0.55** |
| B3 | Correct-seed both populated | ≥ **0.80** |
| B4 | Correct-seed mean χ | ≤ **0.15** |

## Protocol
Seeds `{751, 761, 771}`, trials 3; T=1000; N_SIDE=400; N_SEED_ILW=8; midplane ON.  
Smoke: 1×1×T=250. Budget est 20 min / hard 40 min.

## Prediction
🔮 LEAN NULL on B2: free dual-band may still push md_L < md_R even with swapped seeds (decade inject dominates).  
Most-likely miss: B2 scrambled still ≥0.90.

## NOT claimed
Pure free talent without seeds; C full reopen.

## RESULT
**NULL** (2026-07-20).

| Bar | Value | thr | ok |
|-----|------:|-----|:--:|
| B1 correct-seed | **0.778** | ≥0.90 | no |
| B2 scrambled-seed | **0.667** | ≤0.55 | no |
| B3 pop | **1.000** | ≥0.80 | yes |
| B4 χ | **0.000** | ≤0.15 | yes |

### Calibration
🔮 lean NULL on B2 — **HIT**. Scrambled seeds still specialise ~2/3 (free dual-band dominates). Correct-seed also only 0.778 (not robust 0.90). Seeds are **not** causal drivers of free specialisation under this protocol.

### Class
Attractor-seeded free talent (C6–C7) **CLOSED PARTIAL**: hybrid can hit high rates in some samples (C6 B1=1.0) but polarity control fails; free-only already strong.

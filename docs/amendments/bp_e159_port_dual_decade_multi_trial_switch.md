# BP-E159 — Port dual decade multi-trial switch (forward → reverse → forward)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E158 overwrite reverse  
**Discipline:** multi-trial dual decade content switch — last write wins after three phases

## Hypothesis
Wall ON.  
1. Write L-low R-high → ordered L < R ≥0.90  
2. Write L-high R-low → reversed L > R ≥0.80  
3. Write L-low R-high again → ordered L < R ≥0.80  

## Bars
B1 first ordered ≥0.90 · B2 reverse ≥0.80 · B3 final ordered ≥0.80  

Seeds {4221,4231} trials 8. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS. Multi-trial content switch closes dual decade reconfig.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=0.0 B3=0.0. First ordered OK; reverse and final re-forward fail. Multi-trial dual decade switch not last-write-dominant under multislot (aligns with E158).

# BP-E134 — Coincidence AND soft dual wipe → restore **L1–M only** (no M–R rewrite) → then L2

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E131 NULL (L1 restore rewrote M–R and dual came ON)  
**Discipline:** **new mechanism** = hop-scoped selective restore (L1–M only, no M–R re-ILW) after dual soft wipe

## Hypothesis
Soft dual-cut I1+I2.  
1. Dual wipe silence ≥0.80  
2. Restore **only L1–M** (no M–R link rewrite; re-arm gate only): dual still OFF ≥0.80  
3. Restore L2–M (+ optional M–R once): dual ON ≥0.80  

## Bars
B1 dual wipe silence ≥0.80 · B2 L1–M-only still silence ≥0.80 · B3 full dual ON ≥0.80  

Seeds {3641,3651} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS if E131 leak was M–R rewrite re-coupling residual L2; NULL if residual L2–M alone with intact M–R already dual-fires after L1–M restore.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=0.0 B3=1.0. Soft dual wipe + L1–M hop-only restore still dual ON. E131 leak is **not** solely M–R rewrite; residual L2–M after soft wipe suffices once L1–M is back. Hard dual wipe (E133) required for selective isolation.

# BP-E246 — Cascade reverse asymmetric retrain (replace OFF)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E234 retrain coexist equal train PASS; E244 pair_replace NULL  
**Discipline:** multi-trial reverse **asymmetric retrain** — train both; heavy retrain path0 only (3×); path1 reverse still survives. Not equal retrain re-probe; not mid-kill; replace OFF.

## Hypothesis

1. After equal train both: fire R1 → rev p1 ≥0.90  
2. After heavy retrain path0 only (3× N_TRAIN): fire R0 → rev p0 ≥0.90  
3. After heavy retrain path0: fire R1 → rev p1 still ≥0.80  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | post equal train rev p1 | ≥0.90 |
| B2 | post heavy p0 retrain rev p0 | ≥0.90 |
| B3 | post heavy p0 retrain rev p1 survives | ≥0.80 |

Seeds {7381,7391} trials 6. Budget ~22 min, hard cap 44 min.

## What is NOT claimed

Not E234 equal sequential retrain re-probe. Not pair_replace. Not free dual.

## Prediction

🔮 LEAN PASS if Y-separated reverse paths tolerate asymmetric write pressure on the other path (replace OFF).

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Heavy 3× retrain path0 (replace OFF): path0 reverse OK; path1 reverse survives. Asymmetric write pressure does not erase the other reverse path.


# BP-E234 — Cascade reverse sequential retrain coexistence (no kill)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E214 cascade reverse; E230 concurrent reverse; E178 arm switch used kill — this is **retrain-only no kill**  
**Discipline:** multi-trial dual reverse — train path0 only then path1 only without any mid-kill; both reverse paths should coexist.

## Hypothesis

Same dual L–M–R pair-link scaffold as E214.

1. Train path0 only: fire R0 → reverse p0 ≥0.90  
2. Then train path1 only (no kill): fire R1 → reverse p1 ≥0.90  
3. After path1 train (no kill): fire R0 → reverse p0 still ≥0.80  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | post p0-train rev p0 | ≥0.90 |
| B2 | post p1-train rev p1 | ≥0.90 |
| B3 | post p1-train rev p0 survives | ≥0.80 |

Seeds {7041,7051} trials 6. Budget ~20 min, hard cap 40 min.

## What is NOT claimed

Not mid-kill/restore. Not concurrent dual. Not free dual. Not split-port kill curriculum.

## Prediction

🔮 LEAN PASS if Y-separated dual paths do not overwrite each other under sequential retrain without kill.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Sequential retrain path0 then path1 without kill: both reverse paths coexist. No mid-kill required for dual reverse co-residence.


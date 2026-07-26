# BP-E230 — Cascade reverse concurrent dual R fire

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E214 cascade reverse sequential PASS; E229 incomplete-path PASS  
**Discipline:** multi-trial concurrent reverse content — both R ports driven in one prop window; both L reverse targets must light. Not mid-kill/restore.

## Hypothesis

Same dual L–M–R pair-link scaffold as E214.

1. Sequential: fire R0 alone → reverse p0 ≥0.90  
2. Sequential: fire R1 alone → reverse p1 ≥0.90  
3. Concurrent: fire R0 **and** R1 in the same prop window → both L0 and L1 peak ≥1.0 ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | sequential rev p0 | ≥0.90 |
| B2 | sequential rev p1 | ≥0.90 |
| B3 | concurrent both L peaks ≥1.0 | ≥0.70 |

Seeds {6881,6891} trials 6. Budget ~20 min, hard cap 40 min.

## Negative control

Sequential arms must pass (protocol still works). Concurrent must not collapse to single-path WTA.

## What is NOT claimed

Not mid-kill. Not G12. Not free dual. Not incomplete-path re-probe.

## Prediction

🔮 LEAN PASS if reverse paths are spatially isolated (Y-separated) and concurrent R drive does not destroy both reverse latches.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Sequential reverse both paths OK; concurrent dual R fire lights both L reverse targets. Spatially isolated reverse paths co-activate without WTA collapse. Not mid-kill.


# BP-E232 — Cascade forward concurrent dual L fire

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E214 reverse cascade; E230 concurrent reverse PASS; E186 content cascade forward  
**Discipline:** multi-trial concurrent **forward** dual fire — both L ports driven in one prop window; both R targets must light. Not mid-kill; not reverse concurrent re-probe.

## Hypothesis

Same dual L–M–R pair-link scaffold as E214 (forward direction).

1. Sequential: fire L0 alone → select R0 (R0 peak ≥1 and R0 > R1) ≥0.90  
2. Sequential: fire L1 alone → select R1 ≥0.90  
3. Concurrent: fire L0 **and** L1 in same prop window → both R0 and R1 peak ≥1.0 ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | sequential select R0 | ≥0.90 |
| B2 | sequential select R1 | ≥0.90 |
| B3 | concurrent both R peaks ≥1.0 | ≥0.70 |

Seeds {6961,6971} trials 6. Budget ~20 min, hard cap 40 min.

## What is NOT claimed

Not reverse concurrent (E230). Not mid-kill. Not free dual.

## Prediction

🔮 LEAN PASS if forward paths are as isolated under concurrent drive as reverse E230.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Sequential forward select both paths OK; concurrent dual L fire lights both R. Symmetric to reverse concurrent E230. Not mid-kill.


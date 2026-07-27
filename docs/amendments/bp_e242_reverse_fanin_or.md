# BP-E242 — Reverse fan-in OR (two R → shared M → L)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E34 forward fan-in OR PASS; E214 cascade reverse PASS  
**Discipline:** multi-trial reverse **fan-in OR** — fire R1 or R2 alone each reaches L via shared mid. Not mid-kill; not diamond re-probe.

## Hypothesis

Geometry: R1, R2 → M → L (reverse of forward fan-in L1,L2→M→R).

1. Train all hops: fire R1 → peak L ≥1.0 ≥0.80  
2. Train all hops: fire R2 → peak L ≥1.0 ≥0.80  
3. Both sequential arms succeed in same trial ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | fire R1 → L | ≥0.80 |
| B2 | fire R2 → L | ≥0.80 |
| B3 | both in same trial | ≥0.70 |

Seeds {7301,7311} trials 6. Budget ~18 min, hard cap 36 min.

## What is NOT claimed

Not forward fan-in re-probe. Not mid-kill. Not free dual. Not exclusive WTA between R1/R2.

## Prediction

🔮 LEAN PASS if reverse charge prop through shared mid works from either R input (OR).

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Reverse fan-in OR: fire R1 or R2 each reaches L via shared mid. Not mid-kill.


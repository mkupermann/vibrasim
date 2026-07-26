# BP-E243 — Reverse shared-mid crosstalk

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E33 forward shared-mid crosstalk PASS; E214 cascade reverse PASS  
**Discipline:** multi-trial reverse **shared mid leak** — separate mids isolate reverse; shared mid produces reverse crosstalk to wrong L. Not mid-kill; not diamond/fan-in re-probe.

## Hypothesis

1. **Separate mids** M1/M2: fire R1 → L1 ≥1.0 and L2 <1.0 ≥0.80  
2. **Shared mid** M: fire R1 → L1 ≥1.0 ≥0.80  
3. **Shared mid** M: fire R1 → L2 also ≥1.0 (crosstalk leak) ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | separate mids: selective rev R1→L1 not L2 | ≥0.80 |
| B2 | shared mid: fire R1 → L1 | ≥0.80 |
| B3 | shared mid: fire R1 → L2 leak | ≥0.70 |

Seeds {7321,7331} trials 6. Budget ~20 min, hard cap 40 min.

## What is NOT claimed

Not forward E33 re-probe. Not mid-kill. Not free dual. Not fan-in OR (E242).

## Prediction

🔮 LEAN PASS if reverse prop through shared mid couples both L arms like forward E33 leak.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Separate mids: reverse R1→L1 selective. Shared mid: reverse R1 reaches L1 and leaks to L2. Reverse crosstalk mirrors forward E33-class shared-mid leak.


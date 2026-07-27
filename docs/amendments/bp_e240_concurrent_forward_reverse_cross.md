# BP-E240 — Concurrent forward + reverse dual-path cross drive

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E230 concurrent reverse PASS; E232 concurrent forward PASS  
**Discipline:** multi-trial **mixed-direction concurrent** — fire L0 (forward→R0) and R1 (reverse→L1) in one prop window; both targets light. Not mid-kill; not pure concurrent reverse/forward re-probe.

## Hypothesis

Same dual L–M–R pair-link scaffold as E214 (both paths trained).

1. Concurrent fire L0 + R1: peak R0 ≥1.0 ≥0.80  
2. Concurrent fire L0 + R1: peak L1 ≥1.0 ≥0.80  
3. Both targets lit in same trial ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | concurrent R0 lit (forward p0) | ≥0.80 |
| B2 | concurrent L1 lit (reverse p1) | ≥0.80 |
| B3 | both in same trial | ≥0.70 |

Seeds {7261,7271} trials 6. Budget ~20 min, hard cap 40 min.

## What is NOT claimed

Not pure concurrent reverse (E230). Not pure concurrent forward (E232). Not mid-kill. Not free dual.

## Prediction

🔮 LEAN PASS if Y-separated paths support simultaneous opposite-direction drive without mutual erasure.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Concurrent fire L0 (forward→R0) + R1 (reverse→L1): both targets light. Mixed-direction dual-path drive coexists. Not pure concurrent re-probe.


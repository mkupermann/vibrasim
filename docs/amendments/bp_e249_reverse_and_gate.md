# BP-E249 — Reverse coincidence-AND gated R→G→L

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E61 forward AND gated relay; PRIM9 coincidence AND  
**Discipline:** multi-trial **reverse AND** — fire R alone fails reverse to L; fire R+G succeeds; fire G alone fails. Not reverse cascade dual re-probe; not mid-kill.

## Hypothesis

Geometry R–G–L. Pair-link + charge prop + coincidence_and at G (same prim as E61, reverse drive direction).

1. Fire R only → peak L <1.0 (fails) ≥0.70  
2. Fire R and G together → peak L ≥1.0 ≥0.80  
3. Fire G only → peak L <1.0 (fails) ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | fire R only fails reverse | ≥0.70 |
| B2 | fire R+G succeeds reverse | ≥0.80 |
| B3 | fire G only fails reverse | ≥0.70 |

Seeds {7441,7451} trials 6. Budget ~18 min, hard cap 36 min.

## What is NOT claimed

Not forward E61 re-probe. Not dual cascade reverse. Not free dual. Not XOR.

## Prediction

🔮 LEAN PASS if coincidence_and gates reverse prop through G like forward L→R.

## RESULT

**NULL** (2026-07-26). B1=1.0 B2=1.0 B3=0.0.  
Fire R alone fails reverse (AND-like half). Fire R+G succeeds. But fire G alone **succeeds** reverse (B3 fail) — G is sufficient; reverse is not true AND under coincidence_and + this geometry. Finding: reverse gate is G-driven, not R∧G coincidence.


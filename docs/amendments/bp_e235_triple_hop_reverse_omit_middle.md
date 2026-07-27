# BP-E235 — Triple-hop reverse incomplete omit middle M–A

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E231 triple-hop reverse PASS; E233 omit A–R PASS  
**Discipline:** multi-trial three-hop reverse **middle-hop omission** (L–M + A–R only; no M–A). Different incomplete from E233 terminal A–R omit. Full-path control must succeed.

## Hypothesis

E190/E231 L–M–A–R geometry.

1. **Incomplete** (L–M and A–R only; no M–A): fire R0 → reverse L0 **fails** ≥0.70  
2. **Incomplete**: fire R1 → reverse L1 **fails** ≥0.70  
3. **Full train control**: fire R0 → reverse L0 ≥0.80  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | incomplete rev p0 fails | ≥0.70 |
| B2 | incomplete rev p1 fails | ≥0.70 |
| B3 | full rev p0 succeeds | ≥0.80 |

Seeds {7081,7091} trials 6. Budget ~22 min, hard cap 44 min.

## What is NOT claimed

Not mid-kill. Not E233 A–R omit re-probe. Not free dual.

## Prediction

🔮 LEAN PASS if reverse chain requires continuous middle hop M–A, not just terminal A–R.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Omit middle M–A hops: reverse from R fails both paths. Full triple-hop reverse OK. Continuous middle hop required (distinct from E233 terminal A–R omit). Not mid-kill.


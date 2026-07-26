# BP-E250 — Cascade reverse bridge_prop_min_strength gate

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E214 cascade reverse; bridge_prop_min_strength used in mux/AND scaffolds  
**Discipline:** multi-trial reverse **strength gate** — high `bridge_prop_min_strength` blocks reverse prop; zero min allows reverse. Not reverse cascade topology re-probe; not mid-kill.

## Hypothesis

Same dual L–M–R scaffold as E214; train with standard writes.

1. **min_strength=0**: fire R0 → reverse p0 ≥0.90  
2. **min_strength=50** (above typical pair-link strength): fire R0 → reverse p0 **fails** ≥0.70  
3. **min_strength=0**: fire R1 → reverse p1 ≥0.80  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | min=0 rev p0 | ≥0.90 |
| B2 | min=50 rev p0 fails | ≥0.70 |
| B3 | min=0 rev p1 | ≥0.80 |

Seeds {7481,7491} trials 6. Budget ~22 min, hard cap 44 min.

## What is NOT claimed

Not free dual. Not mid-kill. Not reverse AND re-probe (E249).

## Prediction

🔮 LEAN PASS if charge prop respects min_strength and reverse needs prop through mid hops.

## RESULT

**NULL** (2026-07-26). B1=1.0 B2=0.0 B3=1.0.  
min_strength=0 reverse OK. min_strength=50 does **not** block reverse (B2=0) — trained pair-link strengths exceed 50 or reverse prop does not strictly gate on min_strength under this scaffold. Finding: pre-registered min=50 is not a reverse silencer after standard dual train.


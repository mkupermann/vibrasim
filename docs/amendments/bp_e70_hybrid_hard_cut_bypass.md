# BP-E70 — Hard-kill OR bypass of AND-OR hybrid

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E66 soft-cut bypass PASS; E65 hybrid  
**Discipline:** same hybrid geometry; **hard kill** at L3 (not soft)

## Hypothesis
AND L1/L2–M–R + OR L3–R. Hard I at L3, `fire_kill_bridge_radius=8`.
1. After kill: fire L1+L2 → R ON ≥0.90  
2. Fire L3 → R OFF ≥0.90  
3. Fire L1 alone → R OFF ≥0.90  

## Bars
B1–B3 all ≥0.90. Seeds {2061,2071} trials 8. Budget ~4 min, hard cap 8 min.

## Prediction
🔮 LEAN PASS (hard analogue of E66). Miss if hard kill at L3 also hits R and kills M–R.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard-kill L3 bypass; AND path intact; L1-only silent.

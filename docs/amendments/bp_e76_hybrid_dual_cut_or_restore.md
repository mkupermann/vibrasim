# BP-E76 — Dual soft-cut, selective OR-only restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E75 dual cut AND-only restore PASS; E72 disarm  
**Discipline:** mirror of E75 — restore **L3–R only**; AND stays OFF

## Hypothesis
1. Soft-cut L1 then L3 → both OFF ≥0.90  
2. Disarm; restore L3–R only → L3 ON ≥0.85  
3. L1+L2 still OFF ≥0.90  

## Bars
B1 both OFF ≥0.90 · B2 bypass ON ≥0.85 · B3 AND still OFF ≥0.90  

Seeds {2211,2221} trials 8. Budget ~5 min, hard cap 10 min.

## Prediction
🔮 LEAN PASS (E75 mirror). Miss if L3 restore collaterally rewrites L1–M.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual soft-cut; selective L3–R restore recovers OR only; AND stays silent.

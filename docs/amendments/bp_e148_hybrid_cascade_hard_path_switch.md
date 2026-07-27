# BP-E148 — Hybrid cascade multi-trial hard path-switch OR ↔ cascade AND ↔ OR

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E146/E147 hybrid cascade selective; E139 hard path-switch  
**Discipline:** multi-trial hard path-switch on hybrid cascade topology

## Hypothesis
Full hybrid cascade trained.  
1. Hard-cut I1 (cascade AND); restore L3–R → OR-only ≥0.80  
2. Hard-cut I3 (OR); restore cascade AND → cascade AND-only ≥0.80  
3. Hard-cut I1 again; restore L3–R → OR-only again ≥0.75  

## Bars
B1 OR-only ≥0.80 · B2 cascade AND-only ≥0.80 · B3 OR-only again ≥0.75  

Seeds {3961,3971} trials 6. Budget ~14 min, hard cap 28 min.

## Prediction
🔮 LEAN PASS. Hybrid cascade path-switch composes from E146/E147 + E139.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hybrid cascade multi-trial hard path-switch OR→cascade AND→OR closed.

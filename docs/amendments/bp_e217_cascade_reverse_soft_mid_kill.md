# BP-E217 — Cascade reverse soft mid-kill M0; reverse p1 survives

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E214–E216 cascade reverse; E189 cascade soft mid-kill forward  
**Discipline:** dual cascade train; reverse works; soft kill **M0** silences reverse p0; reverse p1 still works. New vs closed cascade reverse probes.

## Hypothesis
1. Pre: fire R0 → L0 reverse ≥0.90  
2. Soft kill M0: fire R0 → L0 reverse **fails** ≥0.70  
3. Soft kill M0: fire R1 → L1 reverse ≥0.80  

## Bars
B1 pre rev p0 ≥0.90 · B2 post soft rev p0 fail ≥0.70 · B3 rev p1 survives ≥0.80  

Seeds {6241,6251} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if soft mid-hop kill isolates reverse path0 like forward E189.

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Soft kill M0 silences reverse p0; reverse p1 survives.

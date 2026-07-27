# BP-E214 — Content cascade reverse fire-select (R→L multi-hop)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E186 cascade forward PASS; reverse pair-link native E203–E204  
**Discipline:** dual L-M-R cascade train; reverse fire R0 → L0 select; reverse fire R1 → L1 select. Not reverse soft-kill re-probe.

## Hypothesis
1. Fire R0 → L0 reverse multi-hop select ≥0.80  
2. Fire R1 → L1 reverse multi-hop select ≥0.80  
3. Both paths same world ≥0.70  

## Bars
B1 rev p0 ≥0.80 · B2 rev p1 ≥0.80 · B3 both ≥0.70  

Seeds {6121,6131} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if pair-link reverse works multi-hop like single-hop reverse (E204/E205 class).

## RESULT
**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0. Dual cascade reverse R→L multi-hop fire-select works both paths.

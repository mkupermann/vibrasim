# BP-E224 — Cascade reverse graded soft mid-kill (half vs full)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E217 full soft mid-kill PASS; E47 graded soft forward  
**Discipline:** dual cascade train; **half** soft weaken M0 keeps reverse p0; **full** soft kill M0 silences reverse p0. New graded question vs closed full-kill E217.

## Hypothesis
1. Soft mid M0 with frac=0.5: fire R0 → L0 reverse still ≥0.70  
2. Soft mid M0 with frac=1.0: fire R0 → L0 reverse **fails** ≥0.70  
3. Full soft mid M0: reverse p1 still ≥0.80  

## Bars
B1 half-keep rev p0 ≥0.70 · B2 full-fail rev p0 ≥0.70 · B3 full p1 survives ≥0.80  

Seeds {6601,6611} trials 6. Budget ~22 min, hard cap 44 min.

## Prediction
🔮 LEAN PASS if reverse graded soft matches forward E47-class graded silence.

## RESULT
**NULL** (2026-07-26). B1=0.0 B2=1.0 B3=1.0. Half soft mid-kill (frac=0.5) already silences reverse p0 (B1 fail). Full silences p0 and p1 survives. Reverse multi-hop more fragile to soft mid weaken than half-keep hypothesis; no bar retune.

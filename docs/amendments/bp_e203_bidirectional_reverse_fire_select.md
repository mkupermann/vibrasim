# BP-E203 — Bidirectional bridges reverse fire-select (G13)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E171 forward fire-select PASS; G13 bidirectional_bridges never BP port-tested  
**Discipline:** train dual ILW pair-link; treat = bidirectional_bridges + G6 bridge_atom_prop; reverse fire R→L select. Control: G6 ON but bidirectional OFF.

## Hypothesis
1. Treat: fire R-hi → L-lo select ≥0.70  
2. Treat: fire R-lo → L-hi select ≥0.70  
3. Ctrl no-bidir: fire R-hi → L-lo select **fails** ≥0.70 (not reverse-select)  

## Bars
B1 treat reverse c0 ≥0.70 · B2 treat reverse c1 ≥0.70 · B3 ctrl reverse fail ≥0.70  

Seeds {5681,5691} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if G13 bidir + G6 prop enables reverse generative recall on pair-linked arms; LEAN NULL if pair-link charge prop is one-way only and G6 insufficient.

## RESULT
**NULL** (2026-07-26). B1=1.0 B2=1.0 B3=0.0. Reverse R→L select works with treat, but **also** with ctrl (G6 ON, bidir OFF). G13 bidirectional not load-bearing for reverse fire-select under pair-link + bridge prop; reverse already available without bidir.

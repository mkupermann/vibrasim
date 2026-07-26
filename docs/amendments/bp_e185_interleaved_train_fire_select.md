# BP-E185 — Interleaved multi-trial train fire-select (c0/c1 alternate)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E171 blocked train (c0 block then c1 block) PASS  
**Discipline:** **new protocol** = alternate c0 and c1 dual pair_writes each trial (interleaved), not blocked sequential; same fire-select bars

## Hypothesis
Multislot ON, pair-link ON, shared ports.  
N_train=12 of (one dual c0 write burst; idle; one dual c1 write burst; idle) interleaved.  
1. Fire L-lo → R-hi select ≥0.80  
2. Fire L-hi → R-lo select ≥0.80  
3. Both ≥0.70  

Tests whether blocked curriculum is required or interleaved multi-trial still yields fire-select.

## Bars
B1 L-lo ≥0.80 · B2 L-hi ≥0.80 · B3 both ≥0.70  

Seeds {4981,4991} trials 8. Budget ~16 min, hard cap 32 min.

## Prediction
🔮 LEAN PASS if multislot retains both under interleaved writes (E166 capacity class). NULL if interleaving prevents stable pair-links.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Interleaved c0/c1 multi-trial train yields fire-select both arms; blocked curriculum not required.

# BP-E186 — Content+cascade hybrid multi-hop fire-select

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E171 one-hop fire-select; circuit multi-hop cascade E105+; not farming split-port kill  
**Discipline:** two spatial cascade paths L→M→R with content freqs; fire L endpoint selects R endpoint via multi-hop bridges

## Hypothesis
Path0 y=15: L0–M0–R0 freqs 400→1200→5000 (low→mid→high).  
Path1 y=35: L1–M1–R1 freqs 5000→2000→400 (high→mid→low).  
Pair-link train both cascades multi-trial.  

1. Fire L0 → peak latch R0 ≥1 and R0 > R1 ≥0.80  
2. Fire L1 → peak latch R1 ≥1 and R1 > R0 ≥0.80  
3. Both ≥0.70  

Tests multi-hop content fire-select (cascade + content bands), not one-hop residual.

## Bars
B1 path0 select ≥0.80 · B2 path1 select ≥0.80 · B3 both ≥0.70  

Seeds {5021,5031} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if cascade bridges prop charge like E150-class paths with spatial split. NULL if mid-hop fails content discrimination.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Content+cascade multi-hop fire-select: two L→M→R paths with content freqs; fire L endpoint selects correct R via multi-hop bridges.

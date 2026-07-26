# BP-E150 — Dual cascade AND paths + hard selective silence path0

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E141 cascade AND; E56 dual 3-hop hard selective  
**Discipline:** **new topology** = two parallel cascade AND chains with y-sep; hard dual-cut path0 L inputs only

## Hypothesis
Path0 y=12: (L0a∧L0b)→M0→A0→R0. Path1 y=36: (L1a∧L1b)→M1→A1→R1.  
1. Both paths dual ON (single OFF each) ≥0.80  
2. Hard-cut L0a+L0b: path0 dual OFF ∧ path1 dual ON ≥0.80  
3. Full restore path0: both dual ON ≥0.80  

## Bars
B1 both dual ON ≥0.80 · B2 selective path0 OFF path1 ON ≥0.80 · B3 restore path0 both ON ≥0.80  

Seeds {4001,4011} trials 6. Budget ~14 min, hard cap 28 min. y-sep=24 > kill r=8.

## Prediction
🔮 LEAN PASS if y-sep keeps kill local. Miss if gate/kill collaterals hit path1.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual cascade AND concurrent + hard selective path0 silence + restore closed.

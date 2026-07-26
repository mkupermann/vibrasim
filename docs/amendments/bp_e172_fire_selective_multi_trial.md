# BP-E172 — Multi-trial fire-readout selective residual (same world A→B→A)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E171 PASS fire-readout selective  
**Discipline:** one train of c0+c1; sequential fire probes L-lo, L-hi, L-lo again with charge/latch clear between; no retrain

## Hypothesis
Same train as E171 (multislot + pair-link). On **one** world:  
1. Fire L-lo → R-hi select  
2. Clear charge/latch; fire L-hi → R-lo select  
3. Clear; fire L-lo again → R-hi select  

Bars: each step ≥0.80 rate.

## Bars
B1 first L-lo ≥0.80 · B2 L-hi ≥0.80 · B3 second L-lo ≥0.80  

Seeds {4581,4591} trials 8. Budget ~16 min, hard cap 32 min.

## Prediction
🔮 LEAN PASS if E171 select is durable multi-trial without retrain. NULL if latch/state interference after first fire.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Multi-trial fire-readout select A→B→A on one world without retrain closed.

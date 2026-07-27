# BP-E184 — Fire-select durability after long idle (no retrain)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E171 fire-select PASS (immediate probe); residual/split-port families closed  
**Discipline:** multi-assoc pair-link train; **long idle T_IDLE=400** without retrain/kill; then fire-select both arms — temporal durability, not kill/restore farm

## Hypothesis
Same train as E171 (shared ports, multislot, pair-link, c0 then c1).  
Idle 400 ticks (no ILW, no fire). Clear charge/latch.  

1. Fire L-lo → R-hi select ≥0.80  
2. Fire L-hi → R-lo select ≥0.80  
3. Both on same world after idle ≥0.70  

## Bars
B1 L-lo select ≥0.80 · B2 L-hi select ≥0.80 · B3 both ≥0.70  

Seeds {4941,4951} trials 8. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN PASS if pair bridges/content persist over idle. NULL if pair_decay/structure decay erodes select.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Fire-select both arms durable after T_IDLE=400 without retrain. Pair-link multi-assoc select persists temporally.

# BP-E192 — Content cascade fire-select under graded bridge_prop_min_strength

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E186 cascade PASS with bridge_prop_min_strength=0; BET-107 graded prop  
**Discipline:** same dual cascade train as E186; **probe** with `bridge_prop_min_strength=0.5` (only strong bridges carry charge). New question: does multi-hop content fire-select survive graded gating?

## Hypothesis
Train dual L→M→R content cascades (pair-link). At probe, set bridge_prop_min_strength=0.5.  
1. Fire L0 → path0 select ≥0.80  
2. Fire L1 → path1 select ≥0.80  
3. Both ≥0.70  

## Bars
B1 path0 ≥0.80 · B2 path1 ≥0.80 · B3 both ≥0.70  

Seeds {5201,5211} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS if pair-link bridges reach ≥0.5 strength under train. NULL if graded gate silences prop.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Content cascade fire-select survives graded bridge_prop_min_strength=0.5 at probe. Pair-link bridges are strong enough for BET-107 gated multi-hop prop.

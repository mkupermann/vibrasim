# BP-E197 — Pattern-id tags load-bearing for **wrong-arm block** (not for positive select)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E194–E196 PASS; G12 allows ambient pattern_id=0 to fire  
**Discipline:** without tags all atoms stay pid=0 (ambient); with train-time tags wrong-arm is blocked

## Hypothesis
G12: ambient (pid=0) and matching pid fire; only **non-zero mismatched** pid is suppressed.  

1. **No-tag** train (active_pattern_id=0 always): gate active=1, fire L-lo → R-hi select **succeeds** ≥0.80 (ambient E171 path)  
2. **Tagged** train (E196 style): gate active=1, fire L-hi → R-lo select **fails** ≥0.70 (wrong-arm blocked)  
3. **No-tag**: gate active=1, fire L-hi → R-lo select **succeeds** ≥0.70 (wrong arm not blocked without tags)  

## Bars
B1 no-tag correct select ≥0.80 · B2 tagged wrong-arm fail ≥0.70 · B3 no-tag wrong-arm still selects ≥0.70  

Seeds {5441,5451} trials 8. Budget ~18 min, hard cap 36 min.

## Prediction
🔮 LEAN PASS. Tags required for wrong-pattern suppression; positive select works with ambient-only.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. Without tags, ambient atoms fire under gate (positive select + wrong-arm select both work). With train-time tags, wrong-arm is blocked. **Tags are load-bearing for wrong-pattern suppression**, not for positive fire-select.

# BP-E67 — Soft 2×2 concurrent dual-drive under identity

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E59 soft 2×2 PASS (sequential probe)  
**Discipline:** not E59 retune — **simultaneous** fire L0+L1 under identity select

## Hypothesis
Same four arms as E59. Soft-select identity (keep 00+11).  
In one phase fire **both** L0 and L1 concurrently: R0 and R1 both ON; under swap residual should not light (identity only).

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Concurrent: R0 ON and R1 ON | ≥0.80 |
| B2 | After same phase, no false swap (already both ON is fine; check sequential off-path) | ≥0.80 |
| B3 | Under identity, single L0 still only R0 (no R1) | ≥0.80 |

Actually B2: concurrent identity both R ON; B3: single L0 only R0 after concurrent (path isolation). Simplify:

1. Identity select → concurrent L0+L1 → R0≥1 and R1≥1 ≥0.80  
2. Identity select → L0 only → R0 ON R1 OFF ≥0.80  
3. Identity select → L1 only → R1 ON R0 OFF ≥0.80  

## Bars
B1 concurrent both ≥0.80 · B2 L0 only ≥0.80 · B3 L1 only ≥0.80  

Seeds {1971,1981} trials 6. Budget ~6 min, hard cap 12 min.

## Prediction
🔮 LEAN PASS. Miss if concurrent charge crosstalk lights wrong R.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Concurrent L0+L1 under identity lights both R; single-L isolation holds.

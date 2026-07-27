# BP-E160 — Port dual decade reverse overwrite with **multislot OFF**

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E158 NULL (reverse under multislot ON); E6 last-content  
**Discipline:** **new mechanism class** = multislot OFF for last-write dual decade reconfig — not bar retune of E158

## Hypothesis
Same protocol as E158 but `ilw_multislot_enabled=False`.  
1. After L-low R-high: ordered L < R ≥0.90  
2. After reverse L-high R-low: reversed L > R ≥0.80  
3. Pop after reverse ≥0.90  

## Bars
B1 first ordered ≥0.90 · B2 reverse ≥0.80 · B3 pop ≥0.90  

Seeds {4241,4251} trials 8. Budget ~6 min, hard cap 12 min.

## Prediction
🔮 LEAN PASS. Without multislot, last write replaces prior band content (E6-like).

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Multislot OFF: reverse overwrite flips dual decade means. Multislot ON (E158) blocked last-write reconfig; OFF enables it.

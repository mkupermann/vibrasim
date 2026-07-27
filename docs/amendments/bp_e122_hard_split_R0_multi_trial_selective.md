# BP-E122 — Hard split R0 multi-trial selective: hard silence both → soft restore 00 → hard re-cut 00

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E121 PASS (soft multi-trial selective); E120 PASS (hard silence + soft restore)  
**Discipline:** hard multi-trial L-selective cycle on non-shared R0a/R0b

## Hypothesis
Split topology E119. Soft dual-cut all; restore all.  
1. Hard-cut 00+10 → both silent, R1 ON ≥0.80  
2. Soft restore only 00 → L0 fanout; L1 R0b OFF ≥0.80  
3. Hard re-cut only 00 → L0 R0a OFF R1 ON; L1 R0b still OFF ≥0.80  

## Bars
B1 hard dual silence ≥0.80 · B2 selective soft restore ≥0.80 · B3 hard selective re-cut ≥0.80  

Seeds {3361,3371} trials 6. Budget ~12 min, hard cap 24 min.

## Prediction
🔮 LEAN PASS. Hard analogue of E121 multi-trial selective.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Hard multi-trial selective on split R0 closed. Soft (E121) + hard (E122) multi-trial L-selective reconfig complete.

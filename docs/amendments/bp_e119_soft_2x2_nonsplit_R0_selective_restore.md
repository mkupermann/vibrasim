# BP-E119 — Soft 2×2 with split R0 (non-shared) + selective restore 00 only

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E110 NULL (shared R0 selective leak); E112 dual-restore doctrine  
**Discipline:** **new topology** — separate R0a/R0b endpoints for arms 00/10 (not shared bipartite R0). Tests whether selective restore becomes L-selective when endpoints are not shared.

## Hypothesis
Arms: 00 L0→R0a, 01 L0→R1, 10 L1→R0b, 11 L1→R1. R0a≠R0b (y-sep large).  
Soft dual-cut all; restore all; soft-cut 00+10; restore **only 00**.
1. After dual-cut: L0→R0a OFF ∧ R1 ON; L1→R0b OFF ∧ R1 ON ≥0.80  
2. After restore 00: L0→R0a ON ∧ R1 ON ≥0.80  
3. After restore 00: L1→R0b OFF ∧ R1 ON ≥0.80  

## Bars
B1 silence ≥0.80 · B2 L0 fanout (R0a+R1) ≥0.80 · B3 L1 R0b still OFF ≥0.80  

Seeds {3301,3311} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS if shared endpoint was the E110 leak cause; NULL if ILW restore still cross-talks via mids/L.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Split non-shared R0a/R0b: selective restore 00 revives L0→R0a without reviving L1→R0b. **Shared endpoint was the E110 leak cause**; non-shared endpoints allow L-selective restore.

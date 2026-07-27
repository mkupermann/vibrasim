# BP-E111 — Soft 2×2 identity-diag cut then selective restore arm 00 only

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E105 PASS (identity diag → pure swap); E110 selective restore class  
**Discipline:** partial restore after diagonal routing — not full restore, not free talent

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all; soft-cut 00+11 (identity diag → pure swap).  
Then restore **only arm 00**.
1. After diag cut: L0 → R1 ON R0 OFF ≥0.80 (swap)  
2. After restore 00: L0 → R0 ON ∧ R1 ON ≥0.80 (fanout)  
3. After restore 00: L1 → R0 ON R1 OFF ≥0.80 (still pure swap)  

## Bars
B1 L0 swap ≥0.80 · B2 L0 fanout ≥0.80 · B3 L1 still swap ≥0.80  

Seeds {3141,3151} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. Single cut-arm restore reopens one identity path without reopening L1 identity (11 still cut).

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=1.0 B3=0.0. Diag cut pure swap OK; restore 00 reopens L0 fanout **but breaks L1 pure-swap isolation** (same shared-endpoint selective-restore leak class as E110).

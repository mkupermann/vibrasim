# BP-E110 — Soft 2×2 full restore, dual-cut R0 in-edges, selective restore 00 only

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E104 PASS (cut both into R0 after full restore)  
**Discipline:** new step beyond diagonal matrix — **selective single-arm restore** after shared-endpoint silence

## Hypothesis
Wide 2×2. Soft dual-cut all; restore all; soft-cut 00+10 (silence R0 for all L).  
Then restore **only arm 00** (disarm first).
1. After R0 dual-cut: L0 and L1 → R0 OFF ∧ R1 ON ≥0.80  
2. After restore 00: L0 → R0 ON ∧ R1 ON ≥0.80  
3. After restore 00: L1 → R0 OFF ∧ R1 ON ≥0.80  

## Bars
B1 post-cut silence ≥0.80 · B2 L0 fanout restored ≥0.80 · B3 L1 still R0-silent ≥0.80  

Seeds {3121,3131} trials 6. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS. E79/E80 selective restore class; shared R0 + one in-edge only.

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=1.0 B3=0.0. Dual-cut silences R0; restore 00 revives L0 fanout **and** L1→R0 (shared-endpoint selective restore leak).

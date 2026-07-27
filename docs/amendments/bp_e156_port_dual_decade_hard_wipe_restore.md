# BP-E156 — Port dual decade hard kill wipe + ILW restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E154 PASS; E155 NULL (soft wipe does not disrupt)  
**Discipline:** hard kill at L/R ports after dual decade write; re-ILW restore — hard content wipe analogue of E155

## Hypothesis
Wall ON. Hard dual-cut kill emitters at L and R ports after dual decade write.  
1. After initial write: ordered ≥0.90  
2. After hard dual wipe + idle: ordered fails (disruption) ≥0.70 of trials  
3. After re-ILW restore: ordered ≥0.90  

## Bars
B1 initial ordered ≥0.90 · B2 post-hard-wipe disruption ≥0.70 · B3 restore ordered ≥0.90  

Seeds {4161,4171} trials 8. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS. Hard kill should clear local decade structure where soft weaken failed (E155).

## RESULT
**NULL** (2026-07-20). B1=1.0 B2=0.0 B3=1.0. Hard kill at L/R ports also fails to disrupt dual decade specialisation. Soft (E155) and hard (E156) port kill/weaken do not content-wipe decade structure.

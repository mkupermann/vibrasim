# BP-E77 — Dual soft-cut then full restore AND + OR

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E75/E76 selective restores  
**Discipline:** dual soft-cut; disarm; restore **L1–M then L3–R**; both paths ON

## Hypothesis
1. Soft-cut L1+L3 → both OFF ≥0.90  
2. Disarm; restore L1–M then L3–R → L1+L2 ON and L3 ON ≥0.85  
3. L1-only still OFF ≥0.90 (AND still gated)  

## Bars
B1 both OFF ≥0.90 · B2 both ON after full restore ≥0.85 · B3 L1-only OFF ≥0.90  

Seeds {2231,2241} trials 8. Budget ~5 min, hard cap 10 min.

## Prediction
🔮 LEAN PASS. Miss if sequential restore order matters or residual state blocks second arm.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Dual soft-cut then full L1–M + L3–R restore recovers both; L1-only remains gated.

# BP-E47 — Soft partial weaken attenuates (not kills) path

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E44 full weaken (frac=1) silence PASS  
**Discipline:** new question = **graded** inhibit (frac=0.5), not silence retune

## Hypothesis
L–M–R; I near M with `fire_weaken_bridge_frac=0.5`, prop_min=0.5 so half-strength still may prop if strength was ≥1 (pair delta accumulates).  
Initial bridge strength after train ~12; after one I-fire *0.5 → ~6 still >0.5 → R still ON.  
After **many** I-fires until strength < prop_min, R OFF.

Simpler graded bars:
| ID | Criterion | thr |
|----|-----------|-----|
| B1 | After train, fire L: end R ≥1.0 | ≥0.90 |
| B2 | After **one** I-fire (frac=0.5), fire L: end R ≥1.0 still (attenuated not silent) | ≥0.85 |
| B3 | After I-fires until max bridge strength < prop_min (or 8 I phases), fire L: end R ≤0.25 | ≥0.85 |

Seeds {1461,1471} trials 8.

## Prediction
🔮 PASS lean: one half-weaken keeps path; repeated weaken silences.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=1.0 B3=1.0. One half-weaken keeps path; repeated weaken silences.

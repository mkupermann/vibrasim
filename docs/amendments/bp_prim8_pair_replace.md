# PRIM8 — Exclusive pair-link replace (forget old partner)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E27 NULL (maps coexist under PRIM5 add-only links)

## Primitive
`ilw_pair_replace_enabled: bool = False` (default OFF)

When enabled, after `apply_ilw_pair_write` forms/strengthens bridge (i,j):
- Kill all **other** alive bridges that touch atom **i** (except partner j)
- Kill all **other** alive bridges that touch atom **j** (except partner i)

Honest engineered forget for curriculum relearning. Bond counts best-effort.

## PRIM8-D0 bars
| ID | Criterion | thr |
|----|-----------|-----|
| R1 | After two pair_writes MapA then MapB on same L slot (single y): n_cross bridges == 1 in ≥0.90 trials | ≥0.90 |
| R2 | replace OFF: n_cross ≥ 2 in ≥0.80 trials (add-only) | ≥0.80 |
| R3 | replace ON: endpoint pair nearest Map B not Map A ≥0.85 | ≥0.85 |

Seeds {891,901} trials 8. Smoke 1×3.

## Prediction
🔮 PASS — kill-other is mechanical.

## RESULT
### PRIM8-D0 **PASS** (2026-07-20)
R1=1.0 R2=1.0 R3=1.0. Replace leaves one bridge; add-only multi; endpoints Map B.

# BP-C88 — Free dual talent with bistable_drive_mode (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C87; C60 bistable_rate NULL; C45 rectified NULL; `bistable_drive_mode` never BP free dual  
**Discipline:** **new mechanism** = bistable_rate ON + drive_mode absolute vs relative free dual + wall. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON. Both arms `bistable_rate=0.05`.  
Treatment: `bistable_drive_mode="absolute"`.  
Control: `bistable_drive_mode="relative"` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7101,7111} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Absolute vs relative drive mode unlikely to create free dual decade specialisation alone.

## RESULT

**NULL** (2026-07-26). B1=0.25 B2=0.50 B3=0.25 B4=-0.25.  
`bistable_drive_mode=absolute` vs relative (rate=0.05 both) does not unlock free dual talent.


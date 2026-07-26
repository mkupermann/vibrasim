# BP-C102 — Free dual talent with video_emit_pair_band (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C101; C99 audio_emit_pair_band NULL; `video_emit_pair_band` never BP free dual  
**Discipline:** **new mechanism** = video_emit_pair_band >0 free dual + wall vs 0. Budget-fit T=500 N=250. n_emit=0. Video IO off (likely no-op).

## Hypothesis

Wall ON. Neuron dynamics ON.  
Treatment: free dual L-low R-high with `video_emit_pair_band=0.15`.  
Control: `video_emit_pair_band=0.0` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7861,7871} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Without video_io, pair-band is likely no-op on free dual inject.

## RESULT

**NULL** (2026-07-26). B1=0.25 B2=0.50 B3=0.25 B4=-0.25.  
`video_emit_pair_band=0.15` does not unlock free dual talent (likely no-op without video_io).


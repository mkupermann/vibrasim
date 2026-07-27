# BP-C99 — Free dual talent with audio_emit_pair_band (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C98; `audio_emit_pair_band` never BP free dual  
**Discipline:** **new mechanism** = audio_emit_pair_band >0 free dual + wall vs 0. Budget-fit T=500 N=250. n_emit=0. Audio IO off (band may no-op without audio — honest null possible).

## Hypothesis

Wall ON. Neuron dynamics ON.  
Treatment: free dual L-low R-high with `audio_emit_pair_band=0.15`.  
Control: `audio_emit_pair_band=0.0` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7741,7751} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Without audio_io_enabled, pair-band is likely no-op on free dual inject path.

## RESULT

**NULL** (2026-07-26). B1=0.25 B2=0.25 B3=0.25 B4=0.0.  
`audio_emit_pair_band=0.15` does not unlock free dual talent (likely no-op without audio_io).


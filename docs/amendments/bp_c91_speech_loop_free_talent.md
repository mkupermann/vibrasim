# BP-C91 — Free dual talent with speech_loop_strength (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C90; `speech_loop_strength` never BP free dual  
**Discipline:** **new mechanism** = speech_loop_strength >0 free dual + wall vs off. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON.  
Treatment: free dual L-low R-high with `speech_loop_strength=1.0`.  
Control: `speech_loop_strength=0.0` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7221,7231} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Speech-loop coupling is audio-path oriented; free dual inject unlikely to unlock decade order.

## RESULT

**NULL** (2026-07-26). B1=0.50 B2=0.75 B3=0.50 B4=-0.25.  
`speech_loop_strength=1.0` does not unlock free dual talent.


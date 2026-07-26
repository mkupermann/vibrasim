# BP-C92 — Free dual talent with emit_freq (n_emit=2 budget-safe)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C91; C80 emit_band_ratios FAILED hard-cap at n_emit=8; `emit_freq` never BP free dual  
**Discipline:** **new mechanism** = elevated emit_freq under n_emit=2 free dual + wall vs default emit_freq. Budget-fit T=400 N=200 (smaller than C80 to stay under hard cap).

## Hypothesis

Wall ON. Neuron dynamics ON. Both arms `n_emit=2`.  
Treatment: `emit_freq=80000.0` (high emit carrier).  
Control: `emit_freq=30000.0` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7461,7471} trials 2. T=400 N=200. Budget ~10 min, hard cap 20 min.

## Prediction

🔮 LEAN NULL. Emit freq under n_emit=2 unlikely to unlock decade specialisation; inject still dominates.

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=0.0 B3=0.0 B4=0.0.  
`emit_freq=80000` vs 30000 under n_emit=2 free dual: no unlock; treat pop collapsed. Budget finished cleanly (vs C80 hard-cap).


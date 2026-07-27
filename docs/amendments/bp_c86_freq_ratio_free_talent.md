# BP-C86 — Free dual talent with freq_ratio (never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C85; C36 freq_tolerance; C42 wide freq_tol fragile; `freq_ratio` never BP free dual  
**Discipline:** **new mechanism** = elevated `freq_ratio` free dual + wall vs default 0.08. Budget-fit T=500 N=250. n_emit=0.

## Hypothesis

Wall ON. Neuron dynamics ON.  
Treatment: free dual L-low R-high with `freq_ratio=0.25` (looser harmonic/ratio matching band).  
Control: `freq_ratio=0.08` (default).

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | treat ordered fraction | ≥0.90 |
| B2 | ctrl ordered fraction | ≤0.80 |
| B3 | treat dual-side L4+ pop | ≥0.80 |
| B4 | B1−B2 | ≥0.15 |

Seeds {7021,7031} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction

🔮 LEAN NULL. Wider freq_ratio may increase binding noise rather than decade specialisation; not C42 retune (different knob).

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=0.50 B3=0.0 B4=-0.50.  
Elevated `freq_ratio=0.25` does not unlock free dual talent; treat pop collapses.


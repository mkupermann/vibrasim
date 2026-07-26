# BP-C36 — Free dual talent with tighter freq_tolerance (new mechanism)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** C16 CLOSED PARTIAL; C27–C35 NULL families  
**Discipline:** **new mechanism** = tighter `freq_tolerance=0.01` (stricter band matching) free dual + wall vs default 0.03. Budget-fit T=500 N=250.

## Hypothesis
Wall ON. Treatment: free dual L-low R-high with `freq_tolerance=0.01`.  
Control: same inject `freq_tolerance=0.03`.  

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars
B1–B4. Seeds {4961,4971} trials 2. T=500. Budget ~6 min, hard cap 12 min.

## Prediction
🔮 LEAN NULL. Tighter tolerance may reduce binding/pop more than it unlocks ordered talent.

## RESULT
**NULL** (2026-07-26). B1=0.0 B2=0.25 B3=0.0 B4=-0.25. Tighter freq_tolerance collapses treat population; does not unlock free dual ordered talent.

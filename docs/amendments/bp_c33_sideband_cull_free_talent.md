# BP-C33 — Free dual talent with PRIM7 midplane sideband cull (new mechanism)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** C16 CLOSED PARTIAL; wall required C20; sideband cull never tried in free dual C family  
**Discipline:** **new mechanism** = `midplane_sideband_cull_enabled=True` (PRIM7 spectral purification) during free dual + wall vs cull OFF. Budget-fit T=500 N=250.

## Hypothesis
Wall ON. Treatment: free dual L-low R-high with midplane_sideband_cull ON (wrong-side free vibs absorbed by band).  
Control: same inject cull OFF.  

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars
B1–B4. Seeds {4841,4851} trials 2. T=500. Budget ~6 min, hard cap 12 min.

## Prediction
🔮 LEAN PASS if PRIM7 enforces L-low/R-high free vib geography enough for ordered talent unlock. NULL if cull kills population or ordered still fails.

## RESULT
**NULL** (2026-07-26). B1=0.0 B2=0.25 B3=0.0 B4=-0.25. PRIM7 sideband cull collapses treat population (over-purification); does not unlock free dual ordered talent.

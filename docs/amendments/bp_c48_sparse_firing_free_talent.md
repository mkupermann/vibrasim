# BP-C48 — Free dual talent with sparse_firing_enabled (new mechanism)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C47; G11 sparse_firing never used in BP free dual  
**Discipline:** **new mechanism** = `sparse_firing_enabled=True` (per-port top-K fire) free dual + wall vs off. Budget-fit T=500 N=250.

## Hypothesis
Wall ON. Neuron dynamics ON. Treatment: free dual L-low R-high with sparse_firing_enabled, top_k=3.  
Control: sparse_firing_enabled=False.  

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars
B1–B4. Seeds {5541,5551} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN NULL. Sparse firing without named audio/video ports may no-op or fail to unlock ordered talent.

## RESULT
**NULL** (2026-07-26). B1=0.0 B2=0.75 B3=0.0 B4=-0.75. sparse_firing_enabled top_k=3 collapses treat pop (B3=0); does not unlock ordered free dual talent. Control still partial-spec without unlock.

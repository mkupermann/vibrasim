# BP-C30 — Free dual talent with elevated atom_repulsion_k (new mechanism)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** C16 CLOSED PARTIAL; C29 asymmetric speed NULL  
**Discipline:** **new mechanism** = `atom_repulsion_k>0` (inter-atom repulsion) during free dual + wall vs default 0. Budget-fit T=500 N=250.

## Hypothesis
Wall ON. Treatment: free dual L-low R-high with `atom_repulsion_k=20`.  
Control: same inject with `atom_repulsion_k=0`.  

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars
B1–B4 as above. Seeds {4681,4691} trials 2. T=500. N_SIDE=250. Budget ~6 min, hard cap 12 min.

## Prediction
🔮 LEAN NULL. Atom repulsion unlikely to unlock free dual ordered talent.

## RESULT
**NULL** (2026-07-26). B1=0.25 B2=0.50 B3=0.25 B4=-0.25. Elevated atom_repulsion_k hurts vs control; no free dual unlock.

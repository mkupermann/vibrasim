# BP-C55 — Free dual talent with stdp_alignment_strict_threshold (G8.2, never tried)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** free dual NULL farm C27–C54; C12 STDP NULL; stdp_alignment_strict never BP free dual  
**Discipline:** **new mechanism** = `stdp_alignment_strict_threshold=0.95` + stdp free dual + wall vs stdp-only (threshold 0). Budget-fit T=500 N=250.

## Hypothesis
Wall ON. Neuron dynamics ON. STDP ON both.  
Treatment: stdp_alignment_strict_threshold=0.95. Control: threshold=0.  

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars
B1–B4. Seeds {5821,5831} trials 2. T=500. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN NULL. Strict orientation alignment filters STDP; free dual inject unlikely to unlock decade order.

## RESULT
**NULL** (2026-07-26). B1=0.0 B2=0.5 B3=0.0 B4=-0.5. stdp_alignment_strict_threshold=0.95 collapses treat pop; does not unlock free dual talent.

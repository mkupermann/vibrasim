# BP-C69 — Replicate C68 node_freq_binding OFF free dual (larger N)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** C68 PASS* budget-fit; C42→C43 fragile lesson  
**Discipline:** **honest replicate** — same bars as C68 (0.90/0.80/0.80/0.15), same protocol, larger seed×trial set. No bar retune. Defend or falsify C68.

## Hypothesis
Wall ON. Treatment: free dual L-low R-high with `node_freq_binding=False`.  
Control: `node_freq_binding=True`.  

B1 treat ordered ≥0.90 · B2 ctrl ≤0.80 · B3 treat pop ≥0.80 · B4 delta ≥0.15

## Bars
B1–B4 (identical to C68). Seeds {6361,6371,6381,6391,6401} trials 3. T=500 N=250. Budget ~25 min, hard cap 50 min.

## Prediction
🔮 LEAN NULL (C42-class): budget-fit PASS often fails larger-N; B1 may land 0.6–0.8. If B1≥0.90 still, C68 class is more robust than C42.

## RESULT
**NULL** (2026-07-26). B1=0.80 B2=0.20 B3=1.0 B4=0.60 (n=15).  
Larger-N falsifies C68 budget-fit unlock (B1 fails 0.90). Strong positive delta remains. **C68 fragile** (C42-class). No bar retune.

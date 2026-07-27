# BP-E157 — Port multislot K=3 dual-side band occupancy

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E10 multiset L-only; E5 K=3 storage; E154 dual decade  
**Discipline:** multislot holds **three** frequency bands on **both** L and R after sequential ILW — capacity, not free talent

## Hypothesis
Wall ON, multislot ON. Sequential ILW three bands on L and three on R (distinct f sets).  
1. Treatment multislot ON: fraction of trials where all 3 L bins and all 3 R bins occupied ≥0.80  
2. Control multislot OFF: all-6 occupancy ≤0.20  
3. Treatment both sides populated ≥0.90  

Bands L: {400, 1500, 5000}; R: {600, 2000, 7000}. Occupancy = nearest-centroid bin has ≥1 level≥4 node within half.

## Bars
B1 treat all-six occupancy ≥0.80 · B2 ctrl all-six ≤0.20 · B3 treat pop both sides ≥0.90  

Seeds {4181,4191} trials 8. N_write=8 per band. Budget ~8 min, hard cap 16 min.

## Prediction
🔮 LEAN PASS. Multislot dual-side extends E10 to both halves.

## RESULT
**PASS** (2026-07-20). B1=1.0 B2=0.0 B3=1.0. Multislot ON holds K=3 bands on both L and R; legacy OFF fails all-six occupancy.

# BP-E163 — Multi-association last-write residual (c0→c1, multislot OFF)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E162 residual co-presence; E160/E161 multislot OFF last-write reconfig  
**Discipline:** train two associations sequentially; probe last association residual without baked map

## Hypothesis
Multislot OFF.  
c0: L=500, R=5000 · c1: L=5000, R=500 (swapped).  

**Treatment:** N_train=12 dual c0, then N_train=12 dual c1; L-only rewrite at c1 L (5000).  
**Control:** N_train=12 dual c0 only; L-only rewrite at 5000 (no c1 train).  

1. Treatment: R residual **low** (c1 partner) ≥0.80  
2. Treatment: L mean **high** ≥0.90  
3. Control: R residual **not** low (no spurious c1) ≥0.80  

Tests whether last-write association residual dominates after multi-assoc switch (E160/E161 doctrine applied to residual, not mean decades alone).

## Bars
B1 treat R low ≥0.80 · B2 treat L high ≥0.90 · B3 ctrl R not low ≥0.80  

Seeds {4381,4391} trials 8. Budget ~10 min, hard cap 20 min.

## Prediction
🔮 LEAN PASS if multislot OFF last-write reconfig extends to residual co-presence. NULL if c0 residual bleeds into c1 probe.

## RESULT
**PASS** (2026-07-26). B1=B2=B3=1.0. After c0→c1 multi-trial switch, L-only at c1 L yields R-low residual (c1); control c0-only does not spuriously produce c1 residual. Last-write residual reconfig under multislot OFF (extends E160/E161 + E162).

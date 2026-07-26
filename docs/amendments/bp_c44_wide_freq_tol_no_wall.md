# BP-C44 — Wider freq_tolerance free dual requires midplane wall (ablation)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** C42/C43 wide freq_tol unlock; C20 strength-decay needs wall  
**Discipline:** treatment = freq_tol=0.08 **wall ON**; control = freq_tol=0.08 **wall OFF**. Same inject. Tests whether C42 unlock is wall-dependent (like C20).

## Hypothesis
Both arms use freq_tolerance=0.08.  
1. Wall ON ordered ≥0.90  
2. Wall OFF ordered ≤0.80  
3. Wall ON pop ≥0.80  
4. Delta (ON−OFF) ≥0.15  

## Bars
B1 wall_on ordered ≥0.90 · B2 wall_off ordered ≤0.80 · B3 wall_on pop ≥0.80 · B4 delta ≥0.15  

Seeds {5331,5341,5351} trials 3. T=500. N_SIDE=250. Budget ~12 min, hard cap 24 min.

## Prediction
🔮 LEAN PASS if wall is required for dual-side specialisation under wide tol (C20 class). NULL if wide tol alone suffices without wall.

## RESULT
**NULL** (2026-07-26). B1=0.6667 B2=0.3333 B3=1.0 B4=0.333. Wall ON beats OFF (delta OK) but wall ON ordered still fails ≥0.90 unlock bar (aligns with C43). Wide freq_tol free dual remains fragile; wall helps but does not lock 0.90.

# BP-E31 — Parallel path isolation without pair-replace

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E30 NULL (replace destroys multi-hop)  
**Not** E30 bar retune — **replace OFF** required for multi-hop (new mechanism condition)

## Hypothesis
Same dual chains as E30 with `ilw_pair_replace_enabled=False`. Fire L1 → R1 peak≥1.0 and R2≤0.25 ≥0.85; fire both L → both R ≥1.0 ≥0.80; ≥4 bridges ≥0.90.

## Bars
Same thr as E30 B1–B4.

Seeds {1001,1011} trials 10.

## Prediction
🔮 PASS — E29 two-hop works without replace; isolation should hold.

## RESULT
*(after)*

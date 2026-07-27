# BP-E252 — Multi-trial map curriculum A→B with ilw_strength_decay only

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E28 pair_replace curriculum PASS; E27 overwrite without replace NULL; C16 strength_decay free dual PARTIAL  
**Discipline:** multi-trial **port map curriculum** — train MAP_A then MAP_B with `ilw_strength_decay_tau>0` and **pair_replace OFF**. Last map B matches; residual A low. Not reverse cascade; not residual kill farm; not E28 replace re-probe.

## Hypothesis

Dual y-slot L–R ports, pair-link multislot, charge prop + latch. `ilw_pair_replace_enabled=False`, `ilw_strength_decay_tau=30`.

1. After A→B train: match rate on MAP_B ≥0.85  
2. After A→B train: residual match on MAP_A ≤0.25  
3. A-only control (no B): match MAP_A ≥0.85  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | match B after A→B | ≥0.85 |
| B2 | residual A after A→B | ≤0.25 |
| B3 | A-only match A | ≥0.85 |

Seeds {7561,7571} trials 8. Budget ~20 min, hard cap 40 min.

## What is NOT claimed

Not free dual unlock. Not pair_replace. Not reverse cascade. Not residual soft/hard kill.

## Prediction

🔮 LEAN NULL if strength decay alone does not forget A (E27-class residual without replace) — decay may be too slow over curriculum gap.

## RESULT

**NULL** (2026-07-26). B1=0.50 B2=0.50 B3=1.0.  
Strength decay alone (replace OFF) does not cleanly switch A→B: B match and residual A both ~0.50 (50/50 residual). A-only control OK. Confirms E27-class: without replace, curriculum leaves residual — strength decay τ=30 insufficient forget mechanism over curriculum gap.


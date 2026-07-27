# BP-E256 — Dual decade multi-trial co-residence after temporal gap

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E20 peak partner; E166 multislot residual capacity; E163 last-write residual  
**Discipline:** multi-trial **temporal-gap dual decade switch/co-residence** — train pair A, long gap, train pair B on same L–R ports (multislot ON, replace OFF); both selective partners still work. Not residual kill farm; not reverse cascade; not Y-separated dual pair re-probe (E253–E255).

## Hypothesis

Shared midplane L–R ports. Pair-link multislot. Train MAP_A (400↔7000), idle T_GAP=200, train MAP_B (1500↔2500).

1. Fire L@400 → peak partner closer to 7000 than 2500 ≥0.80  
2. Fire L@1500 → peak partner closer to 2500 than 7000 ≥0.80  
3. Both selective in same trial ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | A partner selective after gap+B | ≥0.80 |
| B2 | B partner selective after gap+B | ≥0.80 |
| B3 | both in same trial | ≥0.70 |

Seeds {7721,7731} trials 6. Budget ~20 min, hard cap 40 min.

## What is NOT claimed

Not soft/hard residual kill. Not free dual. Not reverse cascade. Not E255 long idle Y-pairs.

## Prediction

🔮 LEAN PASS if multislot co-resides both pair-links across temporal gap without replace.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Train A, temporal gap, train B on shared L–R ports: both pair decades remain selectively recallable. Multislot co-residence across gap without replace/kill.


# BP-E253 — Concurrent dual pair-link selective recall

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E16 selective recall; E20 peak partner; E11 dual pairs  
**Discipline:** multi-trial **port concurrent dual recall** — train two exclusive L–R pairs on Y-slots; fire both L concurrently; both correct R partners light. Not reverse cascade; not residual kill farm; not curriculum residual re-probe (E252).

## Hypothesis

Two Y-separated L–R ports, pair-link multislot, charge prop + latch.

1. After dual train: concurrent fire L0+L1 → peak R0 ≥1.0 ≥0.80  
2. Concurrent fire L0+L1 → peak R1 ≥1.0 ≥0.80  
3. Both R lit in same trial ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | concurrent R0 lit | ≥0.80 |
| B2 | concurrent R1 lit | ≥0.80 |
| B3 | both in same trial | ≥0.70 |

Seeds {7601,7611} trials 6. Budget ~18 min, hard cap 36 min.

## What is NOT claimed

Not reverse cascade concurrent. Not free dual. Not residual A→B curriculum.

## Prediction

🔮 LEAN PASS if Y-separated pair-links support concurrent dual L drive without WTA collapse.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Concurrent fire both L ports lights both correct R partners. Dual pair-link concurrent recall works under Y-separation. Not reverse cascade.


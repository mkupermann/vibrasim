# BP-E257 — Multislot OFF last-write residual after temporal gap

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E256 multislot ON co-residence PASS; E163 last-write residual; E27 residual without replace  
**Discipline:** multi-trial **shared-port dual decade** — train A, gap, train B with **multislot OFF**; A residual fails; B selective succeeds. Not soft/hard residual kill; not reverse cascade; not E256 re-probe (opposite multislot).

## Hypothesis

Shared L–R ports. `ilw_multislot_enabled=False`, pair-link ON. Train A (400↔7000), idle T_GAP=200, train B (1500↔2500).

1. Fire L@400 → A partner selective **fails** ≥0.70  
2. Fire L@1500 → B partner selective ≥0.80  
3. A-only control (no B train): A partner selective ≥0.80  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | A residual fails after gap+B | ≥0.70 |
| B2 | B selective after gap+B | ≥0.80 |
| B3 | A-only selective A | ≥0.80 |

Seeds {7761,7771} trials 6. Budget ~20 min, hard cap 40 min.

## What is NOT claimed

Not residual kill. Not free dual. Not multislot ON co-residence re-probe.

## Prediction

🔮 LEAN PASS if multislot OFF forces last-write overwrite of pair-link (unlike E256 ON co-residence).

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Multislot OFF: train A, gap, train B → A residual fails; B selective; A-only OK. Last-write residual without kill when multislot OFF (contrasts E256 ON co-residence).


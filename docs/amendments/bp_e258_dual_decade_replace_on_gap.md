# BP-E258 — Dual decade temporal gap with pair_replace ON (last-write)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E256 multislot ON co-residence PASS; E257 multislot OFF last-write PASS; E28 replace curriculum  
**Discipline:** multi-trial **shared-port dual decade** — train A, gap, train B with **multislot ON + pair_replace ON**; A residual fails despite multislot; B selective. Not reverse cascade; not multislot OFF re-probe (E257); not residual kill.

## Hypothesis

Shared L–R ports. Multislot ON, `ilw_pair_replace_enabled=True`. Train A (400↔7000), idle T_GAP=200, train B (1500↔2500).

1. Fire L@400 → A partner selective **fails** ≥0.70  
2. Fire L@1500 → B partner selective ≥0.80  
3. Matched control replace OFF: A residual **succeeds** ≥0.80 (E256-class)  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | replace ON: A residual fails | ≥0.70 |
| B2 | replace ON: B selective | ≥0.80 |
| B3 | replace OFF: A residual survives | ≥0.80 |

Seeds {7801,7811} trials 6. Budget ~22 min, hard cap 44 min.

## What is NOT claimed

Not reverse cascade pair_replace (E244). Not free dual. Not residual soft/hard kill.

## Prediction

🔮 LEAN PASS if pair_replace overwrites partner links even when multislot ON (blocks E256-class co-residence).

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=1.0 B3=1.0.  
pair_replace ON does **not** erase A residual after gap+B under multislot ON (B1 fails). B selective OK; replace OFF A survives. Finding: multislot co-residence dominates replace for dual decade shared-port curriculum (unlike E244 reverse cascade break under replace).


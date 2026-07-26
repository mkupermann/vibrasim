# BP-E141 — Cascade coincidence AND multi-hop: (L1∧L2)→M→A→R soft dual wipe-restore

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E128 PASS (2-hop AND wipe-restore); multi-hop E56  
**Discipline:** **new topology** = gated AND mid then ungated M→A→R third hop — cascade wipe-restore

## Hypothesis
L1,L2 → gated M → A → R. Soft dual-cut both L ports; full restore all hops + re-arm gate.
1. After train: dual ON ∧ single OFF ≥0.80  
2. After dual soft wipe: dual OFF ≥0.80  
3. After full restore: dual ON ≥0.80  

## Bars
B1 cascade AND initial ≥0.80 · B2 wipe silence ≥0.80 · B3 restore dual ON ≥0.80  

Seeds {3781,3791} trials 6. Budget ~12 min, hard cap 24 min.

## Prediction
🔮 LEAN PASS if third hop is reliable; NULL if cascade fails single-off or restore misses hop.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Cascade gated multi-hop AND soft dual wipe-restore closed.

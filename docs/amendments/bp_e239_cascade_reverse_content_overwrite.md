# BP-E239 — Cascade reverse content overwrite same path (no kill)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E214 cascade reverse PASS; E234 retrain coexist PASS; E6/E158 overwrite curricula (ports)  
**Discipline:** multi-trial reverse **content overwrite** on same L–M–R ports without mid-kill — retrain with swapped freqs; reverse structure still selects L0.

## Hypothesis

Path0 cascade only (path1 weakly anchored for exclusivity).

1. Train path0 with ascending freqs: fire R0 → reverse p0 ≥0.90  
2. Overwrite retrain path0 with descending freqs (no kill): fire R0 → reverse p0 ≥0.90  
3. Post-overwrite exclusive reverse p0 (p0>p1) ≥0.80  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | pre-overwrite rev p0 | ≥0.90 |
| B2 | post-overwrite rev p0 | ≥0.90 |
| B3 | post exclusive rev p0 | ≥0.80 |

Seeds {7241,7251} trials 6. Budget ~20 min, hard cap 40 min.

## What is NOT claimed

Not mid-kill. Not hop-depth. Not free dual. Not graded write re-probe (E238).

## Prediction

🔮 LEAN PASS if pair-link reverse structure survives content re-write on same geometry.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Content overwrite (ascending→descending freqs) on same reverse path without kill: reverse structure still selects L0 exclusively. Not mid-kill.


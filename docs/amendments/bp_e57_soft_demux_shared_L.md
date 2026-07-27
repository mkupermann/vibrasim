# BP-E57 — Soft DEMUX: shared L fan-out to three R

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** E49 soft MUX (separate L per path); E45 selective soft  
**Discipline:** not E49 retune — **shared source L** fans to three arms (true demux)

## Hypothesis
One L; three arms L–M_k–R_k (y=12,25,38). Soft I_k near each M_k.  
Curriculum: restore all, soft-cut all but arm k; fire **shared L**; only R_k ON.

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Select arm0 only (R0 ON, R1/R2 OFF) | ≥0.80 |
| B2 | Select arm1 only | ≥0.80 |
| B3 | Select arm2 only | ≥0.80 |

Seeds {1661,1671} trials 6. Budget ~5 min, hard cap 10 min.

## Prediction
🔮 LEAN PASS if y-sep keeps soft radii local. Miss if shared L bridges cross-arm or cut bleeds.

## RESULT
**PASS** (2026-07-20). B1=B2=B3=1.0. Soft DEMUX: shared L fan-out; soft-cut selects one of three R arms.

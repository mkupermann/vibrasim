# BP-E238 — Cascade reverse graded write strength (no mid-kill)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E214 cascade reverse PASS; E224 graded soft mid NULL (different: graded **write** not kill)  
**Discipline:** multi-trial reverse **content strength** — weak pair-writes fail reverse; strong pair-writes succeed. Not mid-kill/restore; not hop-depth re-probe.

## Hypothesis

Same dual L–M–R pair-link scaffold as E214. Single path0 focus for graded write.

1. **Weak train** (N_WRITE=2 per link, N_TRAIN=6): fire R0 → reverse p0 **fails** ≥0.70  
2. **Strong train** (N_WRITE=12, N_TRAIN=12): fire R0 → reverse p0 ≥0.90  
3. **Strong train** also: fire R0 → reverse p0 exclusive (p0>p1) ≥0.80  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | weak reverse fails | ≥0.70 |
| B2 | strong reverse succeeds | ≥0.90 |
| B3 | strong exclusive rev p0 | ≥0.80 |

Seeds {7201,7211} trials 6. Budget ~18 min, hard cap 36 min.

## What is NOT claimed

Not mid-kill graded soft (E224). Not free dual. Not hop-depth.

## Prediction

🔮 LEAN PASS if reverse needs adequate write dose (pair-link strength) not just topology presence.

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=1.0 B3=1.0.  
Weak pair-writes (N_WRITE=2, N_TRAIN=6) still produce reverse success — graded weak arm does not fail. Strong arm OK. Reverse cascade is **dose-robust** at low write counts under this scaffold (not mid-kill). Finding: weak≠fail at pre-registered weak dose.


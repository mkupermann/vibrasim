# BP-E233 — Triple-hop reverse incomplete-path (omit A–R)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E231 triple-hop reverse PASS; E229 two-hop incomplete reverse PASS  
**Discipline:** multi-trial three-hop reverse **incomplete boundary** — train L–M and M–A only (no A–R); reverse from R must fail. Full-path control must succeed. Not mid-kill; not E229 two-hop re-probe.

## Hypothesis

E190/E231 L–M–A–R geometry, pair-link ILW, charge prop + latch.

1. **Incomplete** (L–M, M–A only): fire R0 → reverse L0 **fails** ≥0.70  
2. **Incomplete**: fire R1 → reverse L1 **fails** ≥0.70  
3. **Full train control**: fire R0 → reverse L0 ≥0.80  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | incomplete rev p0 fails | ≥0.70 |
| B2 | incomplete rev p1 fails | ≥0.70 |
| B3 | full rev p0 succeeds | ≥0.80 |

Seeds {7001,7011} trials 6. Budget ~22 min, hard cap 44 min.

## What is NOT claimed

Not mid-kill. Not two-hop incomplete re-probe alone. Not free dual.

## Prediction

🔮 LEAN PASS if reverse needs the terminal A–R hop like E229 needs M–R.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Omit A–R hops: reverse from R fails both paths. Full triple-hop reverse OK. Terminal A–R required (extends E229 incomplete boundary to three hops). Not mid-kill.


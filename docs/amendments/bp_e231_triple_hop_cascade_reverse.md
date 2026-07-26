# BP-E231 — Triple-hop cascade reverse fire-select (L←M←A←R)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E190 triple-hop forward PASS; E214 two-hop cascade reverse PASS; E230 concurrent reverse PASS  
**Discipline:** multi-trial **three-hop reverse** content cascade — not mid-kill/restore, not two-hop re-probe.

## Hypothesis

Dual L–M–A–R ports (E190 geometry), pair-link ILW, charge prop + latch.

1. Fire R0 → reverse-select L0 (L0 peak ≥1 and L0 > L1) ≥0.80  
2. Fire R1 → reverse-select L1 ≥0.80  
3. Both sequential arms succeed in same trial ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | fire R0 → rev L0 | ≥0.80 |
| B2 | fire R1 → rev L1 | ≥0.80 |
| B3 | both in same trial | ≥0.70 |

Seeds {6921,6931} trials 6. Budget ~22 min, hard cap 44 min.

## What is NOT claimed

Not mid-kill. Not concurrent dual R. Not free dual. Not two-hop reverse re-probe.

## Prediction

🔮 LEAN PASS if reverse prop chains through three hops like forward E190 / reverse E214.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Triple-hop reverse cascade fire-select works for both dual paths. Reverse prop chains L←M←A←R like forward E190 / reverse E214. Not mid-kill.


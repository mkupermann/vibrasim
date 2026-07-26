# BP-E237 — Five-hop cascade reverse fire-select

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E236 four-hop reverse PASS; E231 triple-hop reverse PASS  
**Discipline:** multi-trial **five-hop reverse** dual content cascade — not mid-kill; not four-hop re-probe alone (depth extension).

## Hypothesis

Dual six-port chains (5 hops) Y-separated, pair-link ILW, charge prop + latch.

1. Fire R0 → reverse-select L0 ≥0.80  
2. Fire R1 → reverse-select L1 ≥0.80  
3. Both sequential arms succeed in same trial ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | fire R0 → rev L0 | ≥0.80 |
| B2 | fire R1 → rev L1 | ≥0.80 |
| B3 | both in same trial | ≥0.70 |

Seeds {7161,7171} trials 6. Budget ~26 min, hard cap 52 min.

## What is NOT claimed

Not mid-kill. Not incomplete. Not free dual. Not four-hop re-probe.

## Prediction

🔮 LEAN PASS if reverse prop continues to scale hop depth like E231/E236.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Five-hop dual reverse cascade fire-select works both paths. Reverse prop scales to five hops. Not mid-kill.


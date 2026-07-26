# BP-E236 — Four-hop cascade reverse fire-select (L←·←·←·←R)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E36 four-hop forward PASS; E231 triple-hop reverse PASS  
**Discipline:** multi-trial **four-hop reverse** dual content cascade — not mid-kill; not triple-hop re-probe.

## Hypothesis

Dual five-port chains (4 hops) Y-separated, pair-link ILW, charge prop + latch.

1. Fire R0 → reverse-select L0 ≥0.80  
2. Fire R1 → reverse-select L1 ≥0.80  
3. Both sequential arms succeed in same trial ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | fire R0 → rev L0 | ≥0.80 |
| B2 | fire R1 → rev L1 | ≥0.80 |
| B3 | both in same trial | ≥0.70 |

Seeds {7121,7131} trials 6. Budget ~24 min, hard cap 48 min.

## What is NOT claimed

Not mid-kill. Not incomplete omit. Not free dual. Not three-hop re-probe.

## Prediction

🔮 LEAN PASS if reverse prop extends through four hops like E231 triple / E36 forward.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Four-hop dual reverse cascade fire-select works both paths. Reverse prop extends through four hops. Not mid-kill.


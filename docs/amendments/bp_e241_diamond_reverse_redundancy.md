# BP-E241 — Diamond reverse redundancy (no mid-kill)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E35 forward diamond PASS; E214 cascade reverse PASS  
**Discipline:** multi-trial **diamond reverse** — dual mid arms L←M1←R and L←M2←R; fire R reaches L. Single-arm train still works; empty fails. Not mid-kill farm (E35 kill M1); not hop-depth re-probe.

## Hypothesis

Diamond geometry L, M1, M2, R. Pair-link ILW, charge prop + latch.

1. Full diamond train: fire R → peak L ≥1.0 ≥0.90  
2. Single-arm train (L–M1–R only): fire R → peak L ≥1.0 ≥0.80  
3. No train: fire R → peak L <1.0 (fail) ≥0.70  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | full diamond reverse | ≥0.90 |
| B2 | single-arm reverse | ≥0.80 |
| B3 | no-train reverse fails | ≥0.70 |

Seeds {7281,7291} trials 6. Budget ~18 min, hard cap 36 min.

## What is NOT claimed

Not soft/hard mid-kill diamond. Not free dual. Not concurrent dual-path.

## Prediction

🔮 LEAN PASS if reverse prop works through either diamond arm like forward E35 structure without kill.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Diamond reverse: full and single-arm reverse R→L work; no-train fails. Redundant reverse arms without mid-kill.


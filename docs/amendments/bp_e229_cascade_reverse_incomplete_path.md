# BP-E229 — Cascade reverse incomplete-path negative (no mid-kill)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E214 cascade reverse PASS; E191 incomplete forward cascade negative  
**Discipline:** multi-trial reverse content boundary — **missing M–R hop** (not mid-kill/restore farm). Incomplete reverse path must fail; full-path control must succeed.

## Hypothesis

Dual L–M–R ports, pair-link ILW, charge prop + latch (same scaffold as E214).

1. **Incomplete train** (L–M hops only; no M–R): fire R0 → reverse L0 **fails** ≥0.70  
2. **Incomplete train**: fire R1 → reverse L1 **fails** ≥0.70  
3. **Full train control** (all four hops): fire R0 → reverse L0 ≥0.90  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | incomplete: fire R0 → rev p0 fails | ≥0.70 |
| B2 | incomplete: fire R1 → rev p1 fails | ≥0.70 |
| B3 | full: fire R0 → rev p0 succeeds | ≥0.90 |

Seeds {6841,6851} trials 6. Budget ~18 min, hard cap 36 min.

## Negative control

Full-path B3 must pass — protocol + reverse cascade still work when hops complete. Incomplete arms must not spuriously reverse-select.

## What is NOT claimed

Not soft/hard mid-kill. Not restore. Not G12. Not free dual.

## Prediction

🔮 LEAN PASS if reverse cascade genuinely needs full M–R chain like forward E191 incomplete boundary.

## RESULT

**PASS** (2026-07-26). B1=1.0 B2=1.0 B3=1.0.  
Incomplete L–M-only train: reverse from R fails for both paths. Full-path control reverse p0 succeeds. Reverse cascade requires complete M–R hops (parallel to forward E191 incomplete boundary). Not mid-kill.


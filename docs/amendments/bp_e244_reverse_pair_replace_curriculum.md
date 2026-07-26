# BP-E244 — Reverse cascade with pair_replace curriculum switch

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E28 pair_replace curriculum PASS; E214 cascade reverse; E239 content overwrite without replace  
**Discipline:** multi-trial reverse with **`ilw_pair_replace_enabled=True`** — train path0 reverse OK; retrain path1 only with replace ON; path1 reverse OK; path0 reverse may fail if replace kills old partners (or coexist — pre-register switch).

## Hypothesis

Dual L–M–R cascade. `ilw_pair_replace_enabled=True`.

1. Train path0 only: fire R0 → reverse p0 ≥0.90  
2. Then train path1 only (replace ON, no kill): fire R1 → reverse p1 ≥0.90  
3. After path1 train: fire R0 → reverse p0 **fails** ≥0.70 (replace disrupts path0 co-residence unlike E234 replace OFF)  

## Bars

| id | criterion | threshold |
|----|-----------|-----------|
| B1 | after p0-train rev p0 | ≥0.90 |
| B2 | after p1-train rev p1 | ≥0.90 |
| B3 | after p1-train rev p0 fails | ≥0.70 |

Seeds {7341,7351} trials 6. Budget ~20 min, hard cap 40 min.

## What is NOT claimed

Not E234 re-probe (replace was OFF). Not mid-kill. Not free dual. Not G12.

## Prediction

🔮 LEAN NULL if replace is local to rewritten pairs only and Y-separated path0 survives (then B3 fails → NULL: replace does not global-kill reverse co-residence).

## RESULT

**NULL** (2026-07-26). B1=0.0 B2=0.0 B3=1.0.  
With `ilw_pair_replace_enabled=True`, reverse cascade fails even after path0-only train (B1=0). B3 vacuously passes (p0 reverse fails). Finding: pair_replace ON is **incompatible** with reverse cascade co-residence under this scaffold (unlike E234 replace OFF). Not a curriculum switch — baseline reverse broken under replace.


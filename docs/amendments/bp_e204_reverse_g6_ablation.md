# BP-E204 — Reverse fire-select G6 ablation (not G13)

**PRE-REGISTERED 2026-07-26 before data**  
**Depends on:** E203 NULL (reverse works; bidir not required); E171 forward fire-select  
**Discipline:** isolate **G6 bridge_atom_propagation** for reverse R→L. Both arms: pair-link + bridge_charge_prop + latch. Treat = G6 OFF; Ctrl = G6 ON. No bidir.

## Hypothesis
1. Ctrl G6 ON: fire R-hi → L-lo reverse select ≥0.70  
2. Treat G6 OFF: fire R-hi → L-lo reverse **fails** ≥0.70  
3. Treat G6 OFF: forward fire L-lo → R-hi still ≥0.70 (pair-link charge prop sufficient forward)

## Bars
B1 ctrl reverse ≥0.70 · B2 treat reverse fail ≥0.70 · B3 treat forward ≥0.70  

Seeds {5721,5731} trials 6. Budget ~20 min, hard cap 40 min.

## Prediction
🔮 LEAN NULL if pair-link + bridge_charge_prop already reverse (E203 ctrl had G6 ON). If B2 fails (reverse still works G6 OFF), reverse is pair-link-native. If B2 passes, G6 is load-bearing for reverse only.

## RESULT
**NULL** (2026-07-26). B1=1.0 B2=0.0 B3=1.0. Reverse still works with G6 OFF; forward works G6 OFF. Reverse fire-select is **pair-link + bridge_charge_prop native** — neither G13 (E203) nor G6 (E204) required.

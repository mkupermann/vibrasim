# PRIM5 — Exclusive pair link on dual ILW write

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Depends on:** E15 NULL (all-to-all cross bridges kill selectivity)

## Primitive

**Config:** `ilw_pair_link_enabled: bool = False` (default OFF)

**API:** `apply_ilw_pair_write(world, port_L, port_R, seed_L, seed_R, rng)`  
1. ILW at L with seed_L → atom/mol index i  
2. ILW at R with seed_R → atom/mol index j  
3. If pair_link enabled and i,j ≥ 0: ensure a bridge between i and j exists (allocate if needed, strength += delta).  
4. Does **not** form bridges to other cross-side atoms in this call.

**Honesty:** Engineered exclusive association edge. form_bridges may still add extra edges unless `ilw_pair_link_only=True` sets atom_valence path… For D0 we disable general form_bridges side effects by `atom_valence=0` and only pair_link creates bridges.

## PRIM5-D0 bars

| ID | Criterion | thr |
|----|-----------|-----|
| L1 | After two pair_writes (class0 then class1) with pair_link ON, valence=0: exactly 2 cross bridges ≥0.85 trials | ≥0.85 |
| L2 | Same with pair_link OFF: cross bridges = 0 ≥0.90 trials | ≥0.90 |
| L3 | Each bridge endpoints match one exclusive pair row (nearest) — both classes present ≥0.80 | ≥0.80 |

Seeds {521, 531}, trials 10.

## Prediction
🔮 PASS

## RESULT
### PRIM5-D0 **PASS** (2026-07-20 night)
L1=1 L2=1 L3=1. Exclusive pair-link creates exactly two class-matched cross bridges.

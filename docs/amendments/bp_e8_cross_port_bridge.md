# BP-E8 — Cross-midplane bridge after dual ILW write

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Depends on:** PRIM2 ILW, midplane  
**Discipline:** hard structural question — not K-band storage farm; external map not used for bars

---

## Hypothesis

**H-E8.** After **joint** dual-port ILW (both sides seeded as L4 atoms ~40 units apart) with `atom_valence=4` and `r_2=45` (span > port distance), idle T ticks so `form_bridges` can run:

1. **≥1 bridge** connecting an atom with x&lt;mid to an atom with x≥mid in ≥ **0.85** of trials.  
2. **One-sided** ILW (left only): cross-mid bridges in ≤ **0.15** of trials.  
3. Dual write: both sides have ≥1 L4 in ≥ **0.90** trials.

If PASS: physical cross-port **graph link** exists (substrate-native association handle).  
If NULL: need PRIM4 long-range port-link primitive (distance/valence/bridge rules insufficient).

## Bars

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | Dual write: fraction trials with ≥1 cross-mid bridge | ≥ **0.85** |
| B2 | One-sided: fraction with ≥1 cross-mid bridge | ≤ **0.15** |
| B3 | Dual: both sides populated L4 | ≥ **0.90** |

## Protocol
Seeds {341, 351}, trials 12; N_write=15; T_idle=300; mid=40; ports (20,25,25)/(60,25,25); r_2=45; valence=4; midplane ON; ILW ON; tau=0. Budget 90s / hard 180s.

## Prediction
🔮 **LEAN NULL or borderline**: form_bridges uses r_2 and valence; ports 40 apart under r_2=45 should work *if* atoms stay near ports — but midplane does not block bridges. Most-likely miss: atoms drift/repel, or bond formation blocked elsewhere → B1 fail.

## RESULT
**PASS** (2026-07-20 night). B1_dual_cross=**1.000**, B2_onesided=**0.000**, B3_pop=**1.000**.

### Calibration
🔮 lean NULL — **MISS** (good surprise): with r_2=45 and valence=4, dual ILW seeds form reliable cross-mid bridges; one-sided never does.

### Lesson
Physical cross-port **graph link** is available without PRIM4. Association object can be the bridge + endpoint structure.

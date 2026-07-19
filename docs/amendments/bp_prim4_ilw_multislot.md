# PRIM4 — ILW multi-slot (do not collapse distinct bands)

**PRE-REGISTERED 2026-07-20 before data (night)**  
**Depends on:** E6 last-write collapse; E5 K=3 storage on single atom  
**Discipline:** new primitive default OFF; enables multi-item port buffer

---

## Motivation

E6: sequential different classes on the same port **overwrite** one atom’s freq (nudge).  
A port cannot hold a **multiset** of past bands. Multi-trial dictionaries need multiple L4 slots per port.

---

## Primitive

**Config (default OFF):**
- `ilw_multislot_enabled: bool = False`
- `ilw_multislot_rel_freq: float = 0.35`  
  When enabled, `apply_ilw_port_event`:
  1. Among level≥4 in radius, prefer molecule strengthen as today if |f - seed|/max(seed,f,1) ≤ rel **or** always strengthen mol if present with similar freq.
  2. Else among atoms: if nearest atom has relative freq distance ≤ `ilw_multislot_rel_freq`, strengthen+nudge that atom.
  3. Else if any atom in radius has rel distance ≤ thr, use closest such.
  4. **Else allocate a new L4** at port (engineered seed) even if other atoms exist nearby.

Honesty: engineered multi-slot write; not free emergence.

---

## PRIM4-D0 bars

| ID | Criterion | thr |
|----|-----------|-----|
| M1 | Multislot ON: after writing bands 400 then 5000 on L only (N_write each), count distinct L4 on L with freqs in both low&high bins ≥ **0.85** trials | ≥0.85 |
| M2 | Multislot OFF (legacy): same protocol → fraction trials with ≥2 distinct L4 on L ≤ **0.20** | ≤0.20 |
| M3 | No free-vib Δ on either half | =1.0 |

Seeds {381, 391}, trials 10; smoke 1×3. N_write=12; T_idle=50. Budget 60s / hard 120s.

## Prediction
🔮 PASS if implementation allocates second atom when rel freq gap large.

## RESULT
### PRIM4-D0 **PASS** (2026-07-20 night)
M1=1.0 M2=0.0 M3=1.0. Multislot holds two bands; legacy collapses.

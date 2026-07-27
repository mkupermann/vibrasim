# PRIM2 — Internal non-broadcast write (new primitive)

**PRE-REGISTERED 2026-07-19 before data**  
**Depends on:** C CLOSED PARTIAL; PRIM1 D0 leaky; D1 sphere NULL  
**Discipline:** sharp

---

## Motivation

Even if walls improve χ, C-talent failed when drive was **free-vibration field**.  
Activity-memory programme: **write ≈ leak** for activity representations.  
Matter-position and molecule composition succeed when write is **local to bound structure**.

**Missing piece candidate:** a write that updates **local bound matter** without injecting a traveling free-vibration broadcast.

---

## Primitive specification

### Name
**Internal Local Write (ILW)**

### Behaviour (Variant A — first implementation)

When `ilw_enabled` and a port event fires for compartment/region R:

1. Do **not** inject free vibrations into the global field.  
2. Instead, within radius `ilw_radius` of the port centre **inside R**:  
   - If ≥1 level≥4 atom exists: increase `k_strength` of nearest level≥5 molecule (or create one diatomic from two nearest opposite-polarity atoms if present) by `ilw_delta_strength`.  
   - Else: allocate one level-4 atom at port centre (engineered seed — **named as engineered**).  
3. No free `s_*` injection from this path.

### Explicit honesty
- Port location is **engineered** (§4.8).  
- ILW is **not** “emergent understanding.”  
- Goal: local structural change **without** raising free-vibration contamination in the other half.

---

## Diagnostic sequence (locked order)

### PRIM2-D0 — Broadcast contrast (after ILW implemented)

Two arms, same seeds {181, 191}, 2 trials, T=600:

| Arm | Write | Measure |
|-----|-------|---------|
| FREE | classic free-vib burst N=200 in left only | χ and Δ free count in **right** half |
| ILW | ILW port events on left only (matched wall-clock / event count) | χ and Δ free count in right half |

**Bars:**

| ID | Criterion | thr |
|----|-----------|-----|
| I1 | mean Δ free_right under ILW | ≤ **0.5 ×** mean Δ free_right under FREE (or absolute Δ free_right_ILW ≤ 5) |
| I2 | ILW left has structural change: mean Δ strength or +atoms in left | ≥ locked: at least **+1** strength-unit total or +1 level≥4 in left in ≥80% trials |
| I3 | FREE arm still shows Δ free_right ≥ 10 (sanity: free write really contaminates) | True |

If I1+I2+I3: ILW accepted as non-broadcast local write.  
Talent re-open = **separate** amendment after PASS.

---

## Prediction
Prior ≈ 0.45 PASS on I1–I3 if ILW never touches `s_alive` inject.

## RESULT
### PRIM2-D0 **PASS** (2026-07-19)
I1: ILW delta free_right=0 (FREE arm=689); I2 structural 1.0; I3 FREE contaminates 689.
ILW is accepted as non-broadcast local write (engineered port). Talent re-open needs separate amendment.


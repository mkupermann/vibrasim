# PRIM6 — Bridge-propagated charge latch (sustained hold)

**PRE-REGISTERED 2026-07-20 before data (night scheduler)**  
**Depends on:** E13/E19 NULL end-state charge; E14/E20 peak works  
**Discipline:** new primitive default OFF; not E13/E19 bar retune

---

## Motivation

Membrane `tau_membrane` wipes `k_charge` between fires → end-state partner readouts NULL.  
Peak readouts work but do not leave a **durable activity mark**.  
Need a separate **latched** channel that receives bridge-prop deposits and does not use membrane decay.

---

## Primitive

**Config (default OFF):**
- `charge_latch_enabled: bool = False`
- `charge_latch_tau: float = 0.0`  
  - When enabled and `tau <= 0`: latch does **not** decay (hold until reset).  
  - When `tau > 0`: exponential decay with that tau (seconds).

**State:** `world.k_latch[K]` — float, default 0.

**Update:** In `apply_bridge_charge_propagation`, when depositing `gain * s` to neighbour `k_charge`, if latch enabled also:

`k_latch[neighbour] += gain * s`

**Decay:** `apply_charge_latch_decay` each tick if enabled and tau>0.

**Honesty:** Engineered hold channel for port curricula — not free metabolic persistence.

---

## PRIM6-D0 bars

| ID | Criterion | thr |
|----|-----------|-----|
| P1 | Latch ON: after dual ILW + force-fire L + idle T_end=80 (no re-drive), max R `k_latch` ≥ **1.0** in ≥0.90 trials | ≥0.90 |
| P2 | Latch OFF: after same protocol, max R `k_charge` ≤ **0.25** in ≥0.90 trials | ≥0.90 |
| P3 | Latch ON does not inject free vibs (Δ free = 0) | ≥0.90 |

Seeds `{641, 651}`, trials 10; smoke 1×3. PRIM5 pair link, valence=0. Budget 90s / hard 180s.

## Prediction
🔮 PASS — latch accumulates prop deposits independent of membrane.

## RESULT
### PRIM6-D0 **PASS** (2026-07-20 night scheduler)
P1=1.0 P2=1.0 P3=1.0. Latch holds after T_end; membrane charge gone; no free inject.

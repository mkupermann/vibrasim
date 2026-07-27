# PRIM3 — ILW matter strength decay (recency channel)

**PRE-REGISTERED 2026-07-20 before data**  
**Depends on:** PRIM2 ILW, E3 order-from-equal-strength CLOSED  
**Discipline:** new primitive, default OFF; not E3 bar retune

---

## Motivation

E3: equal-N sequential ILW → equal strength; **last-write order not recoverable**.  
L4 atoms are **permanent** (existence); strength only accumulates.  
Missing: a **leak on local matter strength** so older writes fade and newer mass dominates — a recency channel without claiming free talent.

---

## Primitive

**Name:** ILW matter strength decay (engineered optional leak)

**Config (default OFF = legacy):**
- `ilw_strength_decay_tau: float = 0.0`  
  When `> 0` and at least one of `ilw_enabled` / explicit use: each tick, for every alive level≥4 node:

  `s ← 1.0 + (s - 1.0) * exp(-dt / tau)`

  Floor at 1.0. Does **not** kill atoms (permanence of L4 identity preserved).  
  Does **not** inject free vibrations.

**Honesty:** Engineered leak for port curricula / recency tests. Not emergent metabolism.

---

## Acceptance (PRIM3-D0) — mechanism fires

| ID | Criterion | thr |
|----|-----------|-----|
| P1 | After single-side ILW N_write=20 then idle T=400 with tau=2.0: mean side strength < 0.5 × strength measured immediately post-write | True (≥0.90 trials) |
| P2 | Same protocol with tau=0: post-idle strength ≥ 0.90 × post-write strength | True (≥0.90 trials) |
| P3 | No free-vib inject: Δ free count = 0 on both halves | True |

If P1–P3: primitive accepted. Order re-test = **BP-E7** separate amendment.

## Protocol PRIM3-D0
Seeds {311, 313}, trials 8; smoke 1×3. Midplane+ILW on. Budget 45s / hard 100s.

## Prediction
🔮 PASS — exponential leak is deterministic on k_strength.

## RESULT
### PRIM3-D0 **PASS** (2026-07-20)
P1=1.0 P2=1.0 P3=1.0. Strength leak fires under tau=2; off preserves mass; no free-vib.

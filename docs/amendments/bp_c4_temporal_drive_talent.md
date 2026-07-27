# BP-C4 — Temporal-pattern specialization (Rung C, NEW mechanism)

**PRE-REGISTERED before any data · 2026-07-19**  
**Discipline:** `docs/DISCIPLINE_SHARP.md` D9 — not a retune of C1–C3.

---

## Why this is allowed under sharp discipline

C1–C3 tested **frequency-band dual drive**. All NULL / partial.  
**Closed for that mechanism family.**  

BP-C4 asks a **different** question:  
Can two collections specialize when they share the **same frequency band** but receive **different temporal drive patterns** (rhythm), with no pretrained sense nets?

---

## Hypothesis

**H-C4.** Left region receives pulsed free-vibration injections (period *P_L*); right receives a different period *P_R*; same log-frequency band for both. After training, a **probe** of period *P_L* produces more new level≥1 nodes in the left half than the right (and symmetrically for *P_R*), above locked bars, while a matched same-period control does not.

If NULL: temporal rhythm alone does not create dual-collection talent under current primitives → C-family strengthens the boundary (talent needs different primitives or engineered topology).

---

## Mechanism (locked)

- Box `(80, 50, 50)`, midplane `x = 40`.  
- **Shared band** both sides: `freq ∈ [200, 4000]` log.  
- **Train** *T_train* ticks:  
  - Left: every *P_L* ticks inject *N_burst* free vibrations into left volume only.  
  - Right: every *P_R* ticks inject *N_burst* into right volume only.  
  - *P_L* = 30 ticks, *P_R* = 90 ticks (locked).  
- **Probe LOW-period (P_L):** inject *N_probe* globally with period *P_L* for *T_probe* ticks; score `dL = Δn_left`, `dR = Δn_right` (level≥1 node count). Success if `dL > dR`.  
- Fresh world **Probe HIGH-period (P_R):** success if `dR > dL`.  
- **Control C1:** both sides same period *P_L* during train; same probes — success rate must stay low.

No composition planting. No VSA. Headless.

---

## Bars (locked — no post-hoc change)

| ID | Criterion | Threshold |
|----|-----------|-----------|
| B1 | Train L≠R periods: probe-P_L success rate | ≥ **0.75** |
| B2 | Train L≠R periods: probe-P_R success rate | ≥ **0.75** |
| B3 | Control same-period train: mean of both probe success rates | ≤ **0.55** |
| B4 | Train: both halves have ≥1 level≥4 before probe (dual-period arms) | ≥ **0.70** |

Chance-ish floor for B1/B2 is 0.5; 0.75 is the locked bar.

---

## Protocol numbers (locked)

| Param | Value |
|-------|--------|
| N_burst | 40 |
| N_probe | 80 |
| T_train | 900 |
| T_probe | 300 |
| Official seeds | **{151, 157, 163}** |
| Trials / seed | **3** |
| P_L / P_R | **30 / 90** ticks |
| Time estimate | 20 min |
| Hard 2× ceiling | 40 min |

---

## Prediction (pre-data)

Prior ≈ **0.25 PASS**. Most likely NULL: probes wash out regional history (same as C2 frequency probes).  
If PASS: first evidence that **temporal** dual drive yields selective response — still not “understanding,” but new C-mechanism positive.

---

## Runner

`tools/run_bp_c4_temporal_drive_talent.py`  
`~/.eqmod/bet/BP-C4/result.json`

## RESULT

**Verdict: NULL** (2026-07-19) · headless · seeds {151,157,163} · 3 trials/seed  
`~/.eqmod/bet/BP-C4/result.json`

| Bar | Value | thr | ok |
|-----|------:|-----|:--:|
| B1 probe P_L | **0.111** | ≥0.75 | no |
| B2 probe P_R | **1.000** | ≥0.75 | no* |
| B3 control mean | **0.722** | ≤0.55 | no |
| B4 train pop | **1.000** | ≥0.70 | yes |

\*B2 alone would pass but is **not** defensible: control (B3) also high → period-probe selectivity is **not** specifically from dual temporal train.

### Diagnosis (Pattern-01)
- Mechanism fired (injection + population).  
- Local effect asymmetric / artifactual (P_R always “wins” dR>dL; P_L almost never favors left).  
- Binding constraint: probe metric (Δ level≥1 counts) is **not a clean talent readout** under global periodic injection — same failure class as C2, different drive family.  
- **No bar retune. No C5 same design.**

### Discipline consequence
Under D9 + three frequency NULLs + this temporal NULL: **collection talent via dual regional free-vibration injection (freq or period) is closed as a mechanism class** on current primitives. Next C-step only with a **new primitive** or formal partial closure of Rung C.

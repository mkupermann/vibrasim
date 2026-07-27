# BP-PRIM1 — Directional local write channel (new primitive proposal)

**PRE-REGISTERED · 2026-07-19 · before any implementation data**  
**Depends on:** `bp_c_partial_closure.md` (C injection-dual talent CLOSED PARTIAL)  
**Discipline:** `docs/DISCIPLINE_SHARP.md`

---

## 1. Motivation (from evidence, not hope)

Unified failure of Rung C injection designs + long activity-memory programme:

| Finding | Implication |
|---------|-------------|
| write ≈ leak (activity memory closed) | Local content cannot stay selective in a homogeneous active medium |
| Dual injection talent NULL (C1–C4) | Regional free-vib drive does not create defensible specialised collections |
| Matter-position memory PASS (G114–G119) | **Matter** can hold selective content when representation is position, not free activity |
| Molecule composition PASS (B-path) | Bound structure can carry multi-bit content when write is local to the molecule |

**Diagnosis to test:**  
What is missing for *collection talent* is not “more STDP” or “different period,” but a **write path that is directional and non-broadcasting** — so drive into collection L does not become global field contamination of collection R (and vice versa).

---

## 2. Proposed primitive (specification)

### Name
**Directional Local Write (DLW)** — working name; not sold as biology until matched.

### Informal meaning
A **one-way, spatially gated coupling** from an engineered **port** (charter §4.8 allowed) into a **target compartment** of the substrate, such that:

1. Energy/activity/vibration injection intended for compartment L **primarily affects L**.  
2. Matched injection into R **primarily affects R**.  
3. Cross-talk (effect in the non-target compartment) is **below a locked fraction**.

### Relation to belief
- **Ports are engineered** (honest §4.8) — not “emergent talent organs.”  
- **Internals of each compartment** may still emerge (binding, molecules, local structure).  
- This reopens C only as: *with directional write, can two compartments develop distinct persistent structure/response without modality ML stacks?*

### Explicit non-claims
- Not a transformer. Not a pretrained embedding.  
- Not “we discovered axonal biology.”  
- Not automatic brain. Only a candidate **missing channel**.

---

## 3. Minimal implementation sketch (for later coding — not done in this pre-reg)

Config knobs (defaults OFF):

```text
dlw_enabled: bool = False
dlw_ports: tuple of (cx, cy, cz, radius, target_compartment_id)
dlw_cross_talk_max: float  # diagnostic only; not a training target
```

Behaviour when ON:

- Free vibrations (or charge events) originating in port *p* are **reflected/absorbed** if they would leave the target compartment without a DLW permit.  
- Alternatively (choose one in implementation PR, lock before run):  
  **Variant A — hard wall:** engineered compartment (existing `compartment_k`) per region + port injects only inside.  
  **Variant B — soft directional gate:** outbound flux from port region attenuated unless destination matches target id.

**First implementation MUST use Variant A** if possible (reuse existing compartment machinery) to avoid inventing untested soft gates.  
If Variant A is *already* what C1–C4 effectively had (spatial inject only), then PRIM1’s first experiment is a **diagnostic**: measure cross-talk under C1b-like inject — if cross-talk is already low and talent still fails, DLW-as-containment is **insufficient** and the missing piece is deeper (e.g. non-leaking *internal* write, not just walls).

---

## 4. Pre-registered diagnostic sequence (no talent bar yet)

### PRIM1-D0 — Containment audit (read-only / instrumentation)

**Hypothesis:** Under C1b-style dual spatial injection (no new code if possible), cross-talk is already low **or** high.

**Measure:**  
After train T=1200, N=400/side, bands L-low/R-high (same as C1b):  
fraction of free vibrations that were *injected in L* and are later found in R (and vice versa), if birth-region tagging is available;  
else: flux of free vibrations crossing midplane per tick / total free.

**Bars (diagnostic, not talent):**

| ID | Criterion | Interpretation |
|----|-----------|----------------|
| D0a | Report cross-talk ratio χ = free crossings / free count (mean) | number only |
| D0b | If χ ≤ 0.15 → containment “tight”; if χ ≥ 0.40 → “leaky” | classification locked |

**No PASS/FAIL on talent.** Output is χ and class.  
Seeds {171, 173}, 2 trials each — **observational**, thresholds for *classification* only.

**If already tight (χ≤0.15) and C1b was NULL:**  
→ walls/injection locality are **not** the missing talent ingredient; PRIM1-D1 must target **internal non-broadcast write**, not more walls.

**If leaky (χ≥0.40):**  
→ PRIM1-D1 = implement Variant A compartments + re-measure χ ≤ 0.15 as acceptance for the primitive *as containment*.

---

### PRIM1-D1 — Primitive acceptance (only if D0 says leaky **or** Variant B is chosen)

**Hypothesis:** With DLW Variant A ON, χ ≤ 0.15 on both seeds.

| ID | Criterion | thr |
|----|-----------|-----|
| P1 | mean χ | ≤ 0.15 |
| P2 | both compartments still form ≥1 level≥4 | ≥ 0.80 of trials |

Talent bars are **out of scope** for D1.

---

### PRIM1-D2 — Talent re-open (only after P1 PASS, new amendment number)

Not specified here. Must be a **new** doc `bp_c5_…` that reuses DLW and sets talent bars **before** run.  
If D0 says tight and C already failed, D2 is **not** automatic — write a different primitive proposal instead.

---

## 5. Time budgets (locked)

| Step | Estimate | 2× ceiling |
|------|----------|------------|
| D0 audit | 30 min | 60 min |
| D1 (if needed) | 45 min impl + 30 min run | 2× each |

---

## 6. Prediction (pre-data)

**D0 prior:** χ **moderate-high** (~0.25–0.5) because free vibrations move ballistically in a periodic box — dual inject is leaky.  
**If wrong (χ already ≤0.15):** the C-failure is **not** containment; next primitive must address **representational write** (matter-local), not walls.

---

## 7. Implementation status

| Item | Status |
|------|--------|
| This pre-reg | **LOCKED** |
| Code for birth-region tags / χ | **not started** |
| D0 run | **not started** |

---

## RESULT

### PRIM1-D0 (2026-07-19)
**DIAGNOSTIC: leaky** — mean χ=**0.433** (seeds 171,173 × 2 trials).  
All trials class=leaky. Interpretation locked: dual inject is leaky; **PRIM1-D1 Variant A justified**.
Artifact: ~/.eqmod/bet/PRIM1-D0/result.json

### PRIM1-D1 (2026-07-19)
**NULL** — Variant A dual spheres: chi_on=**0.412** (need ≤0.15), chi_off=0.430 (only slight reduce), pop_on=0.75.
Engineered sphere compartments do **not** achieve locked containment. DLW-as-two-spheres insufficient.
Artifact: ~/.eqmod/bet/PRIM1-D1/result.json
Next (not auto): midplane wall primitive or internal non-broadcast write (new pre-reg).

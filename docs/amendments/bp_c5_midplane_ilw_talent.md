# BP-C5 — Structural specialisation with midplane + ILW

**PRE-REGISTERED 2026-07-19 before any C5 data**  
**Depends on:** C CLOSED PARTIAL; PRIM1-D2 PASS; PRIM2-D0 PASS  
**Discipline:** reopens C only with **new tools** (midplane wall + ILW), not C1b bar retune alone.

---

## Hypothesis

**H-C5.** With **midplane wall ON**:

1. **FREE arm:** dual free-vib inject (L low-band, R high-band) yields  
   `mean_decade_L < mean_decade_R` on level≥4 in ≥ **0.90** of trials  
   (same structural bar as C1b, now with working containment).

2. **ILW arm:** dual **internal local write** (no free inject) at left/right ports with  
   seed frequencies in low vs high decade yields the same structural inequality  
   in ≥ **0.90** of trials.

3. Both arms: both halves populated (≥1 level≥4 each) in ≥ **0.80** of trials.

4. **χ** (tagged free wrong-side fraction) under FREE+midplane ≤ **0.15**  
   (containment sanity; ILW arm may have χ≈0 by construction).

If FREE PASSes and ILW fails: containment restores spectral specialisation via free chemistry.  
If ILW PASSes and FREE fails: only engineered local write specialises.  
If both PASS: dual path to structural “collection difference.”  
If both NULL: even with walls + ILW, structural talent bar still fails — deeper gap.

**Not claimed:** understanding, light/sound semantics, brain.

---

## Mechanism (locked)

- `midplane_wall_enabled=True`, `midplane_wall_x=40`  
- Box `(80,50,50)`, N=400/side free inject (FREE arm only)  
- Bands FREE: L [100,2000], R [500,10000]  
- ILW: `ilw_enabled=True`, ports `(20,25,25)` and `(60,25,25)`,  
  `seed_freq` L=500, R=5000 (via extended `apply_ilw_port_event`),  
  N_events=40 per side over T_train  
- T_train=1200  
- Seeds **{201, 203, 207}**, **3** trials/seed  
- Decode: mean floor(log10(k_freq)) level≥4 left vs right  

---

## Bars (locked)

| ID | Criterion | thr |
|----|-----------|-----|
| B1 | FREE arm: fraction md_L < md_R (both populated) | ≥ **0.90** |
| B2 | ILW arm: fraction md_L < md_R (both populated) | ≥ **0.90** |
| B3 | FREE arm: both sides populated | ≥ **0.80** |
| B4 | ILW arm: both sides populated | ≥ **0.80** |
| B5 | FREE arm: mean χ ≤ **0.15** | True |

**PASS** = all B1–B5.  
**PARTIAL** is not a verdict — if only one of B1/B2 fails → **NULL** with diagnosis which arm failed.

---

## Time budget
Estimate 25 min · hard 2× = 50 min.

## Prediction
Prior: FREE+wall ≈0.55 PASS on B1 (C1b was 0.78 without wall); ILW ≈0.70 on B2; χ≈0.

## Runner
`tools/run_bp_c5_midplane_ilw_talent.py`  
`~/.eqmod/bet/BP-C5/result.json`

## RESULT

**Verdict: NULL** (2026-07-19) · `~/.eqmod/bet/BP-C5/result.json`  
seeds {201,203,207} × 3 trials · T=1200 · midplane ON  

| Bar | Value | thr | ok |
|-----|------:|-----|:--:|
| B1 FREE specialisation | **0.667** | ≥0.90 | no |
| B2 ILW specialisation | **1.000** | ≥0.90 | yes |
| B3 FREE pop | **1.000** | ≥0.80 | yes |
| B4 ILW pop | **1.000** | ≥0.80 | yes |
| B5 χ FREE | **0.000** | ≤0.15 | yes |

### Diagnosis
- Containment works (χ=0).  
- **ILW dual-port spectral write fully separates halves** (B2). Honest: engineered seed_freq L/R — not pure free emergence.  
- **FREE dual-band under wall still only ~2/3** specialisation — same class as C1b near-miss (0.78), fails 0.90.  
- Overall NULL: free-chemistry talent still not at bar; ILW path is a **scoped engineered specialisation**, not a full C PASS under all bars.

### Belief language
Do **not** say “C PASSed.”  
Say: “With midplane+ILW, engineered local write produces reliable structural L/R difference; free-vib dual-band under wall still insufficient for 0.90.”

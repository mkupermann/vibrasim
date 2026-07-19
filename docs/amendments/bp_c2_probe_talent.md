# BP-C2 — Probe-response talent after dual drive (Rung C)

**Programme:** Belief path · follows BP-C1b NULL (structural specialisation 0.778)  
**Status:** PRE-REGISTERED  
**Date locked:** 2026-07-19  
**ID:** BP-C2  

---

## Hypothesis

**H-C2.** After dual-drive formation (left = low band, right = high band), a **probe** of free vibrations of one band produces **more new bound structure** (new level≥1 nodes born during the probe window) in the region that was **trained on that band** than in the other region.

This is behavioural talent, not only structural mean-decade specialisation (C1/C1b).

## Mechanism

1. **Train** (*T_train* ticks): plant N per side as C1b (L [100,2000], R [500,10000]); run physics.  
2. **Snapshot counts:** `nL0`, `nR0` = alive nodes with level≥1 and x in left/right.  
3. **Probe LOW:** inject *N_probe* free vibrations, band [100,2000], uniform in full box (not region-locked); run *T_probe* ticks.  
4. **Score:** `dL = nL1−nL0`, `dR = nR1−nR0` (level≥1 alive counts). Success if `dL > dR`.  
5. Fresh world for **Probe HIGH** band [500,10000]: success if `dR > dL`.

## Arms

| Arm | Train | Probe | Success |
|-----|-------|-------|---------|
| T-low | dual | LOW | dL > dR |
| T-high | dual | HIGH | dR > dL |
| C1-low | same-band both | LOW | dL > dR (must fail overall) |
| C1-high | same-band both | HIGH | dR > dL (must fail overall) |

## Bars (locked)

| ID | Criterion | Threshold |
|----|-----------|-----------|
| B1 | T-low success rate | ≥ **0.75** |
| B2 | T-high success rate | ≥ **0.75** |
| B3 | mean(C1-low, C1-high) success rate | ≤ **0.60** |
| B4 | Train: both halves have ≥1 level≥4 node before probe | ≥ **0.80** of dual-train trials |

## Protocol

| Param | Value |
|-------|--------|
| N_side | 400 |
| T_train | 1200 |
| N_probe | 200 |
| T_probe | 400 |
| box | 80×50×50 |
| r_2 | 28 |
| Official seeds | **{53, 59, 61}** |
| Trials/seed | **3** |

## Time budget

Estimate ≤ 25 min · hard 2× = 50 min.

## Prediction

Prior ≈ 0.35 PASS — probe may wash out regional history; NULL expected if talent is structural-only.

## Runner

`tools/run_bp_c2_probe_talent.py` · `~/.eqmod/bet/BP-C2/result.json`  
Live default ON.

## RESULT

**Verdict: NULL** (2026-07-19)  
`~/.eqmod/bet/BP-C2/result.json` · seeds {53,59,61} · 3 trials/seed · **headless lab**  

| Bar | Value | thr | ok |
|-----|------:|-----|:--:|
| B1 T-low probe | **0.444** | ≥0.75 | no |
| B2 T-high probe | **0.222** | ≥0.75 | no |
| B3 C1 mean | **0.556** | ≤0.60 | yes |
| B4 train pop | **1.000** | ≥0.80 | yes |

### Diagnosis
Training forms dual-region matter (B4 PASS). Probe response does **not** select the trained region above chance — talent is not behavioural under this probe design. Combined with C1b structural near-miss (0.778), **Rung C stays open / partial** — no bar retune.

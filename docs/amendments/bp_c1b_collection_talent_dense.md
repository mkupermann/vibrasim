# BP-C1b — Dual-drive specialisation under denser formation

**Programme:** Belief path · follows BP-C1 NULL (sparse dual-region matter)  
**Status:** PRE-REGISTERED  
**Date locked:** 2026-07-19  
**ID:** BP-C1b  

---

## Hypothesis

Same as H-C1: left low-band vs right high-band free-vibration drives produce `mean_decade_L < mean_decade_R` on level≥4 nodes when both sides form matter.

**Change vs C1 (mechanism/regime, not bar fishing):** session-3b-like denser binding + more particles + longer *T* so B4 population can fire. Bars **re-locked** at same numeric thresholds as C1 for the specialisation claim.

## Protocol (locked)

| Parameter | C1 | **C1b** |
|-----------|----|---------|
| N per side | 300 | **400** |
| T ticks | 800 | **1500** |
| box | 80×40×40 | **80×50×50** |
| r_2 | 20 | **28** |
| freq_tolerance | 0.030 | **0.030** |
| Official seeds | 17,29,43 | **{19, 31, 47}** |
| Trials/seed | 4 | **3** |

Bands unchanged: L [100,2000], R [500,10000]; C1 arm both [100,10000].

## Bars (same logic as C1)

| ID | Criterion | Threshold |
|----|-----------|-----------|
| B1 | T success `mean_L < mean_R` ∧ both n≥1 | ≥ 0.90 |
| B2 | C1 same-band success | ≤ 0.60 |
| B3 | Flipped inequality on T | ≤ 0.60 |
| B4 | Both regions populated | ≥ 0.80 |

## Time budget

Estimate ≤ 20 min · hard ceiling 40 min.

## Prediction

Prior ≈ 0.55 PASS if density was the only bind; NULL if specialisation still weak when both sides populate.

## Runner

`tools/run_bp_c1b_collection_talent_dense.py`  
`~/.eqmod/bet/BP-C1b/result.json`

## RESULT

**Verdict: NULL** (2026-07-19)  
`~/.eqmod/bet/BP-C1b/result.json` · seeds {19,31,47} · 3 trials/seed · T=1500  

| Bar | Value | thr | ok |
|-----|------:|-----|:--:|
| B1 T specialisation | **0.778** | ≥0.90 | no |
| B2 same-band | **0.222** | ≤0.60 | yes |
| B3 flipped | **0.111** | ≤0.60 | yes |
| B4 both populated | **1.000** | ≥0.80 | yes |

### Diagnosis
- **Population fixed** vs C1 (B4 PASS) — denser regime worked.
- Specialisation is **real and majority** (7/9 trials, controls fail) but **below locked 0.90**.
- No post-hoc bar relax. Finding: dual-drive structural talent is **partial / emergent-but-noisy**, not clean acceptance.
- Next (optional): BP-C1c multi-bit probe selectivity, or accept Rung C as open with this boundary.

# BP-C1 — Collections specialise under dual drive (Rung C, structural talent)

**Programme:** Belief path (`docs/BELIEF_PATH.md`)  
**Status:** PRE-REGISTERED  
**Date locked:** 2026-07-19  
**ID:** BP-C1  

---

## Hypothesis

**H-C1.** One world, one rule set, **two spatial collections** receiving different free-vibration frequency drives (no pretrained sense nets) develop **structurally different matter**: the mean frequency-decade of level≥4 nodes in the left region is systematically lower than in the right region after formation time *T*, so region identity is decodable from local matter alone.

This is the first climb of “collections have talent”: **structural specialisation**. Selective *response* to later probes is BP-C2 (only if C1 PASSes).

## Mechanism

- Box `(80, 40, 40)`; midplane `x = 40`.  
- **Left** (x&lt;40): inject *N* free vibrations, log-freq band **[100, 2000]** (“low / sound-like band”).  
- **Right** (x≥40): inject *N* free vibrations, log-freq band **[500, 10000]** (“high / light-like band”).  
- No hand-planted molecules/atoms; no VSA/reservoir.  
- After *T* ticks, for each half: mean `floor(log10(k_freq))` over alive nodes with `k_level ≥ 4`.  
- **Decode (locked):** trial succeeds if `mean_L < mean_R` and both sides have `n ≥ 1` level≥4 nodes.

## Arms

| Arm | Setup | Expected if H-C1 true |
|-----|--------|------------------------|
| T | Dual drive L-low / R-high | success rate ≥ 0.90 |
| C1 | Both halves same band [100,10000] | success rate ≤ 0.60 |
| C2 | Dual drive but success scored with **flipped** inequality `mean_L > mean_R` | rate ≤ 0.60 |
| C3 | Diagnostic: both regions form ≥1 level≥4 node | ≥ 0.80 of T trials |

## Locked bars

| ID | Criterion | Threshold |
|----|-----------|-----------|
| B1 | T success rate (`mean_L < mean_R` ∧ both n≥1) | ≥ **0.90** |
| B2 | C1 success rate | ≤ **0.60** |
| B3 | C2 flipped success rate | ≤ **0.60** |
| B4 | T fraction with both regions populated (n≥1 each) | ≥ **0.80** |

## Protocol (locked)

| Parameter | Value |
|-----------|--------|
| *N* per side | **300** |
| *T* ticks | **800** |
| Official seeds | **{17, 29, 43}** (held out from design probe 13/37) |
| Trials per seed | **4** |
| r_1 / r_2 / freq_tol | 5 / 20 / 0.030 |
| speeds | 5–20 |
| lambda_gen/dec | 0 |

## Time budget

| Phase | Estimate | 2× ceiling |
|-------|----------|------------|
| Full (~36 worlds × ~5–8 s) | ≤ 12 min | 24 min |
| Smoke (seed 17, 2 trials, T=300) | ≤ 2 min | 4 min |

## Prediction

Prior ≈ 0.65 PASS; NULL risk = sparse matter (B4) or same-band still separates by noise (B2).

## What is NOT claimed

- Named “light”/“sound” understanding  
- Behavioural probe selectivity (BP-C2)  
- Brain-level cognition  

## Runner

`tools/run_bp_c1_collection_talent.py`  
`~/.eqmod/bet/BP-C1/result.json`  
Live 3D default ON (`--headless` to disable).

## RESULT

**Verdict: NULL** (2026-07-19)  
Artifact: `~/.eqmod/bet/BP-C1/result.json`  
Seeds {17,29,43} · 4 trials/seed · T=800  

| Bar | Value | thr | ok |
|-----|------:|-----|:--:|
| B1 T specialisation | **0.417** | ≥0.90 | no |
| B2 C1 same-band | **0.000** | ≤0.60 | yes |
| B3 C2 flipped | **0.000** | ≤0.60 | yes |
| B4 both populated | **0.500** | ≥0.80 | no |

### Diagnosis (Pattern-01)
- Mechanism (dual drive) fires; controls behave (same-band does not fake specialisation).
- **Binding constraint:** insufficient level≥4 matter in *both* halves within T=800 / N=300 — half of trials leave a side empty; when both populate, specialisation only ~42%.
- Not a bar-tuning case → open **BP-C1b** with denser/longer formation (new amendment), not edit C1.

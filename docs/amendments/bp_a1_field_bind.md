# BP-A1 — Local density field enables binding (Rung A)

**Programme:** Belief path (`docs/BELIEF_PATH.md`)  
**Status:** PRE-REGISTERED (bars locked before official run data)  
**Date locked:** 2026-07-19  
**ID:** BP-A1  

---

## Hypothesis

**H-A1.** Free vibrations form a **local density field** that enables electron binding: at fixed particle count *N* and fixed frequency multiset (pair-rule eligible),

1. **High local density** (spatial cluster) yields high electron formation,  
2. **Low local density** (position-shuffled / sparse, same *N* and freqs) yields substantially fewer electrons,  
3. **High density with frequency scramble** (pair rule broken; density/energy preserved) yields substantially fewer electrons.

So binding is not “particles exist somewhere in the box”; it requires a **local field of free vibrations** *and* the pair rule. Under current primitives the field is operationalized as **local free-vibration density** (count in a ball), not a separate energy scalar — if that is all the medium has, naming it “energy field” is fair only if density is load-bearing.

**NULL means:** sparse ≈ cluster (density decorative) **or** scramble ≈ cluster (pair rule not required) — then the belief’s “field binds at a point” is not supported under these primitives.

## Mechanism (no new physics)

- Plant *N* free vibrations; no hand-built electrons.  
- **Eligible freqs:** alternate `f` and `f·1.08` with opposite polarity (satisfies 8% table when they meet).  
- **Cluster:** positions ~ Normal(centre, σ=2) in box 60³.  
- **Sparse:** uniform in box.  
- **Scramble:** cluster geometry + frequencies i.i.d. log-uniform [100, 10000] (pair matches rare).  
- Advance physics *T* ticks; count alive level-1 electrons.

## Arms

| Arm | Setup | Expected if H-A1 true |
|-----|--------|------------------------|
| T | cluster + eligible freqs | high electron count |
| C1 | sparse + eligible freqs | ≪ T |
| C2 | cluster + scrambled freqs | ≪ T |
| C3 | threshold check: N_lo=10 sparse vs cluster | sparse ~0; cluster forms some |

## Locked acceptance bars

| ID | Criterion | Threshold |
|----|-----------|-----------|
| B1 | Mean electrons under T / *N* | ≥ **0.35** |
| B2 | Mean electrons C1 / mean electrons T | ≤ **0.55** |
| B3 | Mean electrons C2 / mean electrons T | ≤ **0.55** |
| B4 | Mean electrons at N_lo=10: sparse ≤ **1.0** and cluster ≥ **3.0** | both |

### Verdict rule

- **PASS** — B1–B4 all met.  
- **NULL** — any bar unmet; harness valid.  
- **FAIL** — crash / budget overrun.

No post-hoc threshold tuning. No changing *N*/σ after official data.

## Protocol numbers (locked)

| Parameter | Value |
|-----------|--------|
| *N* (main) | **40** |
| *N_lo* (B4) | **10** |
| *T* ticks | **200** |
| Official seeds | **{13, 37, 41}** (held out from design probes on 11/23/31) |
| Trials per seed per arm | **4** (different plant RNG offsets) |
| box | (60, 60, 60) |
| r_1 / r_2 / freq_tolerance | 5.0 / 28.0 / 0.030 |
| cluster σ | 2.0 |
| base f | 500.0 ; partner 500×1.08 |
| lambda_gen/dec | 0 |
| speed magnitude | 15.0 |

### Design-time note

N-sweeps on seeds {11,23,31} informed feasibility; **official sample is only seeds {13,37,41}.**

## Time budget

| Phase | Estimate | Hard 2× |
|-------|----------|---------|
| Full (~3 seeds × 4 trials × 4 arms × 200 ticks) | ≤ 5 min | 10 min |
| Smoke (1 seed, 2 trials, T=100) | ≤ 1 min | 2 min |

## Prediction (pre-data)

Prior ≈ 0.70 PASS: density + pair rule jointly required; main NULL risk = held-out seeds weaker separation (B2/B3).

## What is NOT claimed

- A new energy primitive beyond free-vibration density  
- Molecules / talent / brain  
- That the 8% table is “discovered” physics (it remains engineered)

## Runner

`tools/run_bp_a1_field_bind.py`  
Results: `~/.eqmod/bet/BP-A1/result.json`

## RESULT

**Verdict: PASS** (2026-07-19)  
Runner: `tools/run_bp_a1_field_bind.py`  
Artifact: `~/.eqmod/bet/BP-A1/result.json`  
Official seeds: {13, 37, 41} · 4 trials/seed · T=200 · N=40  

| Bar | Value | Threshold | Pass? |
|-----|------:|-----------|:-----:|
| B1 T electrons/N | **0.483** | ≥ 0.35 | yes |
| B2 C1/T ratio (sparse) | **0.388** | ≤ 0.55 | yes |
| B3 C2/T ratio (scramble) | **0.241** | ≤ 0.55 | yes |
| B4 N=10 cluster / sparse | **4.25 / 0.83** | ≥3.0 / ≤1.0 | yes |

Means: T=19.3 e⁻, sparse=7.5, scramble=4.7 (N=40). Smoke also PASS.

### Scope (honest)
- Local **free-vibration density** is load-bearing for binding at fixed *N* and freqs.
- Pair rule remains necessary (scramble kills most binding even in a cluster).
- Field is operationalized as density of free vibrations — **not** a new energy primitive beyond what the physics already has.
- Supports the belief’s “at a certain density/energy, binding happens” as density-gated encounters + 8% table — not as a separate mysterious field equation.

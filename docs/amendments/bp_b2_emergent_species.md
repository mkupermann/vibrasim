# BP-B2 — Emergent molecule species carry drive identity (Rung B follow-on)

**Programme:** Belief path (`docs/BELIEF_PATH.md`)  
**Status:** PRE-REGISTERED (bars locked before official run data)  
**Date locked:** 2026-07-19  
**ID:** BP-B2  
**Depends on:** BP-B1 PASS (composition can be a content channel under engineered write)

---

## Hypothesis

**H-B2.** Two different **frequency drives** on free vibrations, with **no hand-planted molecules**, produce emergent level-5+ molecule populations whose **composition fingerprints** (atom decades) allow decoding the drive label above chance after formation time *T* — while matched controls fail.

This upgrades BP-B1 from engineered write to **emergent write**: the world writes the content; we only inject vibration spectra (engineered ports of drive, not planted labels).

## Mechanism

- **Drive A (low band):** `freq_min=100`, `freq_max=2000`, log distribution  
- **Drive B (wide/high band):** `freq_min=500`, `freq_max=10000`, log distribution  
- Config base: session-3b-like productive binding (`box=60³`, `n_initial=800`, `r_2=28`, `freq_tolerance=0.030`, no ambient regen)  
- **No** `allocate_node` of molecules or atoms for the label  
- **Readout:** for all alive level-5+ nodes, walk composition → atom decades;  
  `mean_decade = mean(all atom decades across molecules)`.  
  **Decode (locked):** `mean_decade < 3.5` → **A**, else → **B**.  
  If zero molecules → decode fails (incorrect).

## What is NOT claimed

- Collections with talent (Rung C)  
- Field-threshold binding law (Rung A)  
- That drive bands are “unknown physics” — bands are chosen experimental conditions  
- Open-ended language or cognition  

## Arms

| Arm | Description | Expected if H-B2 true |
|-----|-------------|------------------------|
| T | Drive A vs B; decode by mean molecule decade | acc ≥ 0.90 |
| C1 | Same physical band for both labels (`100–10000`); labels still A/B | acc ≤ 0.60 |
| C2 | Post-hoc **shuffle** of T labels vs fingerprints (no new physics) | acc ≤ 0.60 |
| C3 | Decode by **molecule count only** (`n_mol >= median` → B else A) on T physics | acc ≤ 0.60 |
| C4 | Diagnostic: fraction of T trials with `n_mol >= 1` | ≥ 0.80 (bar B5) |

## Locked acceptance bars

| ID | Criterion | Threshold |
|----|-----------|-----------|
| B1 | Treatment (T) decode accuracy | ≥ **0.90** |
| B2 | C1 accuracy | ≤ **0.60** |
| B3 | C2 accuracy | ≤ **0.60** |
| B4 | C3 accuracy | ≤ **0.60** |
| B5 | T trials with ≥1 molecule | ≥ **0.80** |

### Verdict rule

- **PASS** — B1 and B5 met, and B2–B4 all met.  
- **NULL** — any required bar unmet; harness valid; diagnose.  
- **FAIL** — crash, budget overrun, or indefensible control pattern.

**No post-hoc threshold tuning.** No changing drive bands after official data.

## Protocol numbers (locked)

| Parameter | Value |
|-----------|--------|
| Trials per seed *N* | 20 (10 A + 10 B, shuffled) |
| Official seeds *S* | **{11, 23}** (held out from exploratory probes that used 42/7/99) |
| Formation ticks *T* | **1200** |
| n_initial_vibrations | 800 |
| box_size | (60, 60, 60) |
| r_1 / r_2 / freq_tolerance | 5.0 / 28.0 / 0.030 |
| lambda_gen / lambda_dec / lambda_dec_mol | 0 |
| Decode threshold | mean_decade **&lt; 3.5** → A else B |

### Design-time note (not official data)

Exploratory probes on seeds {42,7,99} suggested band separation is feasible; **official verdict uses only seeds {11,23}** so those probes are not the acceptance sample.

## Time budget

| Phase | Estimate | Hard 2× |
|-------|----------|---------|
| Full protocol (~80 physics worlds × ~5 s) | ≤ 15 min | 30 min |
| Smoke (N=4, T=400, seed 11) | ≤ 2 min | 4 min |

Overrun → FAILED post-mortem in LOGBOOK.

## Prediction (pre-data)

Prior ≈ 0.60 PASS if held-out seeds behave like exploratory; main NULL risk = molecule non-formation (B5) or C3 molecule-count accidentally separating drives.

## Runner

`tools/run_bp_b2_emergent_species.py`  
Results: `~/.eqmod/bet/BP-B2/result.json`

## RESULT

**Verdict: PASS** (2026-07-19)  
Runner: `tools/run_bp_b2_emergent_species.py`  
Artifact: `~/.eqmod/bet/BP-B2/result.json`  
Official seeds: {11, 23} · N=20/seed · T=1200  

| Bar | Value | Threshold | Pass? |
|-----|------:|-----------|:-----:|
| B1 treatment acc | **1.000** | ≥ 0.90 | yes |
| B2 C1 same-band acc | **0.475** | ≤ 0.60 | yes |
| B3 C2 shuffle acc | **0.550** | ≤ 0.60 | yes |
| B4 C3 count-only acc | **0.375** | ≤ 0.60 | yes |
| B5 mol formation | **1.000** | ≥ 0.80 | yes |

### Harness note
First full attempt crashed with `RecursionError` in composition walk (cyclic CSR under molecule fusion). Fixed with cycle-safe depth-limited walk in the runner only — **bars unchanged**. Re-run completed cleanly.

### Scope (honest)
- **Emergent write works:** different vibration frequency drives produce molecule decade structure that decodes drive identity (mean decade ≶ 3.5) at 100% on held-out seeds.
- Same-band control, label shuffle, and molecule-count-only readout stay near chance — content is in **composition**, not count or label noise.
- Drive bands are **chosen experimental conditions** (engineered ports of stimulation), not discovered physics. Internals (which species form) emerge.
- Does **not** show collection talent (Rung C) or field→bind law (Rung A).

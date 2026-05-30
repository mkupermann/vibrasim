# BET-098 — Sharp Spatial Separation: Clean Persistent Selectivity

Pre-registered: 2026-05-31 (BEFORE any run). Continuation of BET-097, which got
contrast ✓, selective write ✓, and an improved hold, but failed clean persistent
selectivity because control-region boundary bridges caught stim-vibration tails
(r_2=10 sensing; injection σ=2; region edges ~1 r_2 apart) and the well latched
that contamination.

## The fixes (spatial sharpness, not drive/threshold)

1. **Tighter injection: σ ≈ 1.0** (was 2.0) so frozen stim vibrations stay near
   x≈7.5 and do not reach the region boundary (~x15).
2. **Measure region CORES only: half ≈ 3.0** (was 7.0), i.e. stim core
   x∈[4.5,10.5], control core x∈[19.5,25.5], with a guard gap around the midline
   so boundary bridges never enter either readout.

Everything else identical to BET-097 (rectified one-sided drive, frozen vel=0
injection, true starve, blank-slate bridges, flux_ref=1000).

## Acceptance bars (locked pre-run — same memory bars)

| ID | Criterion | Bar |
|----|-----------|-----|
| T98a | Contrast EXISTS (gate) | during STIM, median stim-core flux >= 1.5× median control-core flux |
| T98b | Selective latch | stim-core bridge mean > mid (3) AND control-core mean < mid during STIM |
| T98c | Hysteresis memory | after STIM stops AND field cleared, >= 2000 s later stim-core mean > mid AND control-core mean < mid |
| T98d | Negative control FAILS | uniform frozen injection does NOT meet T98c |

PASS = T98a, T98b, T98c hold AND uniform control fails T98c.
**PASS = the first selective, persistent, content-bearing memory the substrate
has held.**

Stopping rule (from BET-097): if clean persistent selectivity STILL fails, the
flux-addressing line is a QUALIFIED PARTIAL SUCCESS (selective write ✓, clean
persistent recall ✗) and the work pivots to STDP/BTSP correlation addressing
(BET-099). No further regime iteration past BET-098.

## Run design

Identical to BET-097 plus: injection σ=1.0; region readout half=3.0. Warmup
3000 s → starve + cull + blank → STIM 3000 s (frozen σ=1 confined, 40/step stim;
control arm 20/20) → clear field → POST ≥ 2000 s. Same rng_seed across arms.

## RESULT (2026-05-31): NULL — sharp separation fixed contamination; HOLD fails via bridge turnover → PIVOT

Verdict: **NULL** (T98c). The sharp separation worked for its target (T98b is the
cleanest selective latch yet), but persistent recall still fails — and per the
pre-registered stopping rule this ends the flux-addressing line.

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T98a contrast metric | ✗ (artifact) | stim/ctrl flux read 0/0 — the tightly-clustered (σ=1) frozen vibrations are CONSUMED into nodes, so free-vibration flux self-extinguishes by sampling time. The latch still formed (T98b), so contrast existed transiently; the metric just can't see it after consumption. |
| T98b selective latch (STIM) | ✓ **cleanest yet** | stim-core 3.89 vs control-core 1.72 — clean separation, boundary contamination gone (the σ/core fix worked). |
| T98c hysteresis hold | ✗ | POST: stim-core 3.41→2.50, control-core 2.07→2.82, converging ~2.7. The stored pattern erodes. |
| T98d control fails | ✓ | uniform arm non-selective. |

### Why the hold fails now — bridge turnover

With rectified drive and POST flux=0, the well should freeze the pattern. It
doesn't, because **bridges turn over**: core bridge counts swing 12–35 across the
run; bridges break and reform, and new ones are born at strength 1.0 (weak),
overwriting any latched value. The memory is stored per-bridge, but bridges are
not permanent enough to hold it — even though their host ATOMS are (BET-091).
The latched pattern is continually diluted by fresh weak bridges.

### Consolidated finding of the flux-addressing line (BET-089→098)

- Persistent lattice: SOLVED (BET-091).
- Selective WRITE: SOLVED (BET-096/097/098 — localized stimulus latches the
  stimulated region, control stays weak, cleanly with sharp separation).
- Persistent selective RECALL: NOT achieved. The per-bridge bistable state is
  eroded by bridge turnover and by stimulus self-consumption. Storing memory in
  individual bridge strengths is too fragile against the substrate's own
  bond/vibration dynamics.

This is a **qualified partial success**, exactly the stopping-rule branch.

### PIVOT (BET-099)

Per the pre-registered stopping rule: pivot to **STDP/BTSP correlation
addressing** — the charter's designed learning primitive. Instead of storing
memory in per-bridge flux state, store it in spike-timing-correlation weights
between co-active atoms (enable neuron_dynamics + stdp/btsp). Correlation-based
weights are the substrate's intended, turnover-robust memory substrate. No
further flux-line regime iteration.

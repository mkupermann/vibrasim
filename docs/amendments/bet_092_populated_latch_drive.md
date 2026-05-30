# BET-092 — Fixed-Reference Latch Drive for a Populated Lattice

Pre-registered: 2026-05-30 (BEFORE any run under this design).
Follows BET-091: persistence is solved (atoms live ~1500 s, ~68 bonded), but the
bistable latch never fired because its drive is **relative to the moving mean
flux** — on a populated lattice the mean rides up with the stimulus, the
stim/mean ratio stays ~1, and no bridge crosses the barrier.

## Mechanism under test (within substrate primitives)

`apply_bistable_plasticity` gains a drive mode (cfg.bistable_drive_mode):
- `relative` (default, unchanged): drive = flux_gain·(flux/mean_flux − 1).
- `absolute` (this amendment): drive = flux_gain·(flux/flux_ref − 1), where
  flux_ref is a FIXED reference. Bridges with flux above flux_ref are pushed
  toward the STRONG well; bridges below it decay toward WEAK. This reuses the
  already-existing `bistable_flux_ref` knob (designed for exactly this, unused
  since BET-089 v2). No new dynamics.

This is the natural latch for a persistent, place-stable lattice: a fixed
threshold the stimulated region clears and the resting region does not.

## flux_ref selection — pre-registered RULE (not a tuned value)

flux_ref is set by a rule fixed before the stim test, derived from the
substrate's own resting statistics, NOT from the stimulated result:

> Run a no-stimulus baseline on the persistent lattice (fusion_bond_block=3,
> anchoring on) for 4000 sim-s. Over the last 2000 s, collect per-bridge flux
> (density_i·density_j, same quantity the latch uses). Set
> **flux_ref = the 90th percentile of that resting per-bridge flux.**

Rationale: drive up only bridges experiencing flux above the resting 90th
percentile — i.e. clearly above what the unstimulated substrate produces. The
value is computed mechanically by this rule and recorded below before the stim
test is run.

## Acceptance bars (locked pre-run)

| ID | Criterion | Bar |
|----|-----------|-----|
| T92a | Selective latch during STIM | absolute-drive arm: stim-region bridge mean > `bistable_mid` (3) AND control-region mean < `bistable_mid` |
| T92b | Selective memory persists | >= 2000 s after stimulus stops, stim-region mean still > mid AND control < mid |
| T92c | Bimodal | bridge strengths cluster near low or high, not the middle |
| T92d | Negative control FAILS | relative-drive arm (cfg.bistable_drive_mode='relative', the BET-091 setting, all else identical) does NOT meet T92b — required for the absolute-drive result to be defensible |

PASS = T92a, T92b, T92c hold AND the relative-drive control fails T92b.
NULL is valid: e.g. absolute drive latches but not selectively (flux_ref too
low → control also crosses), which would point at the flux contrast, not the
drive form.

## Run design

- Substrate identical to BET-091 (fusion_bond_block=3, anchor_damping=0.7,
  persistence on). Same rng_seed across arms.
- Arm A (ON): bistable_drive_mode='absolute', bistable_flux_ref = value from the
  rule above. Arm B (control): bistable_drive_mode='relative'.
- Localized slow-vibration stimulus drives the left region during STIM; right
  region undriven. Measure region means through STIM and a >= 2000 s POST window.

## Time budget

Realistic: 12 min wall (baseline probe + two arms). Ceiling: 24 min. Overrun →
FAILED post-mortem in LOGBOOK.md.

## flux_ref VALUE (filled from baseline probe, before stim test)

Baseline probe (tools/_probe092_flux.py, no stimulus, 8480 resting per-bridge
samples over the last 2000 s): mean 8170, p50 8096, **p90 9785**, p99 11312,
max 13456. Per the rule, **flux_ref = 9785.0**. (Recorded before the stim test;
git diff is the proof it was set from resting stats, not the stimulated result.)

## RESULT (2026-05-30): NULL — and it relocates the real blocker to flux CONTRAST

Verdict: **NULL**. But it cleanly isolates the true constraint.

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T92a selective latch (STIM) | ✗ | absolute arm: stim 0.75 vs ctrl 0.74 — identical, both collapsed below the weak well. No latch, no selectivity. |
| T92b selective memory (POST) | ✗ | follows from T92a. |
| T92c bimodal | ✓ (trivially) | everything collapsed to low; mid-band empty. |
| T92d control fails | ✓ | relative arm non-selective (stim≈ctrl≈1.0–1.8), as in BET-091. |

### What actually happened

The absolute drive used flux_ref = resting p90 = 9785. In the stim run, **both
regions' bridge flux sat at the same ~resting level**, below 9785, so every
bridge got negative drive and decayed to ~0.75 (below low=1). The threshold was
fine; there was simply **no signal to threshold**: stim and control flux are
indistinguishable (0.75 vs 0.74). The relative arm shows the same thing from the
other side — stim and control means track each other (1.0–1.8), never separating.

### The relocated constraint: no spatial flux contrast

Flux is `density_i·density_j`, and the substrate carries ~500 ambient vibrations
(vibration_soft_cap) in a 30³ box. Every atom is bathed in high background
density (~80–115 neighbours → flux ~8000) regardless of stimulus. The localized
stimulus (20 vibrations / 4 steps) is a small perturbation on that large
background, so it produces **no measurable flux gradient** between the
stimulated and control regions. Both latch mechanisms (relative and absolute)
are downstream of a flux contrast that does not exist. This is neither a
structure problem (solved, BET-091) nor a drive-form problem (both forms tested
here) — it is a **stimulus-to-ambient signal-to-noise** problem.

### Finding

Persistence + a working latch are not enough without a **spatial flux contrast**
for the latch to read. The ambient vibration density saturates local flux and
washes the stimulus out. The next lever is the stimulus/ambient ratio, not the
latch dynamics.

### Next direction (new pre-registered amendment, no tuning here)

BET-093: create a real flux gradient — lower the ambient density
(vibration_soft_cap / lambda_gen) and/or concentrate the stimulus, so the
stimulated region's flux clearly exceeds the resting field. Pre-register a
direct check that a stim/control flux contrast EXISTS before testing whether the
latch reads it. The absolute-drive mode added here is kept (it is the correct
latch once a contrast exists); changing bistable_* post-result to force T92 is
refused.

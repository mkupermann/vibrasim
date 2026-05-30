# BET-094 — Confined Stimulus: a Readable Flux Gradient + Hysteresis Memory

Pre-registered: 2026-05-31 (BEFORE any run under this design).
Follows BET-093's REGIME-NULL (no gradient: vibrations delocalized) and the
pre-probe (tools/_probe094_gradient.py) which showed the fix:

> Zero-velocity, high-rate confined injection sustains a gradient: stim-region
> flux ~2000–2580 vs control ~340–660 (ratio 2.5–6.4×), free_vib steady at the
> soft cap. Delocalization is defeated by injecting vibrations with ~0 velocity
> so they stay where placed.

## Mechanism under test (within substrate primitives)

Same persistent lattice (BET-091: fusion_bond_block=3, anchoring on) and
absolute-drive latch (BET-092). The ONLY change vs BET-093 is the injection:
vibrations are placed in the stim region with **~0 velocity** at **high rate**
(40/step) so they do not diffuse, sustaining a real spatial flux gradient.

Phases: warmup (build lattice) → starve ambient → **calibrate** (1000 steps, no
stim, measure resting flux → flux_ref) → **STIM** (confined injection) → **clear
field** (cull free vibrations so flux returns to baseline) → **POST** (no stim).
Clearing the field in POST is what makes this a true memory test: if stim-region
bridges stay STRONG after the driving flux is gone, that is hysteresis (memory),
not flux being sustained.

## flux_ref selection — pre-registered RULE

> flux_ref = 90th percentile of per-bridge flux over the 1000-step CALIBRATE
> window (starved, no stimulus) — the resting field level. Computed before STIM;
> recorded in RESULT.

## Acceptance bars (locked pre-run)

| ID | Criterion | Bar |
|----|-----------|-----|
| T94a | Contrast EXISTS (gate) | during STIM, median stim-region per-bridge flux >= 1.5× median control flux |
| T94b | Selective latch | given T94a, stim-region bridge mean > `bistable_mid` (3) AND control mean < mid during STIM |
| T94c | Hysteresis memory | after STIM stops AND the field is cleared, >= 2000 s later stim-region mean still > mid AND control < mid (latched despite flux gone) |
| T94d | Negative control FAILS | uniform confined injection (both regions equally → no contrast) does NOT meet T94c |

PASS = T94a, T94b, T94c hold AND the uniform control fails T94c.
This would be the FIRST selective, persistent (content-bearing) memory the
substrate has held — write, remove stimulus, read back. NULL remains valid: if
T94a holds but T94b fails, the latch still can't read a real gradient (back to
drive dynamics); if T94c fails after T94b holds, the latch doesn't survive field
removal (back to the well depth / hysteresis).

## Run design

- Warmup 3000 s; starve (lambda_gen→0.0005, cull free vibs to 10%); calibrate
  500 s; STIM 3000 s (confined vel≈0, 40/step into left region); clear field;
  POST >= 2000 s.
- Negative control arm: identical, but confined injection split equally into
  both regions (no spatial contrast).
- Same rng_seed across arms; only the stimulus spatial pattern differs.

## Time budget

Realistic: 12 min wall. Ceiling: 24 min.

## flux_ref VALUE (filled at run time, before STIM verdict)

_(filled by the calibrate window)_

## flux_ref VALUE (filled at run time, before STIM verdict)

Calibrate p90 = 7411.6 — anomalously high (see below): the "starved" field had
already refilled uniformly to the soft cap during the calibrate window.

## RESULT (2026-05-31): REGIME-NULL — calibrate window + residual regen erased the starve

Verdict: **REGIME-NULL**. T94a contrast gate failed (ratio 1.16), so T94b/c are
not interpretable — the pre-registered "regime didn't create a gradient" branch.

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T94a contrast (>=1.5×) | ✗ | STIM stim-flux 7332 vs ctrl-flux 6311, **ratio 1.16**. No gradient. |
| T94b / T94c | n/a | not interpretable without contrast. |
| T94d control fails | ✓ (trivially) | uniform arm identical. |

### Precise cause (Pattern 01: the mechanism works; my regime broke it)

The pre-probe proved a confined zero-velocity stimulus sustains a 2.5–6×
gradient. BET-094 failed to reproduce it because of two harness faults that
re-homogenised the field BEFORE the stimulus could dominate:

1. **`lambda_gen=0.0005` is not starved.** With `lambda_dec=0`, ambient
   regeneration injects ~6 vibrations/step regardless — refilling the culled
   field to the 500 soft cap within ~75 steps.
2. **The 1000-step calibrate window** (no stim) gave that regeneration time to
   refill the field *uniformly* to the cap. By the time confined injection
   started, the shared 500-vibration budget was already full and even across
   both regions, so the stimulus could not create a density gradient
   (stim-flux ≈ ctrl-flux ≈ resting). The probe worked precisely because it
   injected *immediately* into a freshly-culled field, letting injection own the
   budget (stim ~2000 vs ctrl ~400).

(Also visible: WARM bridges saturated at 7.0 because the default flux_ref=1000
sits far below full-ambient flux ~8000 — every bridge driven to the strong well.
Harmless to the lattice, but shows the absolute drive is highly threshold
-sensitive to the flux regime.)

### Finding

The contrast is achievable (probe), but requires the stimulus to OWN the shared
vibration budget: true `lambda_gen=0` (no competing uniform regen) and immediate,
continuous confined injection with no uniform-refill window. This is a regime
implementation fix, not a mechanism or threshold change.

### Next direction

BET-095: reproduce the probe's winning conditions inside the full hysteresis
protocol — `lambda_gen=0`, cull control field, inject confined stimulus
continuously from the moment of cull, fixed flux_ref derived from the probe
(control ~400–660, stim ~2000 → flux_ref=1000). Same pre-registered hysteresis
bars. New amendment number per the retry rule (never edit a FAILED/NULL bar).

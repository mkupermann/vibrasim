# BET-095 — Confined Stimulus, Starved Field: Selective Hysteresis Memory

Pre-registered: 2026-05-31 (BEFORE any run). Retry of BET-094 with the regime
fixed (new amendment number per the retry rule; BET-094's NULL bars are not
edited). Same hypothesis and bars; only the regime that produces the gradient is
corrected per BET-094's diagnosis.

## Why BET-094 was REGIME-NULL, and the fix

The pre-probe proved a confined zero-velocity stimulus sustains a 2.5–6× flux
gradient. BET-094 lost it because `lambda_gen=0.0005` still regenerated ~6
vib/step and a 1000-step calibrate window let the field refill uniformly to the
500 soft cap before the stimulus could own the budget. Fix:
- **`lambda_gen = 0` at starve** — no competing uniform regeneration.
- **No calibrate window** — cull the field and begin confined injection in the
  same step, so the stimulus owns the shared vibration budget.
- **Fixed `flux_ref = 1000`** — between the probe's control level (~400–660) and
  stim level (~2000); set pre-run from prior probe data, not from this result.

## Mechanism (unchanged from BET-094, within primitives)

Persistent lattice (BET-091) + absolute-drive bistable latch (BET-092). Confined
zero-velocity injection into the stim region only; with the field starved, the
control region holds ~0 vibrations (flux ≈ 0) while the stim region carries the
whole budget (flux ≈ 2000). The latch drives stim bridges to the STRONG well and
lets starved control bridges decay to WEAK. Field cleared in POST → a persisting
stim latch is hysteresis (memory), not sustained flux.

## Acceptance bars (locked pre-run — same as BET-094)

| ID | Criterion | Bar |
|----|-----------|-----|
| T95a | Contrast EXISTS (gate) | during STIM, median stim-region per-bridge flux >= 1.5× median control flux |
| T95b | Selective latch | given T95a, stim-region bridge mean > `bistable_mid` (3) AND control mean < mid during STIM |
| T95c | Hysteresis memory | after STIM stops AND field cleared, >= 2000 s later stim mean still > mid AND control < mid |
| T95d | Negative control FAILS | uniform confined injection (both regions) does NOT meet T95c |

PASS = T95a, T95b, T95c hold AND uniform control fails T95c. PASS = the first
selective, persistent, content-bearing memory the substrate has held.

## Run design

- Warmup 3000 s (full ambient, build lattice). At warmup end: `lambda_gen→0`,
  cull all free vibrations, begin confined injection (vel≈0, 40/step into stim;
  control arm splits 20/20 both regions). STIM 3000 s. Clear field. POST ≥ 2000 s.
- Same rng_seed across arms; only the stimulus spatial pattern differs.

## Time budget

Realistic: 12 min. Ceiling: 24 min.

## RESULT (2026-05-31): REGIME-NULL — two compounding harness bugs (both fixable)

Verdict: **REGIME-NULL**. T95a contrast gate failed (ratio 1.12; stim-flux 6612,
ctrl-flux 5929). Diagnosis (Pattern 01) found two compounding causes:

1. **`vel_scale=0.01` is not zero.** Free vibrations move ballistically with no
   collisions, so even speed ~0.017 carries them ~50 units over the 3000-unit
   STIM phase — across the entire 30-box (periodic). They delocalised into the
   control region; ctrl-flux rose to ~5929 ≈ stim. The pre-probe held a gradient
   only because it used `vel=0.0` exactly (vibrations frozen at injection point).
2. **Warmup pre-latched every bridge to 7.0.** With `flux_ref=1000` far below
   warmup ambient flux (~8000), all bridges were driven to the strong well
   before STIM began. Control entered STIM already saturated — there was no blank
   baseline to write onto. POST shows both regions settling to 5.17, identical.

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T95a contrast | ✗ | ratio 1.12 (vibrations delocalised at vel 0.01) |
| T95b/c | ✗ | control pre-latched at 7.0; no selectivity to read |
| T95d control fails | ✓ (trivially) | uniform arm identical |

### Finding

Spatial flux localization in this substrate requires **vel exactly 0** (any
nonzero velocity homogenizes ballistically over the run) AND a **blank memory
baseline** (bridges must start weak, not pre-latched by warmup ambient). Both are
regime/harness fixes, not mechanism changes.

### Next direction (BET-096) — and a discipline note

BET-096 fixes both: `vel=0.0` exactly, and blank all bridge strengths to the low
well at the warmup→STIM transition so control starts weak. This is the cleanest
shot at a selective latch. **If BET-096 also fails the T9xa contrast/selectivity
gate, the flux-addressing line is exhausted — pivot to STDP/BTSP correlation
addressing (BET-097), which addresses by co-activity between connected atoms
rather than fragile spatial flux fields.** No more regime-whacking past one clean
attempt.

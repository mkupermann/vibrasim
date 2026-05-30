# BET-093 — Flux Contrast: Starve the Ambient Field

Pre-registered: 2026-05-30 (BEFORE any run under this design).
Follows BET-092: persistence + a working latch exist, but the localized
stimulus produces NO spatial flux contrast — ~500 ambient vibrations bathe
every atom in ~8000 background flux, washing the stimulus out. The latch has
no signal to read.

## Mechanism under test (within substrate primitives)

Two-phase regime, no new dynamics — only the existing generation/injection
primitives:
1. **Warmup** (normal density): build the persistent lattice (BET-091:
   fusion_bond_block=3, anchoring on) until ~60+ bonded atoms exist.
2. **Contrast phase**: drop the ambient field — set `lambda_gen` low and cull
   existing free vibrations — then inject the slow-vibration stimulus ONLY into
   the stim region. Now the stim region carries vibrations (high local flux)
   while the control region is starved (low flux). A real spatial gradient.

The absolute-drive latch (BET-092, `bistable_drive_mode='absolute'`) is kept
unchanged; flux_ref is re-derived for the new low-ambient regime by the same
resting-p90 rule (measured in the contrast phase's control region).

## Hypothesis

With the ambient field starved, the localized stimulus creates a stim≫control
flux gradient. The absolute-drive latch reads it: stim-region bridges cross the
barrier and latch STRONG; starved control bridges decay to WEAK. Selective
memory forms and persists.

## Acceptance bars (locked pre-run)

| ID | Criterion | Bar |
|----|-----------|-----|
| T93a | Contrast EXISTS (gate) | during STIM, median stim-region per-bridge flux >= 1.5× median control-region per-bridge flux. If this fails, the regime did not create a gradient and T93b/c are not interpretable (report as regime-NULL). |
| T93b | Selective latch | given T93a, stim-region bridge mean > `bistable_mid` (3) AND control-region mean < `bistable_mid` during STIM |
| T93c | Selective memory persists | >= 2000 s after stimulus stops, stim-region mean > mid AND control < mid |
| T93d | Negative control FAILS | same starved-ambient regime but UNIFORM stimulus (both regions injected equally → no contrast) does NOT meet T93c |

PASS = T93a, T93b, T93c hold AND the uniform-stimulus control fails T93c.
NULL is valid and informative: if T93a holds but T93b fails, the latch cannot
read even a real contrast (back to drive dynamics); if T93a fails, the starve
regime didn't produce a gradient (back to the regime knobs).

## Run design

- Warmup 3000 sim-s (no stim) at lambda_gen=0.006 to build the lattice.
- Contrast phase: lambda_gen -> 0.0005 (≈1/12), cull free vibrations to ~10% of
  the box, then STIM the left region (20 vib / 4 steps) for 3000 sim-s; POST for
  >= 2000 s. Control arm injects the SAME total stimulus split across both
  regions (uniform).
- flux_ref = resting p90 measured on the starved control region before STIM.
- Same rng_seed across arms; only the stimulus spatial pattern differs.

## Time budget

Realistic: 12 min wall. Ceiling: 24 min.

## RESULT (2026-05-30): REGIME-NULL — no gradient forms; vibrations delocalize

Verdict: **REGIME-NULL**. The T93a contrast gate failed, so T93b/c are not
interpretable — exactly the pre-registered branch for "the regime didn't create
a gradient."

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T93a contrast exists (>=1.5×) | ✗ | STIM median stim-flux 6177 vs ctrl-flux 6141 — **ratio 1.01**. No gradient. |
| T93b/T93c | n/a | not interpretable without contrast (per pre-registration). |
| T93d control fails | ✓ (trivially) | uniform arm identical, as expected. |

### What happened (Pattern 01 triage)

The starve mechanism *fired* and had a real local effect: overall flux fell from
~8000 (BET-092, full ambient) to ~6100. But the **target — a spatial contrast —
did not appear**. Starving lowered the field *uniformly*; it did not localize it.

Root cause: **free vibrations delocalize.** They carry velocity (injected
~N(0,0.8) plus thermal) and the box is small and periodic (30³), so injected
vibrations diffuse across the whole volume within the 200-step sampling window,
faster than the fixed atoms consume them. Stim and control regions equilibrate
to the same density (~6100 flux) no matter where the stimulus enters. Lowering
the ambient rate cannot fix this — it changes the level, not the gradient.

### Finding

A **sustained spatial flux gradient is not achievable** by ambient-rate control
in this geometry: vibration mobility homogenizes the field. Spatial-flux
addressing of memory looks structurally unworkable here. The two candidate exits
are (a) confine/slow the stimulus vibrations so a gradient can persist long
enough to read, or (b) abandon spatial-flux addressing and use the substrate's
actual learning primitives — STDP / BTSP correlation between connected atoms,
which address by *co-activity*, not by spatial flux fields.

### Next direction

BET-094: directly probe whether ANY injection scheme (low-velocity / confined
stimulus) sustains a stim≫control flux ratio. If yes, the latch becomes testable
again; if even confined injection homogenizes, pivot to STDP/BTSP correlation
addressing (the charter's designed learning mechanism) in BET-095. Probe before
pre-registering, per Pattern 01.

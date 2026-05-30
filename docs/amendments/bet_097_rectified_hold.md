# BET-097 — Rectified Drive: Make the Selective Latch HOLD

Pre-registered: 2026-05-31 (BEFORE any run). Direct continuation of BET-096,
which achieved selective WRITE (T96a contrast ✓, T96b selective latch ✓) but
failed the hold (T96c) because the two-sided drive erases stored state at zero
flux.

## The one fix

`apply_bistable_plasticity` gains `cfg.bistable_drive_rectified`. When True:

    drive = flux_gain * max(0, flux/flux_ref − 1)

Flux becomes a one-sided WRITE signal — it only pushes strength UP. The bistable
well alone decides hold-vs-decay. When the field is cleared (flux→0), drive=0, so
a bridge in the strong-well basin relaxes to the strong well and STAYS; a bridge
below the barrier relaxes to the weak well. "No input" = "hold", as a latch must.
Everything else is identical to BET-096 (frozen vel=0 stimulus, true starve,
blank-slate bridges, absolute drive, flux_ref=1000).

## Hypothesis

With the rectified drive, the selective write demonstrated in BET-096 persists
after the stimulus is removed: stim-region bridges stay STRONG, control stays
WEAK, for >= 2000 s post-stimulus with the field cleared.

## Acceptance bars (locked pre-run — same memory bars)

| ID | Criterion | Bar |
|----|-----------|-----|
| T97a | Contrast EXISTS (gate) | during STIM, median stim flux >= 1.5× median control flux |
| T97b | Selective latch | stim-region bridge mean > mid (3) AND control mean < mid during STIM |
| T97c | Hysteresis memory | after STIM stops AND field cleared, >= 2000 s later stim mean > mid AND control < mid |
| T97d | Negative control FAILS | uniform frozen injection (both regions) does NOT meet T97c |

PASS = T97a, T97b, T97c hold AND uniform control fails T97c.
**PASS = the first selective, persistent, content-bearing memory the substrate
has held** — write a localized stimulus, remove it, read it back ≥2000 s later,
with a blank control region. Built only from substrate primitives (persistent
lattice + bistable bridges + rectified flux write).

If T97c still fails despite T97a/b, the bistable well is too shallow to hold
against residual dynamics → BET-098 deepens the well (well_k) or widens the
barrier, pre-registered. If the rectified drive breaks the WRITE (T97b fails),
revert and reconsider.

## Run design

Identical to BET-096 plus `bistable_drive_rectified=True`. Warmup 3000 s → starve
(lambda_gen=0) + cull + blank bridges → STIM 3000 s (frozen vel=0 confined
injection, 40/step stim; control arm 20/20 both) → clear field → POST ≥ 2000 s.
Same rng_seed across arms.

## RESULT (2026-05-31): NULL — rectified drive helps the hold, but control is contaminated at the boundary

Verdict: **NULL** (T97c). Contrast ✓ and selective write ✓ again; the rectified
drive measurably improved the hold (stim stayed ~4.3–4.9 in POST vs BET-096's
collapse to ~3.5), but selectivity still decays because the control region
becomes contaminated.

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T97a contrast | ✓ | stim flux 404, control flux 0. |
| T97b selective latch (STIM) | ✓ | stim 3.42→5.51, control 1.29→3.71. |
| T97c hysteresis hold | ✗ | POST: stim ~4.3–4.9 (held — improvement!), but control crept 3.60→4.27 and at times exceeded stim. Not cleanly separated. |
| T97d control fails | ✓ | uniform arm stim≈ctrl throughout. |

### Diagnosis — boundary contamination, not well depth

Ruled out: `apply_flux_plasticity` is gated off (`flux_plasticity_rate=0`), new
bridges form at 1.0 (weak). The only writer is the bistable latch. With rectified
drive and POST flux=0, drive=0 everywhere, so the well should FREEZE the pattern
(stim→strong, control→weak). It didn't stay selective because **control reached
3.71 during STIM** — above the barrier — so the well then latched it strong in
POST. Control rose despite median control flux = 0 because the `r_2 = 10` sensing
radius lets control-region bridges near the boundary (x≈15.5) catch the tail of
the stim vibrations (injected σ=2 around x≈7.5, reaching x≈13–15). The regions
(±7 around centers 7.5 / 22.5) are only ~1 r_2 apart at their edges, so the
sensing zones touch. A handful of boundary bridges crossing the barrier pulls the
control mean up, and the well makes it permanent.

So: the rectified drive is correct (stim held far better). The remaining failure
is **spatial blur at the region boundary**, not the drive form or well depth.

### Next direction (BET-098) — and a stopping rule

BET-098: sharpen the spatial separation — tighter injection (σ≈1.0 so stim
vibrations don't reach the boundary) and measure region CORES only (half≈3,
x∈[4.5,10.5] vs [19.5,25.5], a guard gap around the midline) so boundary bridges
don't pollute the readout. Same rectified drive, same bars.

Stopping rule: BET-098 is the focused spatial-sharpness attempt. If clean
PERSISTENT selectivity still fails, the flux-addressing line is declared a
QUALIFIED PARTIAL SUCCESS (selective write ✓, clean persistent recall ✗) and the
work pivots to STDP/BTSP correlation addressing (BET-099). No further regime
iteration past BET-098.

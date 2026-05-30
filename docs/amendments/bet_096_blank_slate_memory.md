# BET-096 — Frozen Stimulus, Blank Slate: Selective Hysteresis Memory

Pre-registered: 2026-05-31 (BEFORE any run). Final regime fix of the BET-094/095
line (new amendment number per the retry rule). Same hypothesis and bars; the
two diagnosed regime bugs are corrected.

## The two fixes (from BET-095's diagnosis)

1. **`vel = 0.0` exactly.** Free vibrations move ballistically without
   collisions, so ANY nonzero velocity (even 0.01) carries them across the box
   over the run and homogenises the field. Inject with exactly zero velocity so
   stimulus vibrations stay frozen in the stim region — the only condition the
   pre-probe showed sustains a gradient.
2. **Blank slate.** At the warmup→STIM transition, set every bridge strength to
   the low well (`bistable_low`). Warmup ambient otherwise pre-latches all
   bridges to the strong well, leaving no weak baseline to write onto. Blanking =
   "clear the register before writing the memory."

## Mechanism (within primitives)

Persistent lattice (BET-091) + absolute-drive latch (BET-092). After warmup:
`lambda_gen=0`, cull the field, blank all bridges to low, then inject frozen
(vel=0) confined vibrations into the stim region only. Stim region carries the
whole vibration budget (flux high); control holds ~0 (flux ~0). The latch drives
stim bridges over the barrier into the STRONG well; control stays in the WEAK
well. Field cleared in POST → a persisting stim latch is hysteresis (memory).

## Acceptance bars (locked pre-run — same construct as BET-094/095)

| ID | Criterion | Bar |
|----|-----------|-----|
| T96a | Contrast EXISTS (gate) | during STIM, median stim-region per-bridge flux >= 1.5× median control flux |
| T96b | Selective latch | given T96a, stim-region bridge mean > `bistable_mid` (3) AND control mean < mid during STIM |
| T96c | Hysteresis memory | after STIM stops AND field cleared, >= 2000 s later stim mean > mid AND control < mid |
| T96d | Negative control FAILS | uniform frozen injection (both regions) does NOT meet T96c |

PASS = T96a, T96b, T96c hold AND uniform control fails T96c. PASS = the first
selective, persistent, content-bearing memory the substrate has held.

If T96a still fails (no contrast even at vel=0) OR T96b fails given contrast, the
flux-addressing line is exhausted → pivot to STDP/BTSP correlation addressing
(BET-097). This is the one clean attempt; no further regime-whacking.

## Run design

Warmup 3000 s (full ambient, build lattice). Transition: lambda_gen→0, cull
field, blank bridges to low. STIM 3000 s (frozen confined injection, vel=0,
40/step into stim; control arm splits 20/20). Clear field. POST ≥ 2000 s. Same
rng_seed across arms.

## RESULT (2026-05-31): NULL — but selective WRITE achieved for the first time

Verdict: **NULL** (T96c failed), but T96a and T96b passed — the substrate
selectively wrote a localized memory for the first time in the chain. The only
failure is the hold.

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T96a contrast | ✓ | stim flux 404, control flux **0** — a clean gradient (vel=0 froze the stimulus in place; true starve emptied control). |
| T96b selective latch (STIM) | ✓ **first time** | stim 3.14→5.30 (over barrier mid=3); control 0.77→~3.1 (mostly below). Selective write. |
| T96c hysteresis hold (POST) | ✗ | after field cleared, stim and control both drift to ~3.5 and converge — the latch leaks. |
| T96d control fails | ✓ | uniform arm: stim≈ctrl throughout, never selective. |

### Why the hold leaks — a real mechanism flaw

The drive is `flux_gain·(flux/flux_ref − 1)`. At **flux = 0 (POST), drive =
−flux_gain = −0.3** — maximally negative. So once the field is cleared, EVERY
bridge is actively pushed *down*. At a latched stim bridge (s≈5.3) the strong-well
restoring force is only ≈ +0.28, slightly less than the −0.3 drive, so latched
bridges leak out of the strong well and drift back toward the barrier; control
creeps up to meet them. **Absence of flux erases the memory instead of letting
the bistable well hold it.** A latch must treat "no input" as "hold," not as
"push down."

### Finding

Selective WRITE works (contrast + barrier crossing). The hold fails because the
drive is two-sided: it erodes stored state whenever flux falls below flux_ref.
This is a drive-form flaw, not a structure, contrast, or scale problem.

### Next direction (BET-097)

Rectify the drive: `drive = flux_gain·max(0, flux/flux_ref − 1)` — flux only
writes UP; the bistable well alone decides hold-vs-decay. With rectified drive,
POST flux=0 → drive=0 → stim bridges relax INTO the strong well (stay), control
relax INTO the weak well (stay) → hysteresis holds. This is NOT the STDP-pivot
branch (selective write already works); it continues the flux line with a
one-line, principled drive correction. Pre-registered as BET-097 with the same
memory bars.

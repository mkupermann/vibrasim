# BET-090 — Anchored Selective Memory

Pre-registered: 2026-05-30 (BEFORE any run under this design).
Builds directly on BET-089's registered next step: *"anchor a formed shell
(freeze positions once closed) so its bridges have stable identities. Then
the three verified mechanisms can be composed and tested."*

## The blocker this targets

BET-089 confirmed the bistable latch (hysteresis = memory) but could NOT
show **selective** memory: stimulated-region bridges strong, control-region
bridges weak. Root cause, shared with BET-087/088: the handful of bridges
**drift between regions**. A bridge that latches in the stim region migrates
into the control region (and vice versa), so there is no stable place-identity
to read out. The latch works; the *address* does not hold still.

## Mechanism (the change under test)

`apply_structural_anchoring` (world/bridges.py): an atom that has held
`k_bond_count >= anchor_bond_min` continuously for `anchor_age` sim-seconds
is a mature interior lattice site. Its velocity is damped by `anchor_damping`
each tick, freezing it. This does NOT place atoms — they emerged from the
cascade. It only freezes what already self-assembled, giving the bridges
riding on those atoms stable place-identity.

## Hypothesis

With anchoring ON, mature atoms stop drifting, so stim-region bridges stay
in the stim region. Under the existing relative-to-mean bistable drive they
accumulate sustained above-mean flux and latch STRONG; control-region bridges
stay below-mean and remain WEAK. The selective latch BET-089 could not show
becomes demonstrable.

## Acceptance bars (locked pre-run)

| ID | Criterion | Bar |
|----|-----------|-----|
| T90a | Anchoring freezes structure | mean displacement of mature atoms over the last 2000s < 25% of their displacement over the equivalent pre-mature window (structure measurably stiffens) |
| T90b | Selective latch (the goal) | during STIM, stim-region bridge mean > `bistable_mid`; control-region bridge mean < `bistable_mid` |
| T90c | Selective memory persists | >= 2000s AFTER stimulus stops, stim-region mean still > `bistable_mid` AND control-region mean still < `bistable_mid` |
| T90d | Negative control FAILS | with anchoring OFF (`anchor_damping=0`), T90c does NOT hold (replicates BET-089's non-selective result) — required for the anchored result to be defensible |

PASS = T90a, T90b, T90c all hold AND T90d's negative control fails as required.
A clean NULL (anchoring freezes structure but selectivity still doesn't hold)
is a valid, informative verdict — it would say place-identity is necessary but
not sufficient, and the blocker lies elsewhere.

## Run design

- Same substrate as BET-089 (run_bistable.py params): 400 vibs, 30³ box,
  atom_valence=3, thermal 0.3, bistable_* as registered.
- Two arms, identical except `anchor_damping`: ON arm = 0.7, control arm = 0.0.
- Localized slow-vibration stimulus drives the left (stim) region during STIM;
  right (ctrl) region undriven. Measure region means at low cadence through
  STIM and a >= 2000s POST window.
- `rng_seed` fixed and identical across arms (only the anchoring knob differs).

## Time budget

Realistic: 10 min wall (two arms). Ceiling: 20 min. Overrun → FAILED
post-mortem in LOGBOOK.md, no quiet extension.

## Not claimed

- Not recall (no read-out decoder). The selective latched state is the memory.
- Content-addressability (distinct stimulus → distinct stable pattern) remains
  the follow-up once a single selective latch is shown.

## RESULT

_(to be filled after the run — PASS / FAIL / NULL with evidence)_

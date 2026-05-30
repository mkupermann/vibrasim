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

## RESULT (2026-05-30): NULL — velocity-anchoring works, but atoms don't persist

Verdict: **NULL**. Selective memory not achieved. The negative control failed
as required (T90d ✓), so the comparison is valid, but the anchored arm did not
clear T90a/b/c.

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T90a freeze | ✗ | ON-arm mature-atom drift 20.3→20.4 per 1000s window ≈ OFF control 18.2→13.9. No structural stiffening at the window scale. |
| T90b stim-selective | ✗ | `frac_strong=0.00` every checkpoint, both arms — no bridge ever crossed the barrier. |
| T90c memory-selective | ✗ | follows from T90b. |
| T90d control fails | ✓ | OFF arm equally non-selective (required for defensibility). |

### Why — diagnosed, not assumed

The velocity-freeze **mechanism is sound**. Instrumented run: atoms past the
maturity gate move at mean |vel| **0.0144** vs **0.0804** for the general
level-4 population in the same arm — a 5.6× slowdown. Anchoring fires and bites
(546–1027 distinct atoms entered maturity tracking; ~3 frozen at any instant).

The mechanism is nonetheless **irrelevant at this scale** because the lattice
sites do not persist:
- **Mean level-4 atom lifetime ≈ 13 sim-seconds** — *shorter than the 50 s
  maturity gate itself*. Most atoms die before they ever qualify to freeze.
- **1027 distinct level-4 atoms** churned through 4000 sim-s; only ~3 alive at
  the end. The structure is a standing wave of constant formation/death, not a
  fixed lattice.
- Freezing a site's velocity cannot preserve place-identity when the site
  evaporates in 13 s and is replaced by a new atom elsewhere.

T90a's window-scale drift metric also can't resolve freeze-vs-mobile: in a 30³
box, even thermal 0.3 random-walks to box-scale displacement within one 1000 s
window, so displacement saturates regardless. The velocity diagnostic above is
the metric that actually discriminates, and it shows the freeze working.

### Finding

Velocity-anchoring is **insufficient**. The binding constraint is atom
**persistence**, not mobility. Place-specific memory needs lattice sites that
live on the memory timescale (≫ 13 s); slowing them down does nothing if they
dissolve first. This sharpens the BET-087/088/089 substrate-scale limit: the
missing quantity is *lifetime of high-level structure*, not bridge count or
bridge mobility.

### Next direction (not done here — no tuning to a result)

Extend high-level node lifetime so level-4 atoms persist on the memory
timescale (e.g. lengthen `triad_decay_time`/atom decay for bonded interior
sites, or make bonds themselves protect their atoms from cascade decay). Only
once a level-4 lattice survives ≫ maturity-gate seconds can anchoring give it
stable place-identity and the three verified mechanisms compose. Lowering
`anchor_age` to 13 s would be tuning to this result and would NOT fix the
underlying non-persistence — explicitly rejected.

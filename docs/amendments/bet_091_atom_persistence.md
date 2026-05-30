# BET-091 — Atom Persistence via Valence Commitment

Pre-registered: 2026-05-30 (BEFORE any run under this design).
Direct follow-up to BET-090's diagnosed constraint: level-4 atoms live
~13 sim-s, far shorter than the memory timescale, so anchoring has nothing
durable to anchor.

## The diagnosed cause (from BET-090 instrumentation)

All 1024 level-4 atom deaths in the BET-090 substrate came from
`bind_nodes_upward`. The base upgrade table `_UPGRADE_TARGET` contains
`(4,4): 5` — two atoms within `r_2` of opposite polarity fuse into a level-5
molecule, **consuming both atoms**. This is NOT gated by `mol_fusion_enabled`
(that flag only gates molecule+molecule fusion). So every atom survives only
until it drifts within `r_2` of another atom, then is eaten. Mean lifetime
~13 s. No fixed lattice can form.

## Mechanism under test (within substrate primitives)

**Valence commitment.** An atom that has already formed bridges
(`k_bond_count >= fusion_bond_block`) is committed to its lattice — its
valence is spent on external bonds, leaving none for internal fusion. In
`bind_nodes_upward`, a level-4 atom meeting that bond threshold is skipped as
a fusion partner. This reuses two existing primitives only — the bridge
bond-count (`form_bridges`) and the valence concept (`atom_valence`) — and
adds no new dynamics. Bridges = external connections (preserved); fusion =
internal construction (blocked once bonded). Unbonded atoms fuse exactly as
before, so the cascade up to atom formation is untouched.

## Hypothesis

Blocking fusion for bonded atoms lets a bonded atom persist instead of being
consumed. Bonded-atom lifetime rises far above the 50 s anchoring maturity
gate, giving the lattice stable place-identity. With that persistence in
place, the BET-090 anchored selective-memory test can finally pass: stimulated
-region bridges latch STRONG and stay; control stays WEAK.

## Acceptance bars (locked pre-run)

| ID | Criterion | Bar |
|----|-----------|-----|
| T91a | Persistence | with valence-commitment ON, mean lifetime of atoms that reach `k_bond_count >= fusion_bond_block` exceeds 100 sim-s (>> the 50 s gate and >> the ~13 s baseline) |
| T91b | Control persistence FAILS | with it OFF, bonded-atom mean lifetime stays < 30 sim-s (replicates BET-090's ~13 s) — required to attribute the lifetime gain to the mechanism |
| T91c | Selective memory (the payoff) | with valence-commitment AND anchoring ON: during STIM stim-region bridge mean > `bistable_mid` and control < `bistable_mid`; AND >= 2000 s after stimulus stops, that selectivity still holds |
| T91d | Control memory FAILS | with valence-commitment OFF (anchoring still ON), T91c does NOT hold (replicates BET-090 NULL) |

PASS = T91a AND T91c hold, AND both controls (T91b, T91d) fail as required.
A clean NULL is valid: e.g. atoms persist (T91a) but selectivity still fails
(T91c) — that would say persistence is necessary but not sufficient and send
the next amendment elsewhere.

## Parameters (pre-committed, not to be tuned to a result)

- `fusion_bond_block = atom_valence (=3)` — only a fully valence-saturated atom
  (no dangling bond) is locked into its lattice and resists fusion. (Corrected
  pre-data from the original `=1`, which caused intractable runaway node growth;
  see docs/marker_protocol.md "Pre-data design correction (2026-05-30)".)
- Anchoring as BET-090: `anchor_damping=0.7, anchor_bond_min=2, anchor_age=50`.
- Substrate otherwise identical to BET-090/BET-089. Same `rng_seed` across
  arms; only the gated knob differs between an arm and its control.

## Time budget

Realistic: 12 min wall (persistence probe + two memory arms). Ceiling: 24 min.
Overrun → FAILED post-mortem in LOGBOOK.md, no quiet extension.

## Not claimed

- Not recall (no decoder). The selective latched state is the memory.
- Content-addressability remains the follow-up once one selective latch holds.

## RESULT (2026-05-30): NULL — persistence SOLVED, but not sufficient for the latch

Verdict: **NULL**. The persistence half is a decisive success; the memory half
still fails, for a new and more advanced reason.

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T91a persistence | ✓ **PASS** | ON bonded-atom mean lifetime **1513.6 s** (n=359, 68 still alive at cutoff) — ~30× the 50 s gate, ~115× the ~13 s baseline. |
| T91b control persistence fails | ✓ | OFF bonded-atom mean lifetime **4.3 s** — attributes the gain entirely to valence commitment. |
| T91c selective memory | ✗ **FAIL** | No bridge ever crossed the barrier (mid=3) in either phase; stim/ctrl region means stayed ~1.0–2.0 throughout. The latch never fired. |
| T91d control memory fails | ✓ | OFF arm equally non-selective (and has ~0 bonded atoms). |

### The win: persistence is solved

Valence commitment works exactly as designed and dramatically. Atoms went from
~13 s lifetimes to **~1500 s**, and the substrate now sustains a stable lattice
of **66–68 bonded atoms with ~50–64 bridges per region** (vs ~3 atoms / 1–7
bridges in BET-089/090). For the first time in the BET-087→091 chain the
substrate holds a persistent, populated structure. This is the prerequisite the
whole chain was missing — the base a memory (and learning) could sit on.

### Why the latch still failed (Pattern 01 triage)

The bistable mechanism *fired* (`bistable_rate=1.0`) and had a *partial* local
effect — bridge strengths drifted above the weak well (low=1, to ~1.5–2.0) —
but never crossed the barrier (mid=3). The binding constraint has **moved**:
it is no longer "no persistent structure" but "the latch drive does not scale to
a populated lattice." The bistable drive is **relative to mean flux**
(`flux_gain * (flux/mean_flux - 1)`), calibrated in BET-089 for ~1–7 bridges.
With ~100 bridges the stimulus flux is diluted across many bridges and the
control region carries comparable baseline flux, so the stim/mean ratio stays
near 1 and the drive is too weak to push any bridge over the barrier. The latch
parameters that worked on a tiny substrate are mis-scaled for a populated one.

### Finding

Atom persistence is **necessary but not sufficient** for selective memory. With
persistence achieved, the next limiter is latch *drive vs barrier* at high
bridge density — a calibration/regime problem, not a missing mechanism and not a
structural one. We have climbed from "cannot hold structure" to "holds structure
fine; the write mechanism does not engage at scale" — genuine upward progress.

### Next direction (a NEW pre-registered amendment, not a tune here)

BET-092: re-derive the bistable drive for the populated-lattice regime — e.g.
localized/absolute flux drive (BET-089 v1 latched cleanly under absolute drive),
or a barrier height that scales with bridge density, pre-registered with fresh
bars and matched controls. Changing `bistable_*` here, post-result, to force
T91c is explicitly refused (post-hoc tuning, forbidden by protocol). The
persistence mechanism (this amendment) is kept regardless — it is an independent,
verified win.

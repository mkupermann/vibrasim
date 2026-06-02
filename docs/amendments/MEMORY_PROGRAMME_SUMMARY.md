# Memory Programme Summary (BET-089 → 102)

Consolidated end-state of the autonomous run that attempted selective, persistent
memory in the spontaneous EQMOD substrate. Written 2026-05-31.

## Question

Can the substrate write a localized memory (stimulate one region), hold it after
the stimulus stops, and read it back selectively — using only substrate
primitives (no LLM)?

## What was SOLVED

1. **Persistent lattice (BET-091).** Valence commitment (a fully-bonded atom
   resists fusion) raised level-4 atom lifetime from ~13 s to ~1500 s; ~68 stable
   bonded atoms vs ~3. First persistent structure in the project.
2. **Selective WRITE (BET-096/097 flux; BET-099 correlation).** A localized
   stimulus drives the stimulated region's bridges over the bistable barrier
   while control stays weak — cleanly, with sharp spatial separation.
3. **Persistent RECALL, demonstrated transiently (BET-099).** Firing-coincidence
   (Hebbian) plasticity on the persistent lattice held a selective memory for
   ~3000 s after the stimulus was removed.

## What was NOT achieved, and WHY (the deadlock, characterized)

**Clean, robust, long-horizon selective RECALL.** It failed for a sequence of
reasons, each diagnosed and ruled out, converging on one root cause:

- per-bridge flux state erodes under **bridge turnover** (BET-098);
- tiny-population cores give **noisy readouts** (BET-099/100);
- emission both **writes and contaminates** — an over-loaded coupling (BET-100,
  Pattern 02);
- write/leak are **geometrically inseparable** when neighbour ≈ control distance
  with fast charge decay (BET-101);
- and finally, even with a bigger box + longer integration, the memory still
  spreads — because the substrate is a **connected lattice and activity
  PERCOLATES** atom-to-atom across any gap over time (BET-102).

**Root cause: connectivity, not scale.** A homogeneous, fully-connected substrate
cannot hold a spatially-local selective memory at any scale — percolation
homogenises it. This is a structural property of the medium, not a missing
learning rule (every write mechanism succeeded).

## Resolution — converges on the charter's architecture

Containment of a local memory requires **engineered modular compartments**
(weakly-coupled clusters that localise activity) — precisely CONCEPT §4.8's
engineered port topology, which the charter already designates as ENGINEERED
while internals emerge. The memory programme independently rediscovered the
project's founding design principle: **selective memory needs engineered
modularity; it will not emerge from a homogeneous substrate.**

## Mechanisms left in the codebase (all gated off by default)

- `fusion_bond_block` (valence commitment / persistence) — world/bridges.py
- `bistable_drive_mode='absolute'`, `bistable_drive_rectified` — bistable latch
- `apply_correlation_plasticity` (`corr_plasticity_rate`) — Hebbian co-firing
- plus the neuron_dynamics `n_alive` underflow fix.

## Reusable patterns surfaced

- Pattern 01 — three-way triage before believing a null (fired / ineffective /
  wrong-constraint).
- Pattern 02 — the same coupling both writes and corrupts; reshape locality, not
  gain.

## Honest answer to the strategic question

The recurring wall to learning/recall in this substrate is **structural
(connectivity/scale), not the learning rule.** Mechanisms work in isolation;
composing them into durable selective memory requires engineered modular
architecture. This is the deadlock, mapped — the charter's actual deliverable.

## Next direction (architectural, a strategic decision — not a regime knob)

BET-103+: introduce **engineered modular compartments** (e.g. weak inter-cluster
bridge coupling / port-bounded firing) so a localized memory cannot percolate
out, then re-test selective persistent recall and content-addressability. This is
the engineered-topology path the charter prescribes.

## Update (2026-06-02) — G33→G38: engineered wall built and tested; the gap moved, not closed

Implemented the prescribed engineered compartment as `apply_engineered_compartment`
(CONCEPT §4.8 port wall, config-gated, no-op by default) and ran the (wall × readout) grid
on the BET-099/100 recall protocol:

- **Firing containment: now SOLVED and robust.** A specular mirror wall
  (`compartment_mode='mirror'`, r → 2R−r) contains firing to the stim region 300–330×
  across seeds {42,7,99} (G37/G38). The clamp wall pins vibrations to a degenerate shell
  and suppresses the write (G36); the soft wall leaks (G35); the mirror wall both writes
  and contains. The percolation/propagation route the original programme blamed CAN be cut.
- **Readout: the region-mean statistic was an ARTIFACT.** Strong bridges, once latched,
  persist with retention 1.0 over 14 000 s (G34) — there is no turnover of the engram. The
  earlier 0↔6 "turnover noise" was weak-bridge churn + region-membership drift. A set-based
  readout (bridges keyed by atom slot + k_birth) reads the engram correctly.
- **Selective persistent recall: still NOT robust.** With containment solved and the right
  readout, selectivity replication still FAILED (G38): on n≈3 strong-bridge cores, *which*
  bridges latch is stochastic (no engram on seed 99; control non-selective on seed 7; the
  single-seed G37 PASS was within the noise). The matched no-wall control was itself
  inconsistent (|C|=0 on 2/3 seeds), so even the "contamination" was not robust.

**Refined root cause.** The deadlock is no longer propagation (cuttable by the wall) nor
turnover (engram is permanent) nor readout (set-based works). It is **stochastic latching on
a tiny core**: too few elements per region for *which* bridges potentiate to be controlled
by the stimulus rather than noise. This is the SCALE limit, isolated. **Indicated next
lever:** write the engram on a LARGE persistent core (the G28/G30 ~110-atom lattice now
available) so latching noise averages out, then re-test selectivity across seeds. New
reusable mechanism: the engineered specular port wall (robust firing containment).

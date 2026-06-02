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
by the stimulus rather than noise. This is the SCALE limit, isolated. New reusable mechanism:
the engineered specular port wall (robust firing containment) — docs/patterns/engineered_port_wall.md.

## CLOSE (2026-06-02) — G39 refutes the scale lever; recall thread closed as a robust negative

G39 tested the scale lever (enlarge the core by 3× injection, seeds {42,7,99}): it FAILED.
The engram will NOT grow on demand (|E| stayed 1–6 regardless of input — the strong-bridge
count is capped by the co-firing/bistable dynamics, not the drive), and persistence is itself
seed-dependent at this scale (seed 99's engram dissolved to 0). Only containment stayed robust.

**Verdict on selective persistent CONTENT recall: robust NEGATIVE.** Across BET-089→102 and
G33→G39 (~25 experiments, two sessions), every selective-recall result was NULL or a
single-seed fluke. The substrate's plasticity produces only a tiny (1–6), stochastic engram
that cannot be grown, reliably persisted, or made stimulus-selective — at any core size
reachable by these means, even with the propagation route cleanly cut. This is a complete,
honest characterization, not a missing knob.

**What the programme DID deliver (robust positives):**
1. Persistent lattice / structure (BET-091; G30 ~110-atom closed membrane; G32 sealed it).
2. Robust ACTIVITY containment via the engineered specular port wall (G37–G39, 175–330× every seed).
3. The set-based engram readout (correct instrument; region-mean was an artifact).
4. A mapped deadlock: selective local memory does not emerge from this homogeneous substrate's
   plasticity even with engineered firing containment — the charter's actual deliverable
   (developing/mapping the deadlock-breaking process), now precisely bounded.

**PIVOT (decided 2026-06-02, autonomous).** Stop iterating the recall mechanism (diminishing
returns). Build on the robust positive: use the engineered port wall as a CONCEPT §4.8
modular building block. Next thread (G40+): demonstrate MODULAR INDEPENDENCE — two engineered
port compartments in one substrate, each firing on its own stimulus with NO cross-talk — a
positive the substrate can actually produce, advancing the engineered-modular-architecture
path instead of forcing selective memory the plasticity layer cannot support.

## DEFINITIVE CLOSE (2026-06-02) — the deadlock is mapped across ALL coupling channels

The modular-port thread (G40–G42) also hit the wall, and tying it to the earlier
architectural attempts (BET-103/104/105) completes the map:

- **G40–G42 (modular ports):** the one-way containment wall TRAPS foreign emissions (G40);
  the two-way seal helps at long range but is redundant there (distance already isolates,
  G41); at CLOSE range the seal makes NO difference (G42) because cross-talk there is carried
  by the neuron CHARGE-integration field (r_integrate) and BRIDGE graph, not free vibrations.
- **BET-103/104 (charge-channel gate):** gating the broadcast/charge field contains the leak
  but STARVES the write (write = broadcast = leak; same field).
- **BET-105/106 (bridge-graph write):** the non-broadcast write self-ignites whole compartments.

**Every coupling channel has now been gated or rerouted, and every attempt fails the same
way:** the signal that WRITES a memory is the signal that LEAKS it, on whichever channel you
choose (vibration broadcast, charge field, or bridge graph). Selective persistent CONTENT
memory does not emerge in this substrate — a robust, exhaustively-characterized NEGATIVE
across ~30 experiments and two sessions. This IS the charter's deliverable: the deadlock,
mapped and bounded, not papered over.

**New robust POSITIVES surfaced this session** (kept and reusable):
1. Engineered specular port wall → robust single-region firing containment (175–330×),
   docs/patterns/engineered_port_wall.md (mode='mirror'; one-way valve caveat documented).
2. Set-based engram readout → proved the strong-bridge engram is PERMANENT (retention 1.0);
   the old "turnover" narrative was a region-mean artifact. (Corrects the earlier summary.)
3. Channel decomposition (G42): close-range coupling is charge/bridges, not vibration.

**PIVOT (decided 2026-06-02, autonomous) — to the STRUCTURAL frontier.** The cognition/memory
side is a comprehensively-mapped negative; the substrate's robust POSITIVES are structural
(G27 rich chemistry, G30 large closed membrane, G32 selective permeability). Next work moves
there: build toward a proto-cell — a membrane (G30) enclosing a DISTINCT interior chemistry
maintained by selective permeability (G32) — a bottom-up structural milestone the substrate
has shown it can actually reach. The memory programme is closed.

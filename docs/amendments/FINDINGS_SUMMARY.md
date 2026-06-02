# EQMOD Findings Summary — what the substrate CAN and CANNOT do

Top-level synthesis of the substrate exploration (BET-086→G51), written 2026-06-02. Ties the two
major threads — cognition/memory and proto-cell structure — into the project's overall result.
The charter's goal is "developing a deadlock-breaking process, not necessarily succeeding"; this
document is that deliverable: the substrate's capabilities and ceilings, mapped and bounded.

## The bottom-up chain that WORKS (robust positives)

vibrations → electrons → atoms → molecules → bridges → **a persistent, self-regulating membrane
(a proto-cell)**. Every step is emergent from substrate primitives; the only engineered piece is
the §4.8 channel/port boundary (charter-sanctioned). No LLM, no transformer.

| Result | What | Status |
|--------|------|--------|
| G27 | Widening the frequency rule → rich chemistry (200 atoms, 600+ molecules) | PASS |
| G28 | Element-count ceiling lifted (100–313-atom bridged structures) | finding |
| G30 | Large closed membrane composes (~110 atoms, shell-like, persists) | PASS |
| G32 | Selective permeability in the engine (atom-proximity reflector, clean seal) | PASS |
| G43 | Proto-cell homeostasis (maintained interior–exterior gradient) | PASS |
| G44 | Active regulation to set-point after perturbation | PASS |
| G51 | Membrane formation is scale-invariant (372 atoms at 3.4× box, same σ/R) | partial+ |

**The substrate builds a proto-cell with FUNCTION**: forms → seals selectively → maintains an
interior environment → regulates back to set-point after a disturbance. A genuine bottom-up
cell precursor.

## The ceilings (robust, exhaustively-mapped NEGATIVES)

### 1. No selective persistent memory — the deadlock, mapped across ALL channels
Across ~30 experiments (BET-089→102, G33→G39): selective persistent CONTENT memory does not
emerge. The signal that WRITES a memory is the signal that LEAKS it, on EVERY coupling channel —
vibration broadcast (BET-099–102, G33–G39), neuron charge field (BET-103–104), and bridge graph
(BET-105–106). Containment strong enough to stop the leak also starves the write (monotonic
trade-off, no win cell). Set-based readout proved the engram is PERMANENT (so it is not a
persistence/turnover problem) — it is a write=leak connectivity problem. See
MEMORY_PROGRAMME_SUMMARY.

### 2. No metabolism, no self-repair, no population — the proto-cell's structural ceiling
Across G45→G51 (seven experiments): the membrane is persistent, self-regulating, but STATIC.
- No channel-coupled synthesis / metabolism (G45, G49, G50): interior assembly (~16 atoms) is
  fixed by local geometry, independent of the channel or active uptake.
- No self-repair (G46–G48): a wounded shell does not heal; cause is positional rigidity + no
  wound-targeting (NOT valence commitment — G48 falsified that hypothesis).
- No population (G51): the substrate coalesces to ONE scale-invariant membrane, not several.
See PROTOCELL_SUMMARY.

## The unifying principle
Both ceilings are the same structural fact seen twice: **the substrate is a strongly-coupled,
positionally-rigid connected medium.** That connectivity is why memory leaks (write=broadcast=leak
across channels) AND why the membrane is one rigid coalesced surface that regulates but does not
metabolize, heal, or divide. The substrate excels at CONTAINMENT and REGULATION (its connectivity
working FOR you) and fails at SELECTIVE LOCALIZATION and FLUID REORGANIZATION (its connectivity
and rigidity working against you). Build functions on the former; the latter need a different
medium or new primitives.

## Reusable mechanisms surfaced (docs/patterns/)
- atom_proximity_reflector — gate off the real structure, not a fitted proxy.
- engineered_port_wall — specular reflection for robust activity containment (mode matters).
- protocell_homeostasis — emergent membrane + selective channel = regulated interior.
- (plus the earlier 01-which-constraint-binds, 02-write-contaminate-tension.)

## Honest process notes
Pre-registration held throughout (bars locked before every run; NULL a valid verdict; no post-hoc
tuning). Two of my own mechanistic hypotheses were FALSIFIED by confirmatory tests and corrected
in writing (G33 "turnover" → readout artifact; G47 "persistence⊥repair" → rigidity, via G48). A
single-seed apparent success (G37) was caught by a pre-registered multi-seed replication (G38) and
retracted. Honesty over consistency, throughout.

## What would move the needle next (requires new primitives / a decision, not a regime knob)
- Selective memory: a write channel DECOUPLED from broadcast (directional, non-leaking) — not
  achievable with current primitives (BET-105 tried bridge-graph write; it self-ignites).
- Metabolism/repair/division: a FLUID membrane (atoms that can migrate and re-bond). G52 pinned
  the rigidity precisely to PERMANENT BONDS (not stationarity — atom mobility alone heals nothing,
  the atoms are tethered). The specific needle-mover is BOND TURNOVER: a mechanism for bonds to
  spontaneously break and reform so the network remodels and atoms flow into a wound. This is a
  new substrate primitive (decay_bridges currently breaks bonds only on atom death), the defined
  strategic next step (G53). Risk: the fluidity/stability trade-off — too much turnover dissolves
  the membrane.

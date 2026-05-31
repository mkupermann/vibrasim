# BET-103 — Engineered Modular Compartment: Contain Percolation

Pre-registered: 2026-05-31 (BEFORE any run). The architectural pivot prescribed
by the memory-programme finding (BET-102): clean selective recall fails because a
homogeneous connected substrate lets activity PERCOLATE; containment needs
engineered modularity (CONCEPT §4.8 ports — engineered, internals emergent).

## Mechanism (engineered modularity, within primitives)

A single engineered x-plane wall at the box midline (`compartment_boundary`):
- **neuron_dynamics**: an atom integrates charge only from vibrations on its own
  side of the wall — firing cannot be driven across.
- **apply_correlation_plasticity**: a co-firing pair straddling the wall does not
  potentiate its bridge — the memory write cannot cross.

This is the minimal engineered compartment: it does not place or train anything;
it only blocks cross-compartment activity, so a memory written in one compartment
cannot percolate into the other. The lattice and memory inside each compartment
still emerge.

## Hypothesis

With the wall between the stim region (compartment A) and control region
(compartment B), the selective memory that BET-099 wrote but let percolate now
STAYS contained: stim bridges latch and persist, control stays weak — robustly,
for the full POST window. Same substrate as BET-099 (box 30) otherwise.

## Acceptance bars (locked pre-run — BET-100/101 metric verbatim)

| ID | Criterion | Bar |
|----|-----------|-----|
| T103a | Selective firing (gate) | stim firings >= 3× control during STIM |
| T103b | Selective potentiation | fraction of STIM checkpoints selective >= 0.5 |
| T103c | Persistent recall | fraction of POST checkpoints (>= stim_end+2000 s) selective >= 0.5 |
| T103d | Negative control FAILS | uniform arm: fraction of those POST checkpoints selective < 0.25 |

PASS = T103a–c hold AND T103d. PASS = the first clean, persistent, selective
memory — and confirmation that engineered modularity is the resolution the whole
programme pointed to. NULL with the wall in place would mean even hard
compartmentalization doesn't contain it → the limit is deeper still.

## Run design

BET-099 setup (box 30, neuron_dynamics, correlation plasticity, persistence,
n_emit=8) PLUS `compartment_boundary = 15.0` (midline; stim at x=7.5 in
compartment A, control at x=22.5 in compartment B). Localized vs uniform arms,
fraction-selective metric, same rng_seed.

## RESULT (2026-05-31): NULL — the wall contains percolation but STARVES the write (Pattern 02, fundamental)

Verdict: **NULL**. The compartment wall contained activity (control stayed at
1.00 cleanly) but nothing latched ANYWHERE — stim included (stim 1.00 through
STIM and POST), despite stim atoms firing heavily (ratio 125).

| Bar | Outcome | Evidence |
|-----|---------|----------|
| T103a selective firing | ✓ | ratio 125 — firing confined to stim. |
| T103b selective potentiation | ✗ | 0.00 — no bridge latched, even in the stim compartment. |
| T103c persistent recall | ✗ | 0.00. |
| T103d control fails | ✓ (trivially) | nothing latched. |

### Why — the write field IS the leak field

BET-099 (same box 30, n_emit=8, emit_speed=30, no wall) DID write. The only
change here is the wall. Yet the write died everywhere. The wall confines an
atom's charge integration to same-side vibrations — which, for a stim atom at
x≈7.5 with r_integrate=5, should not even remove any vibrations (its zone is
wholly on the stim side). So the write did not die from local starvation; it died
because the co-firing that wrote BET-099's memory was sustained by the GLOBAL
broadcast field — emitted vibrations (emit_speed 30) flooding the whole box and
co-activating bridged neighbours everywhere. Halving that field (same-side only)
dropped co-firing below the write threshold.

**This is Pattern 02 at the architectural level, and it is fundamental here: the
broadcast activity field that WRITES the memory is the same field that PERCOLATES
(leaks). Containing the leak (the wall) necessarily starves the write.** You
cannot separate them while the write signal IS the broadcast field.

### Deepened consolidated finding

Clean selective persistent memory in this substrate is blocked by a structural
identity: write = broadcast = leak. Engineered modularity that blocks the
broadcast also blocks the write. The resolution must **decouple the write signal
from the broadcast field** — e.g. a write that travels along the BRIDGE GRAPH
(direct atom→atom propagation through strong bridges, G6
`apply_bridge_atom_propagation`), which respects connectivity and can be made
modular by cutting cross-compartment bridges, rather than via omnidirectional
vibration broadcast. That is a different mechanism, not a regime knob.

### Next direction (BET-104, architectural)

Decouple write from broadcast: drive co-activation through the bridge graph (G6)
instead of emitted-vibration broadcast, with cross-compartment bridges weak/cut.
Then the write travels only along connectivity and modularity contains it without
starving it. Surfaced to Michael as a strategic decision.

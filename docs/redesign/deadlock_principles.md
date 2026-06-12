# Deadlock principles — the proven structural constraints of the legacy substrate

**Authored:** 2026-06-12 · **Status:** grounded inventory (cites only proven results) · **Purpose:** state every
mapped deadlock as a precise mechanical constraint, so a redesign knows exactly what it must break — and so no
later session forgets what was actually proven vs. assumed.

Each entry: **Observation** (strongest numeric evidence + the experiment that proved it) → **Binding constraint**
(the mechanical root cause) → **Required break** (the property a new substrate must have to escape it, stated as
an OPEN requirement — NOT a pre-committed mechanism). "Required break" is what `design_requirements.md` derives
from; it is deliberately not a solution.

Authoritative detail: `LOGBOOK.md`, `docs/MEMORY_PROGRAMME_SUMMARY.md`, `docs/amendments/G15*.md`,
`docs/patterns/01-03`. If this disagrees with those, they win.

---

## The activity-memory deadlock is THREE channels, not one

The central finding (the structural reason ~70 experiments — G33–G96, BET-089–106 — all NULL'd): selective
persistent *activity* memory fails because activity can spread A→B through **three independent channels**, and
no single fix closes all three. Containing one leaves the others leaking; containing the field starves the
structure. The channels:

### D1 — Bond-mediated percolation  *(SOLVED on this channel — G159)*
- **Observation:** in a connected bond graph, charge propagates atom-to-atom along bonds: G159 control (M=1, one
  component) → B_fire = 54 across the gap. A homogeneous, fully-connected substrate has no bottleneck.
- **Binding constraint:** connectivity is unbounded; any bond path carries activity, so a localized write spreads.
- **Required break:** connectivity must be partitioned so bond-mediated spread is bounded *by construction*.
- **Status:** an H₀ (connected-component) bond-formation rule self-organises a stable modular partition (G158)
  that COMPLETELY gates this channel (G159, M=2 → B_fire = 0; emergent, not a hand-placed wall like G86). This is
  the one channel with a working, emergence-preserving solution. A redesign should KEEP this mechanism.

### D2 — Field-mediated percolation  *(OPEN — topology cannot touch it)*
- **Observation:** G160 — with the charge-integration field on (firing emits vibrations; atoms integrate charge
  from vibrations within `r_integrate`), charge floods across the topological cut: M=2 → B_fire = 117. ARM C
  proves it is topology-independent: bonds-off M=2 and M=1 give B_fire = 124.7 == 124.7 *exactly*. Free vibrations
  saturate the box (no decay) → the leak is **global flooding, not slow diffusion**; distance barely matters
  (gap 12 → 117, gap 4 → 87). G86's hand wall contained it only by *also* cutting the write.
- **Binding constraint:** the field is spatial and global; it does not read the bond graph, so no connectivity
  rule gates it. And it is the SAME field that performs the write (see D4).
- **Required break:** an **active flux sink** (vibration decay / absorption / culling — the quiet-substrate the
  memory programme already needed) AND/OR a write channel physically distinct from the propagation field.

### D3 — Atom erosion in the quiet substrate  *(OPEN)*
- **Observation:** G93 — in the only regime where the field does not flood (quiet substrate, λ_gen = 0), the
  engram's level-≥4 atoms erode/dissolve (persist ≈ 0.26); consolidation can strengthen a bridge every tick but
  cannot keep it alive once its constituent atoms erode (G94/G95 NULL).
- **Binding constraint:** structural elements require continuous flux to persist — but that flux is the very leak
  field of D2. So containing the leak starves the structure: *active → contaminated, quiet → eroded.*
- **Required break:** element persistence must NOT depend on the same flux that leaks — a self-sustaining or
  non-energetic stability mechanism (an energy barrier far above the substrate's effective kT, or topological/
  discrete persistence).

### D4 — Write = Leak duality  *(OPEN — the meta-constraint behind D2/D3)*
- **Observation:** "the field that writes a memory IS the field that leaks it." G86: the compartment wall
  contained percolation but starved the write. BET-103/104: gating the charge field contains the leak but
  prevents the write. Every channel tested (vibration broadcast, charge field, bridge graph) carried write and
  leak on the same variable.
- **Binding constraint:** write, propagation, and leak are one physical quantity (the charge/vibration field).
- **Required break:** physically distinct write and read/propagation channels, so depositing a memory does not
  automatically become propagating leakage.

---

## Representational / architectural constraints (beyond the three channels)

### D5 — Categorical binding ≠ programmable storage  *(OPEN; the charter knife-edge)*
- **Observation:** G135 NULL (substrate can't relax to a useful layout); G145–G149 (oscillator-Ising only ties
  greedy, loses to SA at matched budget, G153); G154 (matter-register content-recall = 0.014/bit vs Hopfield
  1.000 at ~1/546th the compute). Mechanism: `apply_bridge_tension` uses a SINGLE global equilibrium
  `r_eq = r_2·0.5` with **no per-bond rest length**, so a stored multi-cell pattern is not a retrievable attractor.
- **Binding constraint:** binding rules are categorical-label matches (frequency/polarity), local, pairwise, with
  one global equilibrium. They cannot encode arbitrary per-association content, nor distinct "store X" vs
  "recall X" operations.
- **Required break:** bindings must carry **per-association state** (a settable rest length / weight / token) so a
  specific pattern is a retrievable attractor — *without* hand-building a RAM. The state must EMERGE from local
  rules (see `docs/patterns/03`; this is the line between an emergent substrate and an engineered data structure).

### D6 — Turnover dilutes the readout  *(OPEN)*
- **Observation:** BET-098 (per-bridge flux state erodes under bridge turnover); G94/G95 (a consolidated bridge
  persists, but only non-selectively — by count/topology, not by identity).
- **Binding constraint:** processing elements churn; any distributed or rate-coded readout is averaged away as
  elements turn over.
- **Required break:** a readout that survives element turnover — stable memory loci distinct from the processing
  elements, or a high-redundancy distributed code.

### D7 — The self-model is allopoietic (a passenger)  *(OPEN; peripheral to memory)*
- **Observation:** `docs/marker_protocol.md` — G17 was renamed from "autopoiesis" to **homeostatic parameter
  feedback**: the driver tunes parameters from OUTSIDE the substrate's own production network. G16's self-model
  tracks per-pattern firing but cannot intervene on the structural dynamics.
- **Binding constraint:** the self-model channel is orthogonal to the production rules it would need to change.
- **Required break:** for self-modification to matter, the self-model must causally act on the substrate's own
  binding/production rules (genuine autopoiesis), not tune external knobs.

---

## Summary — the design spec seed

A substrate that holds a **selective, persistent, emergent** memory must, at minimum, simultaneously satisfy:

| # | Channel / constraint | Required break (open) | Proven by |
|---|----------------------|-----------------------|-----------|
| D1 | bond-mediated spread | bounded connectivity (partition) | G158/G159 — **solved, emergent** |
| D2 | field-mediated spread | active flux sink and/or write≠propagate channel | G160 (+ G86) |
| D3 | element erosion | flux-independent persistence | G93/G94/G95 |
| D4 | write=leak coupling | physically separate write & read channels | G86, BET-103/104 |
| D5 | categorical binding | emergent per-association state (not a hand-built RAM) | G135/G145–149/G154 |
| D6 | turnover dilution | turnover-robust readout | BET-098, G94/G95 |
| D7 | passenger self-model | self-model acts on production rules | marker_protocol.md (G17) |

The honest hypothesis a redesign tests: **are these breaks jointly achievable by an emergent, locally-ruled
substrate, or only by an engineered data structure?** D1 is already achievable emergently (G159). If D2–D6 can
each be met by a *local rule* (not by hand-building memory), the deadlock was design-dependent. If any of them
provably cannot be met without engineering the memory mechanism itself, the deadlock is inherent to the substrate
class — itself a publishable negative result.

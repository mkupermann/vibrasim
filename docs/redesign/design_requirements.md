# Design requirements — what an emergence-preserving substrate must satisfy

**Authored:** 2026-06-12 · **Status:** derived from `deadlock_principles.md` (every requirement traces to a
proven deadlock) · **Purpose:** the acceptance criteria for any candidate redesign. A candidate that cannot meet
these does not escape the mapped deadlocks.

**The hard meta-constraint (the project's premise — non-negotiable):** the memory mechanism must **EMERGE from
local binding rules**. We may engineer the *topology / boundary conditions* (ports and scaffold are sanctioned —
README NEW_DIRECTION: "engineered topology, emergent dynamics"), but we may NOT hand-build the memory itself.
A fixed-node + permanent-link + token store is a RAM; it would pass any memory test by construction and answer
the wrong question (`docs/patterns/03`). Each requirement below must be met by a *rule*, not by a hand-placed
structure.

---

| # | Requirement | Traces to | What "met emergently" means |
|---|-------------|-----------|------------------------------|
| R1 | **Bounded connectivity.** Bond-mediated spread is bounded by construction — the connection graph self-partitions into modules. | D1 | KEEP the H₀ rule (G158/G159). It is already emergent and proven. Reuse, don't reinvent. |
| R2 | **Field containment without starving the write.** Activity in the propagation field must not flood the whole substrate, AND containing it must not prevent writing. | D2, D4 | An *active* flux sink that emerges from local rules (local decay/absorption), OR a write operation that does not inject into the propagation field at all. |
| R3 | **Separate write and propagation channels.** The variable that stores a memory is physically distinct from the variable that propagates information between elements. | D4 | Two distinct local state variables per element (e.g. a slow "stored" variable + a fast "signalling" variable), coupled by a local rule — not one shared field. |
| R4 | **Flux-independent persistence.** A stored element survives without continuous drive from the leak field; it does not erode on the recall timescale. | D3 | Persistence from a local energy barrier far above effective kT, or discrete/topological state — an emergent property of the binding rule, not externally refreshed. |
| R5 | **Per-association state (retrievable attractor).** Bindings carry settable per-link state so a specific stored pattern is a content-addressable attractor, with distinct store vs recall operations. | D5 | A per-bond variable (rest length / weight) updated by a LOCAL learning rule (STDP/BTSP-style). The knife-edge: it must be set by emergent dynamics, never hand-written. |
| R6 | **Turnover-robust readout.** The memory readout survives churn of individual processing elements. | D6 | Either stable memory loci distinct from processing elements, or a redundant distributed code whose readout averages correctly under turnover. |
| R7 | **(Stretch) Causal self-model.** If self-modification is in scope, the self-model acts on the substrate's own production rules, not on external knobs. | D7 | Deferred — peripheral to memory; only if R1–R6 succeed. |

---

## Acceptance logic for a candidate redesign

- **A candidate must address R1–R5 to be worth building** (R6 is testable once a memory exists; R7 is stretch).
- **Each requirement is met by ONE local rule change at a time**, pre-registered as a phase with a frozen bar and
  a negative control (rule off). This isolates which break each rule actually achieves and prevents layering bugs.
- **The controlled experiment:** start from the legacy substrate (which already meets R1 via G159) and change the
  *minimal* set of local primitives needed for R2–R5. If a single principled primitive change meets a
  requirement emergently, log it. If a requirement provably cannot be met without hand-building memory, that is
  the boundary of the substrate class — a publishable negative result, recorded, not engineered around.

## The decision this teed up (for the human)

R3/R5 are where the real design choice lives, and it is genuinely the project owner's call: which **single
binding-primitive change** to attempt first. Candidates, each derived from a required break:

- **(a) Two-variable elements (R3/R4):** give each atom a slow "stored" scalar decoupled from its fast charge, with
  a local rule that writes to the slow variable on coincidence and reads from it without injecting into the field.
  Directly attacks write=leak (D4) and erosion (D3).
- **(b) Per-bond rest length (R5):** let each bond's `r_eq` be set by a local learning rule (the direct G154
  follow-on), making a stored configuration a true attractor. Attacks D5; knife-edge on emergence.
- **(c) Directed/irreversible binding (R4/R5):** replace the symmetric attractive bond with a directed, latching
  bond that does not spontaneously decay, so structure persists without flux.

Each is a single local-rule change, emergence-preserving, and pre-registerable as a phase-1 experiment. Pick one;
the next document is its frozen pre-registration.

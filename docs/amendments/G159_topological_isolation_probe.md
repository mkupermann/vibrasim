# G159 — Does the topological (H₀) partition functionally gate activity? (charge-isolation probe)

**Authored / FROZEN:** 2026-06-12 · **Status:** pre-registered, no run yet · **Thread:** substrate physics (`gNNN`)
**Follows:** G158 (the H₀ bond rule self-organises a stable modular partition — STRUCTURAL claim confirmed; the
mechanical functional marker was under-sensitive). **Grounding:** `world/bridges.py::apply_bridge_charge_propagation`
(BET-105), `world/physics.py::neuron_dynamics`, G86 (`compartment_boundary`). Engine `world/` @ main.

## Why this experiment

G158 left one thing unproven: the topological rule *builds* a modular partition of the bond graph, but G158's
readout (mechanical tension through one bottleneck bond) was too weak to show whether the partition *functionally*
blocks anything. The honest fix is a readout on a channel that the partition actually gates. `apply_bridge_charge_propagation`
(BET-105) is that channel: a **firing** atom deposits charge **directly into its bonded neighbours**
(`k_charge[j] += rate·strength`), so activity travels **only along the b_alive bond graph** — exactly the graph
the H₀ rule partitions. With no free vibrations (`n_initial_vibrations=0`) and no emission (`n_emit=0`), the bond
graph is the **only** route from one cluster to another. The field channel (`r_integrate`/emitted vibrations) is
switched off by construction, so this isolates the one sub-channel the rule can control.

## Probe method (exact)

- Two atom clusters, A = {x=10,16,22} and B = {x=34,40,46} at y=z=30; bottleneck candidate = the 22↔34 pair
  (distance 12 < `r_2`=14). All atoms injected via `allocate_node`, **pinned** at fixed positions every tick
  (pure charge-flow test — no tension motion confound).
- Constrained bond formation via the G158 union-find patch of `world.bridges.form_bridges`.
  **Treatment M=2** (keep A, B as two components → bottleneck rejected). **Negative control M=1** (one component
  → bottleneck bond present). Only the M parameter differs. `compartment_boundary=0` (the partition is the
  topological rule, NOT a hand-placed plane — that is the whole point vs G86).
- Charge config: `neuron_dynamics_enabled=True`, `theta_fire=4.0`, `n_emit=0` (firing propagates charge along
  bonds but emits NO vibrations → no field channel), `bridge_charge_prop_rate=2.0`, `bridge_prop_min_strength=0`,
  `lambda_gen=lambda_dec=0`.
- **Drive:** each tick, set `k_charge` of the A atoms to 10 (> `theta_fire`), pin all atoms, `tick`. A fires
  repeatedly; charge propagates along bonds. Run `T_DRIVE = 300` ticks after `T_CONSOL = 10`.
- **Activity readout:** count firing events of B-cluster atoms over `T_DRIVE` (primary), plus peak B charge.

## Pre-registration (FROZEN 2026-06-12 — no post-hoc tuning, NULL stands)

- **Seeds:** {42, 7, 13}; report mean ± SD.
- **Mechanism-fired check (pattern 01), before any verdict:** confirm (a) A atoms actually fire in both arms,
  (b) components held (M=2 → 2, M=1 → 1), (c) in M=1 the bottleneck bond exists with strength ≥ `prop_min`.
- **Primary marker — isolation ratio** `I = B_activity(M=2) / B_activity(M=1)`, where `B_activity` = total B
  firing events. "Injected charge in A produces < X% of the B-activity it would produce without the rule."
  **X = 10%.**
- **Negative-control sanity (MUST hold):** `B_activity(M=1) ≥ 5` firings — the channel genuinely percolates A→B
  without the rule. If it does not, the test is insensitive and the result is FAIL (not informative), not a PASS.
- **Bars:**
  - **PASS** — `I ≤ 0.10` AND `B_activity(M=1) ≥ 5` AND mechanism-fired. The emergent topological partition
    functionally gates bond-mediated activity percolation.
  - **PARTIAL** — `0.10 < I ≤ 0.30` with control percolating: the partition attenuates but does not fully block.
  - **NULL** — `I > 0.30`: charge crosses despite the partition. **Pre-registered conclusion if NULL:**
    topological compartmentalisation of the structural bond graph is **not sufficient** to block percolation —
    an **active gating mechanism** (not just a structural bottleneck) is required; the next amendment engineers
    that gate.
  - **FAIL** — `B_activity(M=1) < 5`: channel did not percolate even without the rule; test insensitive, redesign
    needed (do NOT read a PASS from it).

## Honest scope (no overclaim)

A PASS shows the partition gates the **bond-mediated** activity channel (BET-105) **only**, under idealized
conditions (emission off, no field channel). It does **not** address (a) the field channel (`r_integrate` /
emitted vibrations), which in a full substrate G86 had to contain by spatial separation, nor (b) the memory
starve/erode dilemma (G93). So a PASS = "structural topological partition is a *necessary, working component* for
modular activity isolation on its channel," not a memory-deadlock break. The memory deadlock remains closed.

## Engine / tooling

`tools/g159_topological_isolation.py`: reuses the G158 `form_bridges` union-find patch; pins atoms; drives A;
counts B firings; runs M=2 and M=1 over seeds {42,7,13}. Logs to `LOGBOOK.md`.

## Reproducibility

Engine `world/` @ branch `g159-topological-isolation`; macOS-arm64, Python 3.13 (`uv run`); seeds {42,7,13};
pinned atoms, emission off, bond-charge channel on. Bars frozen pre-run; mechanism-fired check mandatory; control
must percolate (`B_activity(M=1) ≥ 5`) for a PASS to count; NULL stands and triggers the active-gating conclusion.

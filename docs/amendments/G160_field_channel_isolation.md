# G160 — Does the topological (H₀) partition contain the FIELD channel too?

**Authored / FROZEN:** 2026-06-12 · **Status:** pre-registered, no run yet · **Thread:** substrate physics (`gNNN`)
**Follows:** G159 (the H₀ partition completely gates the *bond-mediated* charge channel). **Grounding:**
`world/physics.py::neuron_dynamics` (field channel: charge integrated from vibrations within `r_integrate`),
`world/bridges.py::apply_bridge_charge_propagation` (bond channel), G86 (spatial containment). Engine `world/` @ main.

## Design note — why NOT the "bonds-off, compare M=2 vs M=1" design

That design is **degenerate**: with `bridge_charge_prop_rate=0` and atoms pinned, the b_alive bonds carry no
charge and exert no motion, so the single extra bottleneck bond in M=1 has zero dynamical effect → B_fire(M=2) ≡
B_fire(M=1) by construction, and the marker "M=2 ≤1 AND M=1 ≥5" cannot be satisfied. More fundamentally, the field
channel never reads the bond graph, so topology *cannot* gate it (pattern-03). The clean test keeps **bonds ON**:
G159 proved that in M=2 the bond channel carries **zero** charge across the cut, so any B firing with the field on
is unambiguously **field** leakage — attribution is clean without turning bonds off.

## Probe (exact)

Same pinned A/B geometry and A-drive as G159. **M=2** throughout (bottleneck bond cut by the H₀ rule). Bonds ON
(`bridge_charge_prop_rate=2.0`) — realistic, and inert across the cut by G159. **Field ON:**
`n_emit=8` (firing emits vibrations), `r_integrate=5.0` (default), `n_vibrations_max>0` (free vibrations exist).
Drive A above `theta_fire` each tick; measure B firings.

Three arms:
- **A — leak test (primary):** M=2, field ON, gap = 12 (A max x=22, B min x=34). `B_fire(A)` = field leakage
  across the topological cut.
- **B — field-reachability sanity (MUST hold):** M=2, field ON, gap = 4 (B at x=26,32,38). The field demonstrably
  crosses a small gap → `B_fire(B) ≥ 5`. Guards against an insensitive "field never reached" null.
- **C — topology-independence confirmation:** bonds OFF, field ON, gap = 12, **M=2 vs M=1**. Expect
  `B_fire(M=2) == B_fire(M=1)` — direct empirical confirmation that the field channel ignores the bond topology.

## Pre-registration (FROZEN 2026-06-12 — no post-hoc tuning, NULL stands)

- **Seeds:** {42, 7, 13}. (Note: this configuration has free vibrations emitted with RNG-seeded directions, so
  seeds DO exercise variance here, unlike G159.)
- **Mechanism-fired check:** A fires in all arms; M=2 holds 2 components; free vibrations are emitted and at least
  one is integrated somewhere (field active).
- **Frozen marker & bars:**
  - **Sanity (gate):** `B_fire(B, gap=4) ≥ 5`. If it fails → **FAIL-insensitive** (field never crosses even
    close; redesign; not a pass).
  - **Primary:** `B_fire(A, gap=12)`.
    - **NULL** (predicted, per G86) if `B_fire(A) > 1`: the field leaks across the topological cut → the H₀
      partition gates the bond channel ONLY; the field channel is **not** contained by topology and requires a
      separate mechanism (spatial separation or active field gating).
    - **"isolated-but-not-by-topology"** if `B_fire(A) ≤ 1` (with sanity holding): the field is **spatially
      contained at gap 12** — but since the field is topology-independent (arm C), this is a *geometry* result,
      NOT a topological one. Report as such; do not credit topology.
  - **Confirmation:** arm C must show `B_fire(M=2) == B_fire(M=1)` (bonds off). If it does, topology-independence
    of the field is empirically confirmed.

## Pre-committed interpretation

- The honest expected outcome is **NULL** (field leaks): topology gates bonds (G159), spatial separation gates the
  field (G86). G160 then *completes the two-channel design rule* — a modular activity-isolating scaffold needs
  BOTH a topological bond cut AND spatial separation (and still nothing about atom erosion, G93). Necessary
  components, assembled; not yet a memory-deadlock break.
- A surprising `B_fire(A) ≤ 1` would only mean the required separation is < 12 units; it still would not be a
  topological effect (arm C shows the field ignores M).

## Integrity caveat (log it)

A NULL here does **not** weaken G159: G159's bond-channel isolation stands; G160 probes a *different* channel. The
combined picture is "H₀ topology gates bond-mediated spread; field-mediated spread needs spatial separation,"
mirroring G86's two-part containment with each part now attributed to its mechanism.

## Engine / tooling

`tools/g160_field_channel_isolation.py` — extends the G159 harness: enables emission (`n_emit=8`) and free
vibrations, runs arms A/B/C, logs to `LOGBOOK.md`.

## Reproducibility

Engine `world/` @ branch `g160-field-channel`; macOS-arm64, Python 3.13 (`uv run`); seeds {42,7,13}; field on
(emission + r_integrate); bars frozen pre-run; sanity must hold for an informative verdict; NULL stands.

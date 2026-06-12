# R1 — Decouple the write/store variable from the propagation field (eligibility-as-store)

**Authored / FROZEN:** 2026-06-12 · **Status:** pre-registered, no run yet · **Phase:** redesign R1 (first
emergence-preserving primitive change). **Derives from:** `docs/redesign/design_requirements.md` R3 (separate
write & propagation channels), addressing deadlock **D4 (write=leak)** and bearing on **D2/D3**.
**Engine:** `world/physics.py::apply_btsp` (eligibility update), `neuron_dynamics`. Branch `redesign-charter`.

## The idea (emergence-preserving, reuses an existing primitive)

The legacy deadlock D4: the field that *writes* a memory is the field that *leaks* it — write, propagate, and
leak are one variable (charge). R1 tests whether moving the STORE to a variable that is **slow, per-atom, and
non-propagating** breaks that coupling. The substrate already has exactly such a variable: `k_eligibility` — a
BTSP trace that decays with `btsp_tau_eligibility = 6 s` (≈12× slower than charge's `tau_membrane = 0.5 s`), is
bumped **+1 only on the firing atom's own index** (`physics.py:607`), and **never propagates** to neighbours via
field or bonds. This is not a new primitive (no hand-built RAM); it is a *readout change*: read the eligibility
trace as the memory, instead of reading the ongoing charge/firing field.

**Hypothesis (M beats B):** with firing contained, the eligibility store holds a **selective** (control region
blank) and **persistent** (survives a recall window with no drive) memory, where the charge field cannot — the
charge field is reset to 0 on every firing and decays in ~0.5 s, so it is not a store at all.

## Probe (exact)

Two regions, A = {x=10,16,22}, B = {x=40,46,52}, atoms injected via `allocate_node`, pinned. Quiet substrate
(`lambda_gen=lambda_dec=0` — erosion OFF, to isolate D4; D3 is explicitly out of scope here). `btsp_enabled=True`,
`neuron_dynamics_enabled=True`, `theta_fire=4`. WRITE: drive `k_charge[A]=10` each tick for `T_WRITE=60`; B never
driven. RECALL: stop all drive, run `T_RECALL=120` (~2 s) quiet. READ `k_eligibility` and `k_charge` of A and B.

Three arms:
- **Arm 1 — contained (primary):** `atom_valence=0` (no bonds), `n_emit=0` (no field emission). Firing is purely
  local → B can only fire if it leaks; it can't. Measure eligibility & charge selectivity + persistence.
- **Arm 2 — negative control:** identical to Arm 1 but **A is not driven**. Memory must NOT appear.
- **Arm 3 — uncontained boundary (recorded, not barred):** `n_emit=8`, gap small so the field reaches B. Tests
  whether eligibility leaks when firing is *not* contained (expected: yes — eligibility rises on B because the
  field makes B fire). Bounds the claim: R1 is necessary, not sufficient.

## Pre-registration (FROZEN 2026-06-12 — no post-hoc tuning, NULL stands)

- **Seeds:** {42, 7, 13}.
- **Mechanism-fired:** Arm 1 — A fires (`a_fire>0`) and B does NOT fire (`b_fire=0`, containment real).
- **Marker (Arm 1, primary):**
  - **Selectivity** `S = elig(B)/elig(A) ≤ 0.10` (the store does not leak to the control region).
  - **Persistence** `P = elig(A, end-of-recall) / elig(A, post-write-peak) ≥ 0.50` (survives the recall window).
  - **Store-vs-field (illustrative, reported):** `charge(A, end)` ≈ 0 — the charge field is not a persistent
    store (reset on fire + fast decay). Reported, not a pass gate.
- **Negative control (Arm 2, MUST hold):** `elig(A) ≤ 0.10` (no memory without a write).
- **Boundary (Arm 3, recorded):** `elig(B)/elig(A)` with the field on — expected `> 0.30` (eligibility leaks via
  field-induced B firing), confirming R1 needs containment (the G158/G159 partition + active flux management).
- **Bars:**
  - **PASS** — Arm 1 `S ≤ 0.10` AND `P ≥ 0.50` AND Arm 2 `elig(A) ≤ 0.10` AND mechanism-fired. Decoupling the
    store from the propagation field yields a selective, persistent, non-destructively-read memory.
  - **NULL** — `S > 0.10` (store leaks even when firing is contained) OR `P < 0.50` (does not persist).
    **Pre-registered conclusion if NULL:** decoupling write from propagation does NOT help — the deadlock is
    deeper than the field-coupling; escalate to (b) per-bond rest length or (c) directed/irreversible binding,
    or conclude the deadlock is inherent.

## Honest scope (no overclaim)

R1 isolates **one** break (D4, write≠propagate). It does NOT address: **D3 erosion** (turned off here via
`lambda_dec=0`; with decay on, an eroding atom takes its eligibility with it); **D1/D2 containment** (Arm 3 shows
eligibility leaks when firing is uncontained — R1 must be *composed* with the G159 partition and active flux
management). The persistence relies on the slow `tau_eligibility` and erosion-off, so a PASS demonstrates the
*design property* (a slow, local, non-propagating store decoupled from the fast field), not a full memory system.
A PASS is "D4 is breakable with an emergent local variable"; it is one of the three+ breaks the taxonomy requires.

## Engine / tooling

`tools/redesign_r1_eligibility_store.py`: injects A/B atoms, runs the three arms over seeds {42,7,13}, reports
eligibility/charge selectivity + persistence, logs to `LOGBOOK.md`.

## Reproducibility

Engine `world/` @ branch `redesign-charter`; macOS-arm64, Python 3.13 (`uv run`); seeds {42,7,13}; erosion off
(isolates D4); bars frozen pre-run; mechanism-fired + negative control mandatory; NULL stands.

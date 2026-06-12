# G158 — Topological (H₀-persistence) bond-formation rule: emergent vs engineered modularity

**Authored / FROZEN:** 2026-06-12 · **Status:** pre-registered, no run yet · **Thread:** substrate physics (`gNNN`)
**Grounding:** `world/bridges.py` (`form_bridges`, `apply_bridge_tension`), `LOGBOOK.md` G86 + G88–G95,
`docs/MEMORY_PROGRAMME_SUMMARY.md`, `docs/patterns/01`, `docs/patterns/03`. Engine `world/` @ `g154-matter-recall`.

## Honest scope (read first — this is NOT a memory-deadlock break)

This amendment was reframed before drafting after an adversarial check against the closed threads. The original
intent ("a topological bond rule attacks the percolation deadlock") **would re-derive G86**: percolation is
already known to be *containable* (G86 hand-placed `compartment_boundary` plane; G88–G95 quiet substrate). The
binding constraint of the memory deadlock is the *orthogonal* dilemma **active → write starves / quiet → atoms
erode** (G93), which no bond-graph rule can touch.

So G158 makes only this bounded claim: **a persistent-homology (H₀ / connected-component) constraint on bond
formation can SELF-ORGANISE and STABLY MAINTAIN a modular partition of the structural bond graph — with the
partition determined by graph topology, not by experimenter-specified geometry (unlike G86's plane) — and that
partition functionally isolates modules in the tension graph.** It does **not** address the charge-integration
field channel (`r_integrate`), and it does **not** make selective persistent memory work (starve/erode stands).
A PASS means "emergent modularity is achievable and stable" — necessary, not sufficient, for modular memory.
This is an emergence-of-modularity / tooling result, pre-registered as such.

## The new math (the rule)

The `b_alive` bond graph over level-4 atoms. Maintain a target module count **M** (the H₀-persistence threshold:
keep ≥ M persistent connected components). When the native candidate search (atoms within `r_2`, valence room,
no duplicate) proposes a bond (i, j), accept it iff, on a union-find over the *current* bond graph:

- i, j already in the same component → ACCEPT (intra-module; component count unchanged), or
- i, j in different components AND current component count > M → ACCEPT (still above target), else
- → **REJECT** (this is the edge across a bottleneck whose addition would kill a persistent H₀ feature).

The cut is chosen by **graph topology only** — never by an atom coordinate or a spatial plane. That is the entire
difference from G86. Spectral diagnostic reported alongside: number of components and algebraic connectivity λ₂
(= 0 whenever the graph stays in ≥ 2 components — the spectral signature of the maintained partition).

## Pre-registration (FROZEN 2026-06-12 — no post-hoc tuning, NULL stands)

- **Seeds:** {42, 7, 13}; report mean ± SD.
- **Substrate:** quiet (λ_gen = λ_dec = 0), bridge tension the ONLY inter-atom force (atom_repulsion_k = 0,
  curvature_k = 0, node_thermal_speed = 0, neuron dynamics off). Two atom clusters A and B joined by a single
  candidate "bottleneck" edge. r_2 set so the bottleneck pair is bondable.
- **Treatment:** rule with **M = 2** (keep A and B as two components). **Negative control:** **M = 1** (rule
  effectively off → one component). Only the M parameter differs.
- **Mechanism-fired check (pattern 01), BEFORE believing any verdict:** confirm bonds form, components are
  actually maintained at M over all T ticks, and the constraint rejects ≥ 1 bottleneck merge in the M = 2 arm.
- **Marker (single, functional):** mechanical-percolation ratio **P = mean|Δpos(B)| / DX** after the A cluster is
  displaced by DX and the world is relaxed for T ticks under tension. P measures how much a perturbation of A
  propagates to B through the bond/tension graph.
- **Bars:**
  - **PASS** — `P(M=2) ≤ 0.10` AND components stay = 2 for all T ticks AND the control `P(M=1) ≥ 0.30`
    (the rule is what produces the isolation; the channel genuinely percolates without it).
  - **PARTIAL** — isolation holds (`P(M=2) ≤ 0.10`) but control is weak (`0.10 < P(M=1) < 0.30`): the rule works
    but the test is under-sensitive; report and re-state, do not tune.
  - **NULL** — `P(M=2) > 0.10` (the rule fails to isolate) OR components do not stay at 2.
  - **FAIL** — control also isolates (`P(M=1) ≤ 0.10`): the partition is an artifact of geometry, not the rule.

## Engine / tooling

`tools/g158_topological_bond_rule.py`: monkeypatches `world.bridges.form_bridges` with the constrained,
union-find version (`tick()` re-imports the name at call time, so the patch takes effect), builds the A–B
dumbbell, runs treatment (M=2) and control (M=1), and computes P, component trajectory, rejected-merge count,
and λ₂. Logs to `LOGBOOK.md`.

## Payoff (honest)

- **Brain science:** a principled-topology rule (preserve H₀ persistence) self-organises stable modules from a
  homogeneous medium without a hand-drawn boundary — a constructive sketch of how emergent modularity could arise
  from a local connection constraint rather than from anatomy imposed by fiat. A NULL teaches that an H₀ rule on
  the structural graph is insufficient to bound the dynamics that matter.
- **AI learning:** reusable tooling — persistent-homology / union-find constraint on a *dynamic* graph — and, per
  pattern 03, a clean instance of the gate "does the formalism touch the variable the constraint is about?" Here
  it touches the structural graph, not the charge field, so even a PASS is explicitly scoped away from the memory
  deadlock.

## Reproducibility

Engine `world/` @ branch `g154-matter-recall`; macOS-arm64, Python 3.13 (`uv run`); seeds {42, 7, 13}; quiet
substrate, tension-only. Bars above frozen pre-run; mechanism-fired check mandatory; control must percolate for a
PASS to count; NULL stands.

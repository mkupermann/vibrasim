# Flux Substrate F1b — Bridges + Plasticity + Flux-Coupled Decay → T4

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement bridges, structure-flux, Hebbian plasticity, bridge breakage, and node dissociation per spec §5.4 + §5.5. Replace F1a's T-based decay stub with the proper bridge-flux-coupled decay. Make Phase-1 test T4 (decay-without-flux) pass while keeping T1 + T3 green.

**Architecture (per spec §5.4 + §5.5):**

- **Bridges** are directed weighted edges between nodes. Created at binding time when a new node forms near existing nodes (and from quanta-pair → 2 directed bridges if multi-way binding is on the F1b path; F1b PAIRS-ONLY scope keeps binding 2:1 like F1a).
- **Structure-flux**: each tick, count free vibrations passing within distance `r_flux` of each node-pair's centroid. That count is the "flux through" the bridge.
- **Plasticity** (spec §5.5):
  - Strengthen: `w(t+1) = w(t) + γ * flux_through(t)`
  - Decay (per-bridge): `w(t+1) = w(t) - λ * max(0, flux_min - flux_through(t))`
- **Bridge breakage**: when `w < w_min`, remove bridge.
- **Node dissociation**: when a node has no remaining bridges, remove it; return its energy to the export channel (decay heat).
- **F1a T-based decay is REMOVED.** Its job (suppressing hot-zone accumulation) is now done by the bridge-flux mechanism: floor nodes form alongside many transient bindings that don't last long enough to form stable bridges, so they dissociate; ceiling nodes cluster more (preferential cold-zone binding) and reinforce each other's bridges via through-flux.

**Tech Stack:** Python 3.13, numpy (already a dep), pytest. No new dependencies.

**Spec reference:** `docs/superpowers/specs/2026-05-10-flux-substrate-design.md` — read §5.4 (binding & structures), §5.5 (plasticity), §7 T4 (decay-without-flux acceptance), §6 (tick order: spec puts structure-flux at step 6, decay at step 7, T-update at step 8).

**Estimated wallclock:** 2–4 weeks solo (compressed to hours under autonomous-build).

**Acceptance contract:**
- `uv run pytest tests/flux/test_decay.py -v` passes (T4)
- `uv run pytest tests/flux/test_crystallization.py -v` still passes (T3 — bridge-flux decay still gives cold-zone preference)
- `uv run pytest tests/flux/test_conservation.py -v` still passes (T1 with all F1b mechanisms active)
- All 64 F1a flux tests still pass (or rewritten counterparts)
- All 382 legacy tests still pass

---

## What F1b deliberately defers to F1c / F2

| Concept | Status in F1b | Where it lands |
|---|---|---|
| Multi-way binding (3+ quanta → 1 node) | NOT implemented | F1c or later |
| Node-to-node binding (two existing nodes bind into a parent) | NOT implemented | F1c |
| T2 Bénard acceptance test | NOT in scope | F1c |
| `pred_coherence` as windowed cross-correlation | still simplified to freq-eq (F1a stub) | F2 (cochlea) |
| Cochlea + Synthesis | NOT in scope | F2 |
| Attention reallocate (spec §6 step 9) | NOT in scope | F2 |

Single-frequency injection (T3's setup) keeps `pred_coherence` trivially 1.0 for all pairs. The F1a calibration regime continues to apply.

---

## File structure (locked decisions)

New files:

| Path | Responsibility |
|---|---|
| `world/flux/bridges.py` | `Bridges` SoA container — pre-allocated arrays for up to `MAX_BRIDGES` directed weighted edges. Stores `(src_node, dst_node, weight, last_flux_tick)`. |
| `world/flux/plasticity.py` | The two Hebbian rules: `strengthen` and `decay_per_bridge`. Plus `count_flux_through_bridge` helper. |
| `tests/flux/test_bridges.py` | Bridges container unit tests. |
| `tests/flux/test_plasticity.py` | Plasticity rule unit tests (strengthen + decay + breakage + dissociation). |
| `tests/flux/test_decay.py` | T4 integration test (the acceptance test for F1b). |

Modified files:

| Path | What changes |
|---|---|
| `world/flux/binding.py` | At binding time, create bridges to nearby existing nodes (within `r_bridge`) with initial weight proportional to coherence. |
| `world/flux/dynamics.py` | New tick steps between binding and T-update: structure-flux + plasticity + bridge-breakage + node-dissociation. New kwargs `bridges`, `plasticity_cfg`. F1a-mode return becomes `(exported, binding_heat, decay_heat)` still — decay_heat now includes node-dissociation energy. |
| `world/flux/audit.py` | Auditor learns about `Bridges` reference; conservation includes bridge weights only as internal state (no energy stored in bridges per spec — bridges are weights, not stocks). `record_decay_heat` continues to track node-dissociation energy export. |
| `world/flux/decay.py` | **DELETED.** Functionality replaced by bridge-flux-coupled dissociation in plasticity.py. (Or: kept as deprecated shim that raises if called.) |
| `world/flux/__init__.py` | Drop `DecayConfig`/`attempt_decay`/`decay_probability`. Re-export `Bridges`, `PlasticityConfig`, plasticity helpers. |
| `tests/flux/test_crystallization.py` | Drop `DecayConfig` import + `decay_cfg=` kwarg; pass `bridges=`, `plasticity_cfg=` instead. May need T3 ratio re-calibration. |
| `tests/flux/test_conservation.py` | Same — replace `decay_cfg` with `bridges` + `plasticity_cfg`. |
| `tests/flux/test_dynamics.py` | 3-tuple unpack already in place. |
| `docs/flux/phase-log.md` | F1b start + close entries. |
| `README.md` | One-line status update on F1b. |

---

## Task 1: F1b start — phase-log entry

**Files:**
- Modify: `docs/flux/phase-log.md`

- [ ] **Step 1: Append F1b-start entry**

```markdown

## 2026-05-11 — F1b start

- F1a closed: 64/64 flux + 382 legacy + T3 ratio 9.0; commits `f68705a..a6e5c78`.
- F1b target: T4 (decay-without-flux) passes; T1 + T3 still green.
- F1b implements spec §5.4 (bridges + structure-flux) + §5.5 (plasticity) +
  proper bridge-flux-coupled dissociation. The F1a T-based decay stub is
  REPLACED by the bridge-flux mechanism (DecayConfig removed).
- Plan: `docs/superpowers/plans/2026-05-11-flux-substrate-F1b.md`.
- Estimated 2–4 weeks solo; compressed under autonomous-build.
```

- [ ] **Step 2: Commit**

```bash
git add docs/flux/phase-log.md
git commit -m "flux F1b start: phase-log entry

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Bridges SoA container

**Files:**
- Create: `world/flux/bridges.py`
- Create: `tests/flux/test_bridges.py`

Same SoA pattern as `Quanta` and `Nodes`. Each bridge has src_slot, dst_slot, weight, last_flux_tick (for decay accounting).

- [ ] **Step 1: Write failing tests `tests/flux/test_bridges.py`**

```python
"""Tests for Bridges SoA container."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.bridges import Bridges


def test_bridges_empty_on_init():
    b = Bridges(max_bridges=100)
    assert b.max_bridges == 100
    assert b.n_alive() == 0
    assert b.alive.shape == (100,)
    assert b.alive.dtype == np.bool_
    assert b.src.shape == (100,)
    assert b.dst.shape == (100,)
    assert b.weight.shape == (100,)
    assert b.last_flux_tick.shape == (100,)


def test_bridges_add_returns_slot_and_writes_fields():
    b = Bridges(max_bridges=10)
    slot = b.add(src=3, dst=7, weight=0.5, born_tick=42)
    assert slot == 0
    assert bool(b.alive[0])
    assert int(b.src[0]) == 3
    assert int(b.dst[0]) == 7
    assert float(b.weight[0]) == 0.5
    assert int(b.last_flux_tick[0]) == 42
    assert b.n_alive() == 1


def test_bridges_add_uses_free_slots_in_order():
    b = Bridges(max_bridges=5)
    for i in range(3):
        b.add(src=i, dst=i+1, weight=1.0, born_tick=0)
    assert b.n_alive() == 3
    b.remove(1)
    assert not bool(b.alive[1])
    slot = b.add(src=99, dst=100, weight=2.0, born_tick=10)
    assert slot == 1  # Reuses freed slot


def test_bridges_remove_marks_slot_free():
    b = Bridges(max_bridges=5)
    s = b.add(src=1, dst=2, weight=1.0, born_tick=0)
    b.remove(s)
    assert not bool(b.alive[s])
    assert float(b.weight[s]) == 0.0


def test_bridges_add_returns_minus_one_when_full():
    b = Bridges(max_bridges=2)
    b.add(src=0, dst=1, weight=1.0, born_tick=0)
    b.add(src=1, dst=2, weight=1.0, born_tick=0)
    slot = b.add(src=2, dst=3, weight=1.0, born_tick=0)
    assert slot == -1


def test_bridges_find_by_endpoints():
    """Helper: find a bridge by (src, dst) — used by plasticity to
    avoid duplicate-bridge creation."""
    b = Bridges(max_bridges=10)
    b.add(src=1, dst=2, weight=1.0, born_tick=0)
    b.add(src=2, dst=3, weight=2.0, born_tick=0)
    assert b.find(src=1, dst=2) == 0
    assert b.find(src=2, dst=3) == 1
    assert b.find(src=3, dst=4) == -1
    assert b.find(src=2, dst=1) == -1  # directed, not symmetric
```

- [ ] **Step 2: Implement `world/flux/bridges.py`**

```python
"""Bridges — SoA container for node-to-node directed weighted edges."""
from __future__ import annotations
import numpy as np


class Bridges:
    """Pre-allocated SoA container for bridges between nodes.

    Each bridge: src_slot, dst_slot, weight, last_flux_tick.
    Directed: bridge(a→b) is distinct from bridge(b→a).
    """

    def __init__(self, max_bridges: int):
        self.max_bridges = int(max_bridges)
        N = self.max_bridges
        self.src = np.zeros(N, dtype=np.int64)
        self.dst = np.zeros(N, dtype=np.int64)
        self.weight = np.zeros(N, dtype=np.float64)
        self.last_flux_tick = np.zeros(N, dtype=np.int64)
        self.alive = np.zeros(N, dtype=np.bool_)
        self._next_search = 0

    def n_alive(self) -> int:
        return int(self.alive.sum())

    def add(self, src: int, dst: int, weight: float,
            born_tick: int) -> int:
        N = self.max_bridges
        for i in range(N):
            j = (self._next_search + i) % N
            if not self.alive[j]:
                self.src[j] = int(src)
                self.dst[j] = int(dst)
                self.weight[j] = float(weight)
                self.last_flux_tick[j] = int(born_tick)
                self.alive[j] = True
                self._next_search = (j + 1) % N
                return j
        return -1

    def remove(self, slot: int) -> None:
        if not self.alive[slot]:
            return
        self.alive[slot] = False
        self.weight[slot] = 0.0
        self._next_search = min(self._next_search, slot)

    def find(self, src: int, dst: int) -> int:
        """Return the alive bridge slot with (src, dst) or -1."""
        mask = self.alive & (self.src == src) & (self.dst == dst)
        idx = np.where(mask)[0]
        if idx.size == 0:
            return -1
        return int(idx[0])
```

- [ ] **Step 3: Run** `uv run pytest tests/flux/test_bridges.py -v`. Expected: 6/6 pass.

- [ ] **Step 4: Commit** `flux F1b task 2: Bridges SoA container`.

---

## Task 3: Bridge creation at binding time

When a new node forms via `attempt_binding`, also create directed bridges from the new node to all existing alive nodes within `r_bridge` (default same as `r`). Initial bridge weight is proportional to `pred_coherence` of the binding pair (since coh=1.0 in F1a regime, all initial weights = `bridge_w0`).

**Files:**
- Modify: `world/flux/binding.py`

- [ ] **Step 1: Add `r_bridge` and `bridge_w0` to BindingConfig**

```python
@dataclass
class BindingConfig:
    alpha: float = 4.0
    beta: float = 4.0
    T_crit: float = 2.0
    eta: float = 0.1
    r: float = 1.5
    coherence_eps: float = 1.0
    # F1b additions:
    r_bridge: float = 2.0       # radius for bridge-to-existing-nodes
    bridge_w0: float = 1.0      # initial bridge weight per coherence
```

- [ ] **Step 2: Extend `attempt_binding` to take optional `bridges: Bridges`**

When a binding fires:
1. Create node as before (existing logic).
2. If `bridges` is given, iterate alive nodes within `r_bridge` of new node's centroid. For each, create one bridge new_node→existing and one bridge existing→new_node, both with weight `bridge_w0 * coh`.

If bridges buffer is full (add returns -1), skip bridge creation but keep node (log a warning).

- [ ] **Step 3: Unit test in `tests/flux/test_binding.py`** for "binding near existing node creates 2 bridges".

- [ ] **Step 4: Run** `uv run pytest tests/flux/test_binding.py -v`. All pass.

- [ ] **Step 5: Commit** `flux F1b task 3: bridge creation at binding`.

---

## Task 4: Structure-flux measurement

Each tick, for every alive bridge, count the number of free vibrations within `r_flux` of the line segment connecting the two nodes. That count is the "flux through" the bridge.

**Files:**
- Modify: `world/flux/plasticity.py` (create)

- [ ] **Step 1: Define `PlasticityConfig`**

```python
@dataclass
class PlasticityConfig:
    gamma: float = 0.1       # strengthening rate (spec §5.5)
    lam: float = 0.1         # decay rate (spec §5.5)
    flux_min: float = 1.0    # below this, decay applies
    w_min: float = 0.05      # bridge breakage threshold
    r_flux: float = 0.75     # half-thickness of bridge tube
```

- [ ] **Step 2: Implement `count_flux_through(bridges, nodes, quanta)`**

For each alive bridge `b=(src,dst)`, count alive quanta within distance `r_flux` of segment src.pos → dst.pos. Returns `np.ndarray` of shape `(max_bridges,)` with counts.

Naive O(N_q * N_b) — fine for F1b scale.

- [ ] **Step 3: Tests in `tests/flux/test_plasticity.py`**: place a bridge, place quanta on/off the segment, confirm counts.

- [ ] **Step 4: Commit** `flux F1b task 4: structure-flux count`.

---

## Task 5: Plasticity rules (strengthen + decay)

Apply both Hebbian rules per tick:
- `w_new = w_old + γ * flux_through`
- `w_new -= λ * max(0, flux_min - flux_through)`

Then mark `last_flux_tick = current_tick` for any bridge where flux > 0.

**Files:**
- Modify: `world/flux/plasticity.py`

- [ ] **Step 1: Implement `apply_plasticity(bridges, flux_counts, cfg, tick_index)`**

In-place update of `bridges.weight` and `bridges.last_flux_tick`.

- [ ] **Step 2: Tests**: bridge with flux > flux_min → weight grows; bridge with zero flux → weight shrinks.

- [ ] **Step 3: Commit** `flux F1b task 5: Hebbian plasticity`.

---

## Task 6: Bridge breakage + node dissociation

After plasticity, scan bridges: those with `weight < w_min` are removed. After bridge removal, scan nodes: any node that no longer appears in any alive bridge's `src` or `dst` is dissociated (removed), and its energy is exported as decay heat.

**Files:**
- Modify: `world/flux/plasticity.py`

- [ ] **Step 1: Implement `prune_bridges_and_nodes(bridges, nodes, cfg) -> dissociation_heat`**

```python
def prune_bridges_and_nodes(bridges, nodes, cfg):
    # 1. Remove bridges with weight < w_min
    for slot in np.where(bridges.alive & (bridges.weight < cfg.w_min))[0]:
        bridges.remove(int(slot))
    # 2. Dissociate orphan nodes
    if nodes.n_alive() == 0:
        return 0.0
    alive_bridge_endpoints = set()
    for i in np.where(bridges.alive)[0]:
        alive_bridge_endpoints.add(int(bridges.src[i]))
        alive_bridge_endpoints.add(int(bridges.dst[i]))
    total_decay_heat = 0.0
    for slot in np.where(nodes.alive)[0]:
        if int(slot) not in alive_bridge_endpoints:
            e = nodes.remove(int(slot))
            total_decay_heat += e
    return total_decay_heat
```

Edge case: nodes that JUST formed have no bridges yet if there were no nearby existing nodes at binding time. To avoid instant dissociation, give new nodes a grace period of `K_grace` ticks (default 5). Add `born_tick` check.

Actually simpler: at binding time, ALWAYS create a self-bridge (src=slot, dst=slot, weight=bridge_w0) so the node never starts orphan. Self-bridge gets the same plasticity. If isolated, the self-bridge decays first; only then does the node dissociate.

Decision: **use self-bridge**. Update Task 3 to also create a self-bridge.

- [ ] **Step 2: Tests** for: bridges with low weight get pruned; orphan nodes dissociate; self-bridge prevents instant death; energy accounted.

- [ ] **Step 3: Commit** `flux F1b task 6: prune bridges + dissociate orphan nodes`.

---

## Task 7: Wire F1b into the tick

Tick order (spec §6 conformant):

1. Inject
2. Move
3. Absorb
4. Bind (creates nodes + bridges via Task 3)
5. **Structure-flux** (count flux per bridge — Task 4)
6. **Plasticity** (apply Hebbian rules — Task 5)
7. **Prune + dissociate** (Task 6) → returns decay_heat
8. Update T

**Files:**
- Modify: `world/flux/dynamics.py`

- [ ] **Step 1: Add `bridges` and `plasticity_cfg` kwargs to `tick`**

Return shape stays `(exported, binding_heat, decay_heat)` where `decay_heat` is now from node dissociation (not from the F1a T-based stub).

- [ ] **Step 2: Remove import of `attempt_decay` / `DecayConfig` from dynamics; remove decay_cfg kwarg.**

- [ ] **Step 3: Update test_dynamics tests if needed.**

- [ ] **Step 4: Commit** `flux F1b task 7: wire bridges/plasticity into tick`.

---

## Task 8: Auditor updates

The auditor's `record_decay_heat` still tracks all dissociation energy. Add the optional `bridges` reference for completeness — bridges hold no energy (per spec), so the conservation equation is unchanged in form.

- [ ] **Step 1: Add `bridges` kwarg to `EnergyAuditor.__init__`** (optional, for future use; no logic change).

- [ ] **Step 2: Commit** `flux F1b task 8: auditor bridges-aware`.

---

## Task 9: Remove F1a T-based decay (or deprecate)

The bridge-flux mechanism replaces F1a's `DecayConfig`. Choose:
- (A) **Delete** `world/flux/decay.py`. Update `world/flux/__init__.py` and all tests. Clean break.
- (B) **Keep as deprecated**, mark with `warnings.warn(DeprecationWarning(...))`. More backward-compatible but leaves dead code.

**Decision: (A) — delete.** F1b is the first user. No external API consumers.

- [ ] **Step 1: Remove `world/flux/decay.py`.**

- [ ] **Step 2: Update `world/flux/__init__.py`** to drop `DecayConfig`, `attempt_decay`, `decay_probability`.

- [ ] **Step 3: Update tests/flux/test_crystallization.py** to use `bridges=` and `plasticity_cfg=` instead of `decay_cfg=`. May need re-tuning.

- [ ] **Step 4: Update tests/flux/test_conservation.py::test_T1_conservation_with_binding_active** similarly.

- [ ] **Step 5: Run** `uv run pytest tests/flux/test_conservation.py -v` — T1 must still pass with F1b mechanisms active.

- [ ] **Step 6: Run T3** — may need plasticity-config tuning. Up to 5 sweeps, log to phase-log.

- [ ] **Step 7: Commit** `flux F1b task 9: remove F1a T-based decay`.

---

## Task 10: T4 decay-without-flux integration test

Spec §7 T4: "Form structures via T3. Disable injection. 5000 more ticks. structure_count(end) / structure_count(peak) < 0.10."

**Files:**
- Create: `tests/flux/test_decay.py`

- [ ] **Step 1: Write `tests/flux/test_decay.py`**

```python
"""T4 — Structures decay when flux stops.

Spec §7 T4: form structures via T3 (5000 ticks with injection),
then disable injection and run 5000 more ticks. Structure count at
end should be < 10% of peak count (during the T3 phase).

This is the F1b acceptance test.
"""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.audit import EnergyAuditor
from world.flux.boundary import inject_hot_floor
from world.flux.dynamics import tick
from world.flux.structures import Nodes
from world.flux.bridges import Bridges
from world.flux.binding import BindingConfig
from world.flux.plasticity import PlasticityConfig


def test_T4_decay_without_flux():
    rng_inject = np.random.default_rng(42)
    rng_bind = np.random.default_rng(123)
    q = Quanta(max_quanta=50_000)
    n = Nodes(max_nodes=50_000)
    br = Bridges(max_bridges=200_000)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, nodes=n, bridges=br, tol=1e-9)
    audit.record_initial()

    cfg = BindingConfig(alpha=4.0, beta=4.0, T_crit=2.0, eta=0.1,
                        r=1.5, coherence_eps=1.0,
                        r_bridge=2.0, bridge_w0=1.0)
    pcfg = PlasticityConfig(gamma=0.1, lam=0.1, flux_min=1.0,
                            w_min=0.05, r_flux=0.75)

    def injector(quanta, grid):
        count = inject_hot_floor(quanta, grid, n=5, energy_per=1.0,
                                  freq_mean=200.0, vel_z_mean=2.0,
                                  rng=rng_inject)
        audit.record_injection(count * 1.0)
        return count * 1.0

    # Phase A: 5000 ticks with injection
    peak = 0
    for t in range(5000):
        exp, bh, dh = tick(q, g, dt=0.1, injector=injector,
                            nodes=n, binding_cfg=cfg,
                            bridges=br, plasticity_cfg=pcfg,
                            rng=rng_bind, tick_index=t)
        audit.record_export(exp)
        audit.record_binding_heat(bh)
        audit.record_decay_heat(dh)
        audit.check()
        audit.step()
        peak = max(peak, int(n.n_alive()))

    assert peak > 0, "No structures formed in Phase A"

    # Phase B: 5000 ticks WITHOUT injection
    for t in range(5000, 10000):
        exp, bh, dh = tick(q, g, dt=0.1, injector=None,
                            nodes=n, binding_cfg=cfg,
                            bridges=br, plasticity_cfg=pcfg,
                            rng=rng_bind, tick_index=t)
        audit.record_export(exp)
        audit.record_binding_heat(bh)
        audit.record_decay_heat(dh)
        audit.check()
        audit.step()

    end_count = int(n.n_alive())
    ratio = end_count / peak
    assert ratio < 0.10, (
        f"T4 decay ratio {ratio:.3f} not below 0.10. "
        f"peak={peak}, end={end_count}."
    )
```

- [ ] **Step 2: Run** `uv run pytest tests/flux/test_decay.py -v`. May need plasticity tuning.

- [ ] **Step 3: Up to 5 plasticity-config sweeps** if T4 fails. Log each in phase-log.

- [ ] **Step 4: Run full suites + commit** `flux F1b task 10: T4 decay-without-flux passes`.

---

## Task 11: __init__ re-exports + README + F1b close

**Files:**
- Modify: `world/flux/__init__.py` (drop DecayConfig/attempt_decay/decay_probability; add Bridges, PlasticityConfig, apply_plasticity, count_flux_through, prune_bridges_and_nodes)
- Modify: `README.md` (F1b complete status)
- Modify: `docs/flux/phase-log.md` (F1b-close entry)

- [ ] **Step 1: Update `__init__.py`.** Drop F1a decay symbols, add F1b symbols.

- [ ] **Step 2: README**

```
Status as of 2026-05-11: F0 complete; F1a complete (binding + minimal
T-based decay stub); F1b complete (bridges + plasticity + flux-coupled
decay; T4 passes; F1a T-stub removed). F1c on the work list.
```

- [ ] **Step 3: Phase-log F1b-close entry** with task summary, test counts, final plasticity cfg, T4 ratio, T3 ratio after re-calibration if any.

- [ ] **Step 4: Run** `uv run pytest tests/flux/ -v` — expect all green.

- [ ] **Step 5: Run** `uv run pytest tests/ -q -x --ignore=tests/flux/ -k "not slow"` — expect 382 passing.

- [ ] **Step 6: Commit** `flux F1b complete: re-exports + README status + phase-log`.

---

## Notes for autonomous execution

- T4 is the binary gate. T1 + T3 must remain green. Don't lower T4's 0.10 threshold — it's pre-registered in spec §7.
- Plasticity tuning order if T4 fails: increase `lam` (faster decay without flux), increase `gamma` won't help (only when flux is present), lower `w_min` to keep bridges longer, lower `r_flux` so flux is harder to maintain.
- If T3 regresses after removing F1a T-decay: re-tune `BindingConfig.r_bridge` and `bridge_w0` — over-eager bridge creation makes floor clusters too sticky.
- If energy conservation fails: most likely cause is forgetting to record decay_heat in the test loop after a tick. Run the conservation test first as a smoke gate.
- The Bridges buffer needs to be large enough — N_nodes^2 worst case, but realistically ~10x N_nodes. For T4 with N_nodes ~ 1000 at peak, 200,000 bridges is comfortable.
- Hard blocker: if T4 requires lowering the 0.10 threshold OR if T3 cannot be re-tuned to pass with bridge mechanism, escalate — the bridge mechanic may itself need spec-level rethinking.

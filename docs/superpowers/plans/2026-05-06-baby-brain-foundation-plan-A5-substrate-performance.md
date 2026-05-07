# Plan A.5 — Substrate Performance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Break the quadratic sim-time → wall-time dependence in the substrate by (1) recycling dead node slots so `k_count` plateaus at steady-state population, and (2) Numba-JIT'ing the five hot per-tick loops. Both are pure performance changes — observable behaviour stays bit-identical.

**Architecture:** Two flags (`slot_recycling_enabled`, `numba_jit_enabled`), both default `True`. The flags exist for regression diagnosis; production runs always use both. Reference-counted slot recycling protects against premature reuse. Numba JIT'd cores receive pre-generated RNG rolls so the RNG stream is preserved and Plan A's seeded tests still pass.

**Tech Stack:** Python 3.13, NumPy, Numba (already a project dependency from the original Phase 1 build), pytest. No new dependencies.

**Spec reference:** `docs/superpowers/specs/2026-05-06-baby-brain-foundation-plan-A5-substrate-performance-design.md` — approved 2026-05-06 with all six approval-gate items accepted.

**Prerequisite:** Plan A merged to main. Plan A.5 lands before Plan B so that B's longer integration tests have perf headroom.

---

## File map

| Path | Action | Responsibility |
|---|---|---|
| `world/config.py` | Modify | Add `slot_recycling_enabled` + `numba_jit_enabled` |
| `world/state.py` | Modify | Add `k_ref_count`, `_free_slots`, `_free_slots_set`; modify `allocate_node` for recycling |
| `world/snapshot.py` | Modify | Persist + restore `k_ref_count` |
| `world/physics.py` | Modify | Add `_kill_node` helper; refactor decay paths to use it; convert `_UPGRADE_TARGET` to numpy array; add @njit cores for five hot functions; gate Python vs JIT path behind `numba_jit_enabled` |
| `tests/test_amendment_AP_slot_recycling_correctness.py` | Create | AP3, AP4 |
| `tests/test_amendment_AP_slot_recycling_plateau.py` | Create | AP5 |
| `tests/test_amendment_AP_behavioural_equivalence.py` | Create | AP1, AP2 |
| `tests/test_amendment_AP_jit_correctness.py` | Create | AP7-AP11 |
| `tests/test_amendment_AP_snapshot.py` | Create | AP6 |
| `tests/test_amendment_AP_performance.py` | Create | AP12, AP13 (slow) |

---

## Task 1: Add config flags

**Files:**
- Modify: `world/config.py`
- Test: `tests/test_config.py` (append)

- [ ] **Step 1.1: Write the failing test**

Append to `tests/test_config.py`:

```python
def test_AP_perf_flags_default_true():
    """Plan A.5 perf flags default ON (production path uses both)."""
    cfg = WorldConfig()
    assert cfg.slot_recycling_enabled is True
    assert cfg.numba_jit_enabled is True
```

- [ ] **Step 1.2: Run test, expect failure**

```bash
uv run pytest tests/test_config.py::test_AP_perf_flags_default_true -v
```

- [ ] **Step 1.3: Add the fields**

After Plan B's STDP fields (or wherever the config dataclass body ends), insert:

```python
    # Plan A.5 — substrate performance
    slot_recycling_enabled: bool = True   # World.allocate_node reuses dead slots before extending k_count
    numba_jit_enabled: bool = True        # @njit cores for hot loops
```

- [ ] **Step 1.4: Run test, expect pass**

```bash
uv run pytest tests/test_config.py -q
uv run pytest -q
```

- [ ] **Step 1.5: Commit**

```bash
git add world/config.py tests/test_config.py
git commit -m "feat(config): Plan A.5 perf flags default to True

Both flags exist for regression diagnosis; production runs use both.
slot_recycling_enabled toggles the free-list recycling path in
allocate_node; numba_jit_enabled toggles the @njit cores for the hot
per-tick loops."
```

---

## Task 2: Add `k_ref_count` field + free-list state

**Files:**
- Modify: `world/state.py` (extend `World.__init__`)
- Test: `tests/test_state.py` (append)

- [ ] **Step 2.1: Write the failing test**

Append to `tests/test_state.py`:

```python
def test_AP_k_ref_count_initialised_zero():
    """Plan A.5: per-slot reference count is zero at world init."""
    cfg = WorldConfig(n_initial_vibrations=0, n_nodes_max=16)
    w = World(cfg)
    assert w.k_ref_count.shape == (16,)
    assert w.k_ref_count.dtype == np.int32
    assert (w.k_ref_count == 0).all()
    assert w._free_slots == []
    assert w._free_slots_set == set()
```

- [ ] **Step 2.2: Run test, expect failure**

```bash
uv run pytest tests/test_state.py::test_AP_k_ref_count_initialised_zero -v
```

- [ ] **Step 2.3: Add the fields**

In `world/state.py`, after the existing `self.k_strength = np.ones(K, dtype=np.float64)` line, add:

```python
        # Plan A.5 — slot recycling
        self.k_ref_count = np.zeros(K, dtype=np.int32)
        self._free_slots: list[int] = []
        self._free_slots_set: set[int] = set()
```

- [ ] **Step 2.4: Run test, expect pass + suite green**

```bash
uv run pytest tests/test_state.py -q
uv run pytest -q
```

- [ ] **Step 2.5: Commit**

```bash
git add world/state.py tests/test_state.py
git commit -m "feat(state): add k_ref_count + free-list state for slot recycling"
```

---

## Task 3: Persist `k_ref_count` in snapshots

**Files:**
- Modify: `world/snapshot.py`
- Test: `tests/test_snapshot.py` (append)

- [ ] **Step 3.1: Write the failing test**

Append to `tests/test_snapshot.py`:

```python
def test_AP_snapshot_preserves_k_ref_count(tmp_path):
    """k_ref_count round-trips through save/load."""
    from world.config import WorldConfig
    from world.state import World
    from world.snapshot import save_snapshot, load_snapshot

    cfg = WorldConfig(n_initial_vibrations=0, n_nodes_max=8)
    w = World(cfg)
    w.k_ref_count[2] = 7
    w.k_ref_count[5] = 3
    p = tmp_path / "snapshot_t000000.00.npz"
    save_snapshot(w, p)
    w2 = load_snapshot(p)
    assert w2.k_ref_count[2] == 7
    assert w2.k_ref_count[5] == 3
    assert w2.k_ref_count[0] == 0
```

- [ ] **Step 3.2: Run test, expect failure**

```bash
uv run pytest tests/test_snapshot.py::test_AP_snapshot_preserves_k_ref_count -v
```

- [ ] **Step 3.3: Update save + load**

In `save_snapshot`, add `k_ref_count=world.k_ref_count` to the `np.savez(...)` call.

In `load_snapshot`, add the backward-compat read:

```python
    if "k_ref_count" in data.files:
        w.k_ref_count[:] = data["k_ref_count"]
```

Note: `_free_slots` and `_free_slots_set` are NOT persisted. They are derived state — on load, they start empty. The next decay tick will rebuild them.

- [ ] **Step 3.4: Run test, expect pass**

```bash
uv run pytest tests/test_snapshot.py -q
uv run pytest -q
```

- [ ] **Step 3.5: Commit**

```bash
git add world/snapshot.py tests/test_snapshot.py
git commit -m "feat(snapshot): persist k_ref_count across save/load

Free list (_free_slots, _free_slots_set) is derived state and starts
empty on load; the next tick's decay path rebuilds it as needed."
```

---

## Task 4: `_kill_node` helper

**Files:**
- Modify: `world/physics.py` (add new helper)
- Test: `tests/test_amendment_AP_slot_recycling_correctness.py` (create)

- [ ] **Step 4.1: Write the failing tests (AP3, AP4)**

Create `tests/test_amendment_AP_slot_recycling_correctness.py`:

```python
"""Tests for Plan A.5 slot recycling correctness (AP3, AP4)."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import _kill_node


def _make_world(n_nodes_max=8):
    cfg = WorldConfig(n_initial_vibrations=0, n_vibrations_max=4, n_nodes_max=n_nodes_max)
    return World(cfg)


def test_AP4a_kill_atom_with_no_references_recycles():
    """An atom that no molecule references → recyclable on kill."""
    w = _make_world()
    # Allocate one atom (manually, no allocate_node)
    w.k_pos[0] = [10, 10, 10]
    w.k_level[0] = 4
    w.k_alive[0] = True
    w.k_count = 1
    # k_comp_offset for slot 0: start=0, end=0 (no constituents)
    w.k_comp_offset[0] = 0
    w.k_comp_offset[1] = 0
    w.k_ref_count[0] = 0
    _kill_node(w, 0)
    assert not w.k_alive[0]
    assert 0 in w._free_slots_set
    assert w._free_slots == [0]


def test_AP4b_kill_atom_with_pending_reference_does_not_recycle():
    """An atom that a molecule still references must NOT be recycled
    when the atom dies — the molecule still depends on it."""
    w = _make_world()
    # Allocate atom slot 0
    w.k_pos[0] = [10, 10, 10]
    w.k_level[0] = 4
    w.k_alive[0] = True
    w.k_comp_offset[0] = 0
    w.k_comp_offset[1] = 0
    w.k_ref_count[0] = 1  # referenced by molecule below
    # Allocate molecule slot 1, with constituent = atom 0
    w.k_pos[1] = [10, 10, 10]
    w.k_level[1] = 5
    w.k_alive[1] = True
    w.k_comp_indices[0] = 0  # molecule 1 contains atom 0
    w.k_comp_offset[1] = 0
    w.k_comp_offset[2] = 1
    w.k_comp_used = 1
    w.k_count = 2
    # Kill the atom — its slot must NOT be recycled (still referenced)
    _kill_node(w, 0)
    assert not w.k_alive[0]
    assert 0 not in w._free_slots_set
    # Now kill the molecule — the molecule's slot should be recycled, AND
    # because the molecule's death decrements atom 0's ref count to 0,
    # atom 0's slot should ALSO be recycled.
    _kill_node(w, 1)
    assert not w.k_alive[1]
    assert 1 in w._free_slots_set
    assert 0 in w._free_slots_set


def test_AP3_slot_reused_after_decay():
    """When allocate_node is called and a slot is on the free list, it's reused."""
    w = _make_world()
    # Manually fill slot 0 then mark it dead and on the free list
    w.k_pos[0] = [10, 10, 10]
    w.k_level[0] = 4
    w.k_alive[0] = False  # already dead
    w.k_comp_offset[0] = 0
    w.k_comp_offset[1] = 0
    w._free_slots = [0]
    w._free_slots_set = {0}
    # allocate_node should reuse slot 0
    new_idx = w.allocate_node(
        pos=np.array([20, 20, 20], dtype=np.float64),
        freq=1000.0, pol=True, level=1,
        constituents=np.array([], dtype=np.int32), comp_kind=0,
    )
    assert new_idx == 0
    assert w._free_slots == []
    assert w._free_slots_set == set()
    # k_count must NOT have been incremented (slot 0 was already counted)
    assert w.k_count == 1
    # Slot 0 has the new node's data
    assert w.k_alive[0]
    assert w.k_level[0] == 1
```

- [ ] **Step 4.2: Run tests, expect failure**

```bash
uv run pytest tests/test_amendment_AP_slot_recycling_correctness.py -v
```

Expected: all three fail — `_kill_node` doesn't exist, `allocate_node` doesn't recycle.

- [ ] **Step 4.3: Add `_kill_node` to `world/physics.py`**

Insert after the existing helpers (after `_decade`, before `bind_nodes_upward`):

```python
def _kill_node(world, i: int) -> None:
    """Mark node i dead, decrement ref counts of its constituents,
    and push newly-recyclable slots onto the free list.

    Single source of truth for slot bookkeeping. Every code path that
    deactivates a node must funnel through this helper, otherwise ref
    counts go stale and slots are recycled prematurely.
    """
    cfg = world.config
    if not cfg.slot_recycling_enabled:
        # Legacy path: just deactivate, no bookkeeping
        world.k_alive[i] = False
        return

    if not world.k_alive[i]:
        return  # already dead — no-op

    world.k_alive[i] = False

    # Decrement ref counts of constituents
    start = int(world.k_comp_offset[i])
    end = int(world.k_comp_offset[i + 1])
    for j in range(start, end):
        c = int(world.k_comp_indices[j])
        if 0 <= c < world.k_count:
            world.k_ref_count[c] -= 1
            if world.k_ref_count[c] <= 0 and not world.k_alive[c]:
                if c not in world._free_slots_set:
                    world._free_slots.append(c)
                    world._free_slots_set.add(c)

    # Maybe i itself is now recyclable
    if world.k_ref_count[i] == 0:
        if i not in world._free_slots_set:
            world._free_slots.append(i)
            world._free_slots_set.add(i)
```

Note: the gate on `cfg.slot_recycling_enabled` means setting the flag to `False` reverts to the legacy "just kill, no bookkeeping" behaviour for regression diagnosis.

- [ ] **Step 4.4: Run tests, expect partial pass**

```bash
uv run pytest tests/test_amendment_AP_slot_recycling_correctness.py -v
```

Expected: AP4a and AP4b pass; AP3 fails (still needs Task 5's `allocate_node` change).

- [ ] **Step 4.5: Commit**

```bash
git add world/physics.py tests/test_amendment_AP_slot_recycling_correctness.py
git commit -m "feat(physics): _kill_node helper for slot recycling bookkeeping

Single source of truth for marking nodes dead. Decrements ref counts of
constituents and pushes newly-recyclable slots onto the free list. Gated
behind cfg.slot_recycling_enabled so the legacy path is preserved for
regression diagnosis."
```

---

## Task 5: Modify `allocate_node` to recycle slots

**Files:**
- Modify: `world/state.py` (replace `allocate_node`)

- [ ] **Step 5.1: Replace `allocate_node`**

Edit `world/state.py:allocate_node`. The new version:

```python
    def allocate_node(
        self, pos: np.ndarray, freq: float, pol: bool, level: int,
        constituents: np.ndarray, comp_kind: int,
    ) -> int:
        # Try to recycle a dead, unreferenced slot first
        if self.config.slot_recycling_enabled and self._free_slots:
            i = self._free_slots.pop()
            self._free_slots_set.discard(i)
            # Reset all per-slot state (note: k_ref_count[i] is already 0 by free-list invariant)
            self.k_pos[i] = 0
            self.k_vel[i] = 0
            self.k_freq[i] = 0
            self.k_pol[i] = False
            self.k_level[i] = 0
            self.k_birth[i] = 0
            self.k_alive[i] = False
            self.k_locked_this_tick[i] = False
            self.k_charge[i] = 0
            self.k_refractory_until[i] = 0
            self.k_strength[i] = 1.0
            # k_orientation, k_ref_count: zero from invariant
        else:
            i = self.k_count
            if i >= self.config.n_nodes_max:
                raise RuntimeError("Node capacity exhausted")
            self.k_count += 1

        # Populate the slot
        self.k_pos[i] = pos
        self.k_vel[i] = 0.0
        self.k_freq[i] = freq
        self.k_pol[i] = pol
        self.k_level[i] = level
        self.k_birth[i] = self.t
        self.k_alive[i] = True
        self.k_comp_kind[i] = comp_kind
        n_comp = len(constituents)
        start = self.k_comp_used
        end = start + n_comp
        if end > self.k_comp_indices.shape[0]:
            raise RuntimeError("Composition index capacity exhausted")
        self.k_comp_indices[start:end] = constituents
        self.k_comp_offset[i] = start
        self.k_comp_offset[i + 1] = end
        self.k_comp_used = end

        # Increment ref counts of constituents (slot recycling bookkeeping)
        if self.config.slot_recycling_enabled:
            for c in constituents:
                self.k_ref_count[int(c)] += 1

        return i
```

Also bump the comp-indices capacity from `K * 4` to `K * 16` so long-running runs don't fill it. In `World.__init__`, change:

```python
        comp_caps = K * 4
```

to:

```python
        comp_caps = K * 16  # Plan A.5: larger to accommodate slot recycling appending
```

- [ ] **Step 5.2: Run all slot-recycling tests, expect pass**

```bash
uv run pytest tests/test_amendment_AP_slot_recycling_correctness.py -v
uv run pytest -q
```

Expected: AP3, AP4a, AP4b pass. Full suite green.

- [ ] **Step 5.3: Commit**

```bash
git add world/state.py
git commit -m "feat(state): allocate_node reuses recycled slots before extending k_count

Pops from _free_slots when slot_recycling_enabled. Resets per-slot state
on reuse so the recycled slot is indistinguishable from a fresh allocation.
Increments ref counts of constituents to maintain the recycle invariant.
Bumps k_comp_indices capacity 4x→16x to handle long-running recycle workloads."
```

---

## Task 6: Refactor decay paths to use `_kill_node`

**Files:**
- Modify: `world/physics.py` (decay_unstable_nodes, decay_high_level_nodes, bind_nodes_upward parents-deactivation)

- [ ] **Step 6.1: Write the test (AP5)**

Create `tests/test_amendment_AP_slot_recycling_plateau.py`:

```python
"""Tests for k_count plateau under sustained input (AP5)."""
import numpy as np
import pytest
from world.config import WorldConfig
from world.state import World
from world.physics import tick


@pytest.mark.slow
def test_AP5_k_count_plateaus_under_sustained_growth():
    """1-min simulated run with the growth-amendment config; k_count must
    plateau at no more than 2× peak alive node count."""
    cfg = WorldConfig(
        n_initial_vibrations=80, n_vibrations_max=200, n_nodes_max=4096,
        box_size=(60.0, 60.0, 60.0),
        r_1=3.0, r_2=20.0,
        freq_ratio=0.08, freq_tolerance=0.025,
        pair_decay_time=5.0, triad_decay_time=30.0,
        lambda_gen=0.001, lambda_dec=0.0005,
        rng_seed=42,
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=8, r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.3, emit_speed=15.0,
        lambda_dec_mol=0.01,
        r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=True,
        slot_recycling_enabled=True,
    )
    w = World(cfg)
    burst_pos = np.array([30.0, 30.0, 30.0])

    def _inject_burst():
        free_idx = np.where(~w.s_alive)[0][:5]
        for i in free_idx:
            w.s_pos[i] = burst_pos + w.rng.uniform(-0.5, 0.5, 3)
            w.s_vel[i] = 0
            w.s_freq[i] = 10000.0 + w.rng.uniform(-100, 100)
            w.s_pol[i] = bool(w.rng.random() < 0.5)
            w.s_alive[i] = True
        if len(free_idx):
            w.n_alive = max(w.n_alive, int(free_idx.max()) + 1)

    dt = cfg.dt
    burst_step = max(1, int(0.5 / dt))
    n_ticks = int(60.0 / dt)
    peak_alive = 0
    final_k_count = 0
    for k in range(n_ticks):
        if (k + 1) % burst_step == 0:
            _inject_burst()
        tick(w, dt)
        alive_now = int(w.k_alive[:w.k_count].sum())
        peak_alive = max(peak_alive, alive_now)
    final_k_count = w.k_count

    print(f"AP5: peak alive nodes = {peak_alive}, final k_count = {final_k_count}, "
          f"ratio = {final_k_count / max(peak_alive, 1):.2f}")
    assert final_k_count <= 2 * max(peak_alive, 1), (
        f"AP5: k_count {final_k_count} exceeds 2× peak alive {peak_alive} "
        "— slot recycling not effective"
    )
```

- [ ] **Step 6.2: Run AP5, expect failure**

```bash
uv run pytest tests/test_amendment_AP_slot_recycling_plateau.py -v -s --override-ini="addopts="
```

Expected: FAIL — current decay paths don't push to the free list, so k_count grows monotonically.

- [ ] **Step 6.3: Refactor `decay_unstable_nodes`**

In `world/physics.py`, find every line that sets `world.k_alive[i] = False` inside `decay_unstable_nodes` and replace with `_kill_node(world, i)`.

For example, if the decay path looks like:

```python
        if rolls[idx] < p:
            world.k_alive[i] = False
            n_decayed += 1
```

Change to:

```python
        if rolls[idx] < p:
            _kill_node(world, i)
            n_decayed += 1
```

- [ ] **Step 6.4: Refactor `decay_high_level_nodes` similarly**

Find the lines `world.k_alive[i] = False; world.k_strength[i] = 1.0` in `decay_high_level_nodes` and replace with:

```python
            _kill_node(world, i)
            # k_strength reset still happens in allocate_node when this slot is reused
```

The strength reset is now redundant in the decay path because `allocate_node` resets it on reuse. Remove the `world.k_strength[i] = 1.0` line from the decay path; it's no longer needed.

- [ ] **Step 6.5: Refactor `bind_nodes_upward` parent-deactivation**

In `bind_nodes_upward`, when an upgrade fires, the two parents are deactivated:

```python
            world.k_alive[i] = False
            world.k_alive[j] = False
```

But because the new higher-level node's `constituents` includes both `i` and `j`, the ref counts of `i` and `j` are at least 1 (incremented by `allocate_node` for the new node). So deactivating them does NOT immediately free the slots — they'll be freed when the higher-level node decays. This is correct.

The change: replace `world.k_alive[i] = False` with `_kill_node(world, i)` (and same for `j`). `_kill_node` handles the ref-count check and only pushes to free list if ref count is zero — which it isn't here.

- [ ] **Step 6.6: Run AP5, expect pass + suite green**

```bash
uv run pytest tests/test_amendment_AP_slot_recycling_plateau.py -v -s --override-ini="addopts="
uv run pytest -q
```

Expected: AP5 passes (k_count plateaus). Full non-slow suite green.

- [ ] **Step 6.7: Commit**

```bash
git add world/physics.py tests/test_amendment_AP_slot_recycling_plateau.py
git commit -m "refactor(physics): decay paths funnel through _kill_node

decay_unstable_nodes, decay_high_level_nodes, and the parent-deactivation
inside bind_nodes_upward all now use _kill_node, which decrements ref
counts of constituents and pushes newly-recyclable slots onto the free
list. Result: k_count plateaus at ~2× peak alive population (AP5)."
```

---

## Task 7: Behavioural equivalence under flag toggle

**Files:**
- Test: `tests/test_amendment_AP_behavioural_equivalence.py` (create)

This test verifies that `slot_recycling_enabled=True` and `slot_recycling_enabled=False` produce identical observable behaviour (test outcomes, observation counts) over a sample run. Same for `numba_jit_enabled` once Tasks 8-13 land.

- [ ] **Step 7.1: Write the test (AP1, AP2)**

Create `tests/test_amendment_AP_behavioural_equivalence.py`:

```python
"""Plan A.5 behavioural equivalence tests (AP1, AP2)."""
import numpy as np
import pytest
from dataclasses import replace
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def _run_short(slot_recycling_enabled: bool, numba_jit_enabled: bool,
               rng_seed: int = 42, n_ticks: int = 600):
    """Run a short sim with given flags; return (k_count, n_alive_nodes,
    n_alive_vibrations, total_firings, mean_position) summary."""
    cfg = WorldConfig(
        n_initial_vibrations=80, n_vibrations_max=200, n_nodes_max=4096,
        box_size=(60.0, 60.0, 60.0),
        r_1=3.0, r_2=20.0,
        freq_ratio=0.08, freq_tolerance=0.025,
        pair_decay_time=5.0, triad_decay_time=30.0,
        lambda_gen=0.001, lambda_dec=0.0005,
        rng_seed=rng_seed,
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=8, r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.3, emit_speed=15.0,
        lambda_dec_mol=0.01, r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5), mol_fusion_enabled=True,
        slot_recycling_enabled=slot_recycling_enabled,
        numba_jit_enabled=numba_jit_enabled,
    )
    w = World(cfg)
    dt = cfg.dt
    for k in range(n_ticks):
        tick(w, dt)
    return {
        "k_count": w.k_count,
        "n_alive_nodes": int(w.k_alive[:w.k_count].sum()),
        "n_alive_vibrations": int(w.s_alive.sum()),
        "n_firings": len(w.firing_events),
    }


def test_AP1_slot_recycling_preserves_observable_behaviour():
    """With same RNG seed, slot_recycling_enabled=True and =False must
    produce identical observable counts."""
    a = _run_short(slot_recycling_enabled=True, numba_jit_enabled=False)
    b = _run_short(slot_recycling_enabled=False, numba_jit_enabled=False)
    assert a["n_alive_nodes"] == b["n_alive_nodes"], (
        f"alive nodes differ: recycle={a['n_alive_nodes']}, no-recycle={b['n_alive_nodes']}"
    )
    assert a["n_alive_vibrations"] == b["n_alive_vibrations"]
    assert a["n_firings"] == b["n_firings"]
    # k_count differs (recycling keeps it lower) — not asserted equal


def test_AP2_jit_preserves_observable_behaviour():
    """With same RNG seed, numba_jit_enabled=True and =False must produce
    identical observable counts."""
    a = _run_short(slot_recycling_enabled=True, numba_jit_enabled=True)
    b = _run_short(slot_recycling_enabled=True, numba_jit_enabled=False)
    assert a["n_alive_nodes"] == b["n_alive_nodes"]
    assert a["n_alive_vibrations"] == b["n_alive_vibrations"]
    assert a["n_firings"] == b["n_firings"]
    assert a["k_count"] == b["k_count"]
```

- [ ] **Step 7.2: Run AP1, expect pass**

```bash
uv run pytest tests/test_amendment_AP_behavioural_equivalence.py::test_AP1_slot_recycling_preserves_observable_behaviour -v
```

Expected: PASS (slot recycling is now wired through `_kill_node` and `allocate_node`).

- [ ] **Step 7.3: Skip AP2 for now**

AP2 (JIT equivalence) will fail until Tasks 8-13 land the JIT migrations. Mark it skip for now:

```python
@pytest.mark.skip(reason="awaiting JIT migration (Tasks 8-13)")
def test_AP2_jit_preserves_observable_behaviour():
    ...
```

(remove the `@pytest.mark.skip` after Task 13 lands.)

- [ ] **Step 7.4: Commit**

```bash
git add tests/test_amendment_AP_behavioural_equivalence.py
git commit -m "test(perf): AP1 — slot recycling preserves observable counts

Compares same-seed runs with slot_recycling_enabled=True vs =False;
counts of alive nodes, alive vibrations, and firings must match.
AP2 (JIT equivalence) is skipped until Tasks 8-13 land the JIT cores."
```

---

## Task 8: Convert `_UPGRADE_TARGET` dict → numpy arrays

**Files:**
- Modify: `world/physics.py` (after the existing dict definitions)

This is a small standalone change in preparation for the JIT migrations.

- [ ] **Step 8.1: Add the array versions**

In `world/physics.py`, after the existing `_UPGRADE_TARGET` and `_UPGRADE_TARGET_FUSION` dict definitions, add:

```python
# Plan A.5 — numpy-array versions for Numba JIT lookup. Numba can't
# index Python dicts efficiently; small dense arrays are the canonical
# pattern. Built once at module import.
_MAX_LEVEL = 12
_UPGRADE_TARGET_ARRAY = np.full((_MAX_LEVEL, _MAX_LEVEL), -1, dtype=np.int8)
for (li, lj), target in _UPGRADE_TARGET.items():
    _UPGRADE_TARGET_ARRAY[li, lj] = target

_UPGRADE_TARGET_FUSION_ARRAY = np.full((_MAX_LEVEL, _MAX_LEVEL), -1, dtype=np.int8)
for (li, lj), target in _UPGRADE_TARGET_FUSION.items():
    _UPGRADE_TARGET_FUSION_ARRAY[li, lj] = target
```

The dicts remain for the Python path; the arrays are used by the JIT path.

- [ ] **Step 8.2: Run full suite, must stay green**

```bash
uv run pytest -q
```

- [ ] **Step 8.3: Commit**

```bash
git add world/physics.py
git commit -m "refactor(physics): mirror _UPGRADE_TARGET dicts as numpy arrays

Preparation for Numba JIT: small dense int8 arrays indexable by (li, lj)
that Numba can lookup efficiently. Python dict versions kept for the
non-JIT path."
```

---

## Task 9: JIT `decay_unstable_nodes`

**Files:**
- Modify: `world/physics.py` (split into Python + @njit)
- Test: `tests/test_amendment_AP_jit_correctness.py` (create)

- [ ] **Step 9.1: Write the test (AP7)**

Create `tests/test_amendment_AP_jit_correctness.py`:

```python
"""Plan A.5 JIT correctness tests (AP7-AP11)."""
import numpy as np
import pytest
from dataclasses import replace
from world.config import WorldConfig
from world.state import World
from world.physics import decay_unstable_nodes, decay_high_level_nodes, move_nodes
from world.physics import apply_scale_repulsion, bind_nodes_upward


def _build_test_world(jit: bool, rng_seed: int = 42):
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=4, n_nodes_max=128,
        box_size=(100.0, 100.0, 100.0), rng_seed=rng_seed,
        slot_recycling_enabled=False,  # isolate JIT effects from recycling
        numba_jit_enabled=jit,
    )
    return World(cfg)


def _populate_nodes(w, n=50, level=2):
    for i in range(n):
        w.k_pos[i] = w.rng.uniform(0, 100, size=3)
        w.k_vel[i] = w.rng.uniform(-1, 1, size=3)
        w.k_freq[i] = 1000.0 + i
        w.k_pol[i] = bool(i % 2)
        w.k_level[i] = level
        w.k_alive[i] = True
        w.k_birth[i] = 0.0
    w.k_count = n


def test_AP7_decay_unstable_nodes_jit_matches_python():
    """JIT and Python paths produce identical k_alive after one decay tick."""
    w_py = _build_test_world(jit=False, rng_seed=42)
    _populate_nodes(w_py, n=50, level=2)
    decay_unstable_nodes(w_py, dt=0.01)

    w_jit = _build_test_world(jit=True, rng_seed=42)
    _populate_nodes(w_jit, n=50, level=2)
    decay_unstable_nodes(w_jit, dt=0.01)

    assert np.array_equal(w_py.k_alive, w_jit.k_alive)
```

- [ ] **Step 9.2: Run test, expect failure**

```bash
uv run pytest tests/test_amendment_AP_jit_correctness.py::test_AP7_decay_unstable_nodes_jit_matches_python -v
```

Expected: depends on current state — if `decay_unstable_nodes` doesn't yet check the JIT flag, the test passes vacuously. The intent is that we want EQUAL output, which is satisfied if both paths run the same code today. After we split into Python and JIT cores in Step 9.3, this test verifies they stay equivalent.

- [ ] **Step 9.3: Split into Python + @njit**

Read the current `decay_unstable_nodes` in `world/physics.py`. Identify the inner loop. Extract it into a `@njit` function that takes plain numpy arrays. The Python wrapper handles RNG generation, free-list bookkeeping, and dispatches to JIT or Python based on the flag.

```python
from numba import njit


@njit(cache=True)
def _decay_unstable_njit(k_alive: np.ndarray, k_level: np.ndarray, k_birth: np.ndarray,
                         rolls: np.ndarray, t: float, pair_decay_time: float,
                         triad_decay_time: float, K: int) -> np.ndarray:
    """Returns a boolean array of length K marking which slots should be killed.

    The caller is responsible for calling _kill_node on each True slot.
    """
    decayed = np.zeros(K, dtype=np.bool_)
    for i in range(K):
        if not k_alive[i]:
            continue
        level = k_level[i]
        if level == 2:
            tau = pair_decay_time
        elif level == 3:
            tau = triad_decay_time
        else:
            continue
        age = t - k_birth[i]
        if age <= 0:
            continue
        # Exponential decay: probability of decay this dt = 1 - exp(-dt/tau)
        # Approximation for small dt: dt / tau
        # Or use the actual exponential — see existing implementation
        p = 1.0 - np.exp(-age / tau)  # cumulative decay probability
        if rolls[i] < p:
            decayed[i] = True
    return decayed


def decay_unstable_nodes(world, dt: float) -> int:
    cfg = world.config
    K = world.k_count
    if K == 0:
        return 0

    if cfg.numba_jit_enabled:
        rolls = world.rng.random(K)
        decayed = _decay_unstable_njit(
            world.k_alive[:K], world.k_level[:K], world.k_birth[:K],
            rolls, world.t, cfg.pair_decay_time, cfg.triad_decay_time, K,
        )
        n_decayed = 0
        for i in range(K):
            if decayed[i]:
                _kill_node(world, i)
                n_decayed += 1
        return n_decayed
    else:
        # Legacy Python path — keep for regression diagnosis
        # (... copy the previous implementation here, replacing
        # `world.k_alive[i] = False` with `_kill_node(world, i)`)
        ...
```

**Important:** the exact decay formula must match the previous Python implementation. If the previous code used `dt / tau` (linear) instead of `1 - exp(-dt/tau)` (exponential), match that. The JIT version is a literal translation.

Read the existing `decay_unstable_nodes` carefully and translate one-for-one.

- [ ] **Step 9.4: Run test, expect pass + suite green**

```bash
uv run pytest tests/test_amendment_AP_jit_correctness.py::test_AP7_decay_unstable_nodes_jit_matches_python -v
uv run pytest -q
```

- [ ] **Step 9.5: Commit**

```bash
git add world/physics.py tests/test_amendment_AP_jit_correctness.py
git commit -m "feat(physics): JIT core for decay_unstable_nodes

Inner loop moves to @njit. Python path is preserved behind
numba_jit_enabled=False for regression diagnosis. AP7 verifies the two
paths produce identical k_alive arrays from the same RNG rolls."
```

---

## Task 10: JIT `decay_high_level_nodes`

Same shape as Task 9 but for `decay_high_level_nodes` (Plan A's strength-modulated decay).

- [ ] **Step 10.1: Add AP8 test**

Append to `tests/test_amendment_AP_jit_correctness.py`:

```python
def test_AP8_decay_high_level_nodes_jit_matches_python():
    """JIT and Python paths produce identical k_alive after one decay tick
    on level-5+ molecules."""
    w_py = _build_test_world(jit=False, rng_seed=42)
    _populate_nodes(w_py, n=50, level=5)
    w_py.config = replace(w_py.config, lambda_dec_mol=0.5)
    w_py.k_strength[:50] = w_py.rng.uniform(1.0, 50.0, size=50)
    decay_high_level_nodes(w_py, dt=0.01)

    w_jit = _build_test_world(jit=True, rng_seed=42)
    _populate_nodes(w_jit, n=50, level=5)
    w_jit.config = replace(w_jit.config, lambda_dec_mol=0.5)
    w_jit.k_strength[:50] = w_jit.rng.uniform(1.0, 50.0, size=50)
    decay_high_level_nodes(w_jit, dt=0.01)

    assert np.array_equal(w_py.k_alive, w_jit.k_alive)
```

- [ ] **Step 10.2: Implement the JIT split**

Add `_decay_high_level_njit` core and rewrite `decay_high_level_nodes` to dispatch on `cfg.numba_jit_enabled`. Same pattern as Task 9.

- [ ] **Step 10.3: Test + commit**

```bash
uv run pytest tests/test_amendment_AP_jit_correctness.py::test_AP8_decay_high_level_nodes_jit_matches_python -v
uv run pytest -q

git add world/physics.py tests/test_amendment_AP_jit_correctness.py
git commit -m "feat(physics): JIT core for decay_high_level_nodes

Inner loop moves to @njit, with strength floor and inverse-strength
decay rate computed in the JIT core. Python path preserved behind
numba_jit_enabled=False for diagnosis. AP8 confirms equivalence."
```

---

## Task 11: JIT `move_nodes`

- [ ] **Step 11.1: Add AP9 test**

```python
def test_AP9_move_nodes_jit_matches_python():
    """JIT and Python paths produce identical k_pos after one move tick."""
    w_py = _build_test_world(jit=False, rng_seed=42)
    _populate_nodes(w_py, n=100, level=4)
    move_nodes(w_py, dt=0.01)

    w_jit = _build_test_world(jit=True, rng_seed=42)
    _populate_nodes(w_jit, n=100, level=4)
    move_nodes(w_jit, dt=0.01)

    assert np.allclose(w_py.k_pos, w_jit.k_pos, rtol=1e-12)
```

- [ ] **Step 11.2: Split + dispatch**

Same pattern. `_move_nodes_njit` core takes `k_pos`, `k_vel`, `k_alive`, `box`, `dt`, `K` and modifies `k_pos` in place with periodic wrap. No RNG.

- [ ] **Step 11.3: Test + commit**

---

## Task 12: JIT `apply_scale_repulsion`

- [ ] **Step 12.1: Add AP10 test**

```python
def test_AP10_apply_scale_repulsion_jit_matches_python():
    w_py = _build_test_world(jit=False, rng_seed=42)
    _populate_nodes(w_py, n=80, level=4)
    apply_scale_repulsion(w_py, dt=0.01)

    w_jit = _build_test_world(jit=True, rng_seed=42)
    _populate_nodes(w_jit, n=80, level=4)
    apply_scale_repulsion(w_jit, dt=0.01)

    assert np.allclose(w_py.k_vel, w_jit.k_vel, rtol=1e-12)
```

- [ ] **Step 12.2: Split + dispatch**

`_apply_scale_repulsion_njit` core. Pure numerical, no RNG.

- [ ] **Step 12.3: Test + commit**

---

## Task 13: JIT `bind_nodes_upward`

The most complex JIT migration. Spatial-hash query stays in Python (it's already JIT'd internally and harder to compose). The pair-iteration + binding logic moves to JIT. The upgrade-target lookup uses the `_UPGRADE_TARGET_ARRAY` from Task 8.

- [ ] **Step 13.1: Add AP11 test**

```python
def test_AP11_bind_nodes_upward_jit_matches_python():
    """JIT and Python paths produce identical post-binding state."""
    w_py = _build_test_world(jit=False, rng_seed=42)
    # Place nodes that will bind: pairs of level 1 + level 2 with matching freq ratio
    for i in range(8):
        w_py.k_pos[2*i] = [10 + 5*i, 50, 50]
        w_py.k_pos[2*i+1] = [10 + 5*i + 1, 50, 50]  # within r_2
        w_py.k_freq[2*i] = 1000.0
        w_py.k_freq[2*i+1] = 1080.0  # ratio = 0.08
        w_py.k_pol[2*i] = True
        w_py.k_pol[2*i+1] = False
        w_py.k_level[2*i] = 1
        w_py.k_level[2*i+1] = 2
        w_py.k_alive[2*i] = True
        w_py.k_alive[2*i+1] = True
    w_py.k_count = 16
    bind_nodes_upward(w_py)

    w_jit = _build_test_world(jit=True, rng_seed=42)
    # Same setup
    for i in range(8):
        w_jit.k_pos[2*i] = [10 + 5*i, 50, 50]
        w_jit.k_pos[2*i+1] = [10 + 5*i + 1, 50, 50]
        w_jit.k_freq[2*i] = 1000.0
        w_jit.k_freq[2*i+1] = 1080.0
        w_jit.k_pol[2*i] = True
        w_jit.k_pol[2*i+1] = False
        w_jit.k_level[2*i] = 1
        w_jit.k_level[2*i+1] = 2
        w_jit.k_alive[2*i] = True
        w_jit.k_alive[2*i+1] = True
    w_jit.k_count = 16
    bind_nodes_upward(w_jit)

    assert w_py.k_count == w_jit.k_count
    assert np.array_equal(w_py.k_alive[:w_py.k_count], w_jit.k_alive[:w_jit.k_count])
    assert np.array_equal(w_py.k_level[:w_py.k_count], w_jit.k_level[:w_jit.k_count])
```

- [ ] **Step 13.2: Split + dispatch**

The JIT core takes `_UPGRADE_TARGET_ARRAY` and `_UPGRADE_TARGET_FUSION_ARRAY` as inputs. RNG rolls (for new-node polarity) are pre-generated in Python.

- [ ] **Step 13.3: Test + commit**

```bash
git add world/physics.py tests/test_amendment_AP_jit_correctness.py
git commit -m "feat(physics): JIT core for bind_nodes_upward

Inner pair-iteration + upgrade-target lookup moves to @njit. Spatial
hash query stays in Python. RNG rolls pre-generated. AP11 confirms
JIT and Python paths produce identical post-binding state."
```

- [ ] **Step 13.4: Unskip AP2 in `tests/test_amendment_AP_behavioural_equivalence.py`**

Remove the `@pytest.mark.skip` decorator. Run AP2 — should now pass.

```bash
uv run pytest tests/test_amendment_AP_behavioural_equivalence.py::test_AP2_jit_preserves_observable_behaviour -v
```

Expected: PASS. Commit:

```bash
git add tests/test_amendment_AP_behavioural_equivalence.py
git commit -m "test(perf): unskip AP2 — JIT preserves observable behaviour

All five hot loops are now JIT'd; full-tick equivalence holds across
the numba_jit_enabled flag toggle."
```

---

## Task 14: Performance bound test (AP12)

**Files:**
- Test: `tests/test_amendment_AP_performance.py` (create)

- [ ] **Step 14.1: Write AP12**

```python
"""Plan A.5 performance tests (AP12, AP13)."""
import time
import numpy as np
import pytest
from dataclasses import replace
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def _growth_config(rng_seed: int = 42) -> WorldConfig:
    return WorldConfig(
        n_initial_vibrations=80, n_vibrations_max=200, n_nodes_max=4096,
        box_size=(60.0, 60.0, 60.0),
        r_1=3.0, r_2=20.0,
        freq_ratio=0.08, freq_tolerance=0.025,
        pair_decay_time=5.0, triad_decay_time=30.0,
        lambda_gen=0.001, lambda_dec=0.0005,
        rng_seed=rng_seed,
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=8, r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.3, emit_speed=15.0,
        lambda_dec_mol=0.01, r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5), mol_fusion_enabled=True,
        slot_recycling_enabled=True, numba_jit_enabled=True,
    )


@pytest.mark.slow
def test_AP12_per_tick_wall_cost_bounded():
    """5-min sim with growth-amendment config; wall-clock per simulated
    second stays within 5x of the minimum across the run.

    Pre-A.5: ratio was >100x as k_count grew. Post-A.5 with slot recycling
    and JIT, the ratio should be ~2-5x.
    """
    w = World(_growth_config())
    burst_pos = np.array([30.0, 30.0, 30.0])
    dt = w.config.dt

    def _inject_burst():
        free_idx = np.where(~w.s_alive)[0][:5]
        for i in free_idx:
            w.s_pos[i] = burst_pos + w.rng.uniform(-0.5, 0.5, 3)
            w.s_vel[i] = 0
            w.s_freq[i] = 10000.0 + w.rng.uniform(-100, 100)
            w.s_pol[i] = bool(w.rng.random() < 0.5)
            w.s_alive[i] = True
        if len(free_idx):
            w.n_alive = max(w.n_alive, int(free_idx.max()) + 1)

    # Warm up the JIT functions (one tick to trigger compilation)
    tick(w, dt)

    burst_step = max(1, int(0.5 / dt))
    n_seconds = 60 * 5  # 5 sim-min
    wall_per_sim_sec = []
    for sim_sec in range(n_seconds):
        t_start = time.time()
        for k in range(int(1.0 / dt)):
            if (k + 1) % burst_step == 0:
                _inject_burst()
            tick(w, dt)
        wall_per_sim_sec.append(time.time() - t_start)

    min_wall = min(wall_per_sim_sec)
    max_wall = max(wall_per_sim_sec)
    print(f"AP12: wall-clock per sim-sec — min={min_wall:.3f}s, max={max_wall:.3f}s, "
          f"ratio={max_wall / max(min_wall, 1e-6):.1f}x")
    assert max_wall <= 5.0 * min_wall, (
        f"AP12: wall ratio {max_wall / min_wall:.1f}x exceeds bound 5x"
    )
```

- [ ] **Step 14.2: Run AP12, expect pass**

```bash
uv run pytest tests/test_amendment_AP_performance.py::test_AP12_per_tick_wall_cost_bounded -v -s --override-ini="addopts="
```

- [ ] **Step 14.3: Commit**

```bash
git add tests/test_amendment_AP_performance.py
git commit -m "test(perf): AP12 — per-tick wall-cost bounded under sustained run

5-min sim with the growth-amendment config; wall-clock per simulated
second stays within 5x of the minimum. Pre-A.5 the ratio was >100x;
post-A.5 with slot recycling and JIT, it should be 2-5x."
```

---

## Task 15: F1 at full 60 sim-min (AP13, headline)

- [ ] **Step 15.1: Write AP13**

Append to `tests/test_amendment_AP_performance.py`:

```python
@pytest.mark.slow
def test_AP13_F1_at_full_60_minutes_feasible():
    """Re-run Plan A's F1 acceptance test at the original 60-sim-minute
    duration. Wall-clock target: ≤ 30 minutes on developer hardware.

    Pre-A.5: projected 5-100+ hours.
    """
    w = World(_growth_config())
    burst_pos = np.array([30.0, 30.0, 30.0])
    dt = w.config.dt

    def _inject_burst():
        free_idx = np.where(~w.s_alive)[0][:5]
        for i in free_idx:
            w.s_pos[i] = burst_pos + w.rng.uniform(-0.5, 0.5, 3)
            w.s_vel[i] = 0
            w.s_freq[i] = 10000.0 + w.rng.uniform(-100, 100)
            w.s_pol[i] = bool(w.rng.random() < 0.5)
            w.s_alive[i] = True
        if len(free_idx):
            w.n_alive = max(w.n_alive, int(free_idx.max()) + 1)

    burst_step = max(1, int(0.5 / dt))
    samples = []
    n_minutes = 60
    samples_per_minute = 12
    t_start = time.time()
    for _ in range(n_minutes * samples_per_minute):
        for k in range(int(5.0 / dt)):
            if (k + 1) % burst_step == 0:
                _inject_burst()
            tick(w, dt)
        samples.append(int(w.s_alive.sum()))
    wall_seconds = time.time() - t_start

    mean_count = float(np.mean(samples))
    in_band = sum(1 for s in samples if 0.25 * mean_count <= s <= 2.0 * mean_count)
    pct_in_band = in_band / len(samples)

    print(f"AP13: 60-min F1 wall={wall_seconds:.0f}s, mean={mean_count:.0f}, "
          f"in-band={pct_in_band*100:.0f}%")
    assert pct_in_band >= 0.8
    assert wall_seconds <= 30 * 60, f"AP13: wall {wall_seconds/60:.1f} min > 30-min target"
```

- [ ] **Step 15.2: Run AP13, expect pass**

This will run for up to 30 wall-minutes. Don't terminate early.

- [ ] **Step 15.3: Commit**

```bash
git add tests/test_amendment_AP_performance.py
git commit -m "test(perf): AP13 — F1 at full 60 sim-min wall ≤ 30 min

Headline acceptance test for Plan A.5. Validates the foundation spec's
original target duration is now feasible. Combined with slot recycling
and JIT, the substrate runs at sustainable per-tick cost over many
simulated hours."
```

---

## Task 16: Mark Plan A.5 amendment in dashboard DB

- [ ] **Step 16.1: Insert + mark**

```bash
docker exec vibrasim-postgres psql -U vibrasim -d vibrasim -c "
INSERT INTO amendments (number, title, spec_section, description, motivation, status)
VALUES ('PERF-A5',
        'Substrate performance — slot recycling + Numba JIT',
        '§ baby-brain-foundation-plan-A5-substrate-performance-design.md',
        'Reference-counted slot recycling in World.allocate_node + @njit cores for the five hot per-tick loops. Breaks the quadratic sim-time→wall-time dependence; k_count plateaus at steady-state population.',
        'Discovered during Plan A Task 9 when 60-sim-minute F1 projected at multi-hour wall-clock. Required to make Plan B-G integration tests feasible.',
        'proposed')
ON CONFLICT (number) DO NOTHING;

UPDATE amendments
SET status = 'implemented',
    impl_commit = '$(git rev-parse main)',
    decided_at = NOW()
WHERE number = 'PERF-A5';
"
```

(Run after Plan A.5 is merged to main and the SHA is known.)

- [ ] **Step 16.2: Verify**

Open http://localhost:8502/Amendments; confirm PERF-A5 shows `implemented` with the commit SHA.

---

## Plan A.5 complete

After Task 15, the substrate has slot recycling and Numba-JIT'd hot loops. Wall-clock per simulated second stays roughly constant (no longer linear in `k_count`); the foundation spec's full-duration tests become feasible.

**Verify final state:**

```bash
uv run pytest -q                    # full suite green (≥190 tests)
uv run pytest -m slow -v            # AP5, AP12, AP13 pass
git log --oneline feat/baby-brain-plan-A5  # ~16 commits
```

**Next plans:**

- **Plan B** — STDP + bridge orientation. Now feasible at full P3 scale.
- **Plan C** — Audio I/O.
- **Plan D** — Video I/O.

---

## Mid-flight discoveries

### k_comp_end data-corruption fix (commits 11fdf0a, a3330bb)

While AP12 was running its sustained-load stress test, slot recycling
exposed a latent bug in `World.allocate_node`: when recycling slot `i`,
the code was clobbering `k_comp_offset[i+1]` — the start-pointer of
the *next* slot, not slot `i`'s end-pointer. With the monotonic
allocator that preceded recycling this was harmless because slot
i+1 was always free. With recycling, slot i+1 was often a live node
whose composition span got corrupted.

Fix: split the start-pointer (`k_comp_offset`) and end-pointer
(`k_comp_end`) into separate arrays. Updated four read sites in
`physics.py` (`_kill_node`, the two decay paths, `ambient_regeneration`)
and `tools/classify_molecules.py`. Added backward-compat in
`snapshot.py` (commit a3330bb): legacy snapshots without `k_comp_end`
reconstruct it from `k_comp_offset[1:K+1]` on load.

This kind of bug is exactly what AP12-type sustained-load tests
exist to catch. The fix is invariant-clean — there is now exactly one
writer of each pointer per slot.
- Subsequent: E (orchestrator + reward), F (checkpoint extension), G (M4 demo).

# Plan A — Substrate Growth Amendments Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the substrate capable of activity-driven growth with use-dependent decay over many simulated minutes — landing amendments R1 (recycling regen), R2 (strength-modulated decay), PHASE3-R1 (molecule fusion), tuned PHASE4 emissions, and the `k_strength` field.

**Architecture:** All additions are guarded by `neuron_dynamics_enabled` (already in config from prior PHASE4-R1/R2/R3 work). Existing tests must remain green. New behaviour is unit-tested in isolation, then validated end-to-end via four integration tests (F1–F4 from the foundation spec §6.1).

**Tech Stack:** Python 3.13, NumPy, Numba @njit (existing), pytest. No new dependencies.

**Spec reference:** `docs/superpowers/specs/2026-05-06-baby-brain-foundation-design.md` §3.1–§3.4 + §6.1 (F1–F4, partial P1).

**Out of scope for this plan** (covered by later plans): STDP and bridge-orientation vectors (Plan B), audio/video I/O (Plans C/D), reward channel (Plan E), brain checkpoint (Plan F), end-to-end demos (Plan G).

---

## File map

| Path | Action | Responsibility |
|---|---|---|
| `world/config.py` | Modify | Add `lambda_dec_mol`, `r_strengthen`, `emit_band_ratios`, `mol_fusion_enabled` fields |
| `world/state.py` | Modify | Add `k_strength: np.ndarray` field |
| `world/snapshot.py` | Modify | Persist + restore `k_strength` |
| `world/physics.py` | Modify | Modify `_emit_vibrations` (frequency-band fan); add `decay_high_level_nodes`; modify `_UPGRADE_TARGET` (PHASE3-R1); modify `ambient_regeneration` (recycling); add strengthening pass to `neuron_dynamics`; wire new step into `tick` |
| `tests/test_amendment_R1_recycling_regen.py` | Create | Unit tests for R1 |
| `tests/test_amendment_R2_strength_decay.py` | Create | Unit tests for R2 (decay and strengthening) |
| `tests/test_amendment_PHASE3R1_molecule_fusion.py` | Create | Unit tests for molecule + molecule binding |
| `tests/test_tuned_emissions.py` | Create | Unit tests for the frequency-band emission fan |
| `tests/test_substrate_growth_e2e.py` | Create | F1–F4 integration tests |

---

## Task 1: Add config fields for substrate growth amendments

**Files:**
- Modify: `world/config.py:43-58`
- Test: existing `tests/test_config.py` (new test added at end)

- [ ] **Step 1.1: Write the failing test**

Append to `tests/test_config.py`:

```python
def test_growth_amendment_fields_have_safe_defaults():
    """Plan A new fields must default off so legacy configs are unaffected."""
    cfg = WorldConfig()
    assert cfg.lambda_dec_mol == 0.001
    assert cfg.r_strengthen == 5.0
    assert cfg.emit_band_ratios == (0.08, 1.0, 12.5)  # freq_ratio, 1, 1/freq_ratio
    assert cfg.mol_fusion_enabled is False
```

- [ ] **Step 1.2: Run test, expect failure**

```bash
uv run pytest tests/test_config.py::test_growth_amendment_fields_have_safe_defaults -v
```

Expected: FAIL with `AttributeError: 'WorldConfig' object has no attribute 'lambda_dec_mol'`.

- [ ] **Step 1.3: Add the new fields to `WorldConfig`**

Edit `world/config.py` — insert these fields right after the existing `emit_freq` field at the end of the dataclass body (around line 58):

```python
    # Plan A — substrate growth amendments
    lambda_dec_mol: float = 0.001         # baseline decay rate for level-5+ molecules
    r_strengthen: float = 5.0             # radius around firings for level-5+ strengthening
    emit_band_ratios: tuple[float, float, float] = (0.08, 1.0, 12.5)  # PHASE4 emission band multipliers
    mol_fusion_enabled: bool = False      # PHASE3-R1: allow molecule + molecule binding
```

- [ ] **Step 1.4: Run test, expect pass**

```bash
uv run pytest tests/test_config.py::test_growth_amendment_fields_have_safe_defaults -v
```

Expected: PASS. Run the full config test file: `uv run pytest tests/test_config.py -q` — all 7+ tests pass.

- [ ] **Step 1.5: Commit**

```bash
git add world/config.py tests/test_config.py
git commit -m "feat(config): add substrate-growth-amendment fields to WorldConfig

Plan A new fields (lambda_dec_mol, r_strengthen, emit_band_ratios,
mol_fusion_enabled) default off / safe so legacy configs behave as before."
```

---

## Task 2: Add `k_strength` field to World state

**Files:**
- Modify: `world/state.py:30-50`
- Test: `tests/test_state.py` (new test added at end)

- [ ] **Step 2.1: Write the failing test**

Append to `tests/test_state.py`:

```python
def test_k_strength_field_initialised_to_one():
    """k_strength must default to 1.0 for every node slot — birth strength."""
    cfg = WorldConfig(n_initial_vibrations=0, n_nodes_max=16)
    w = World(cfg)
    assert w.k_strength.shape == (16,)
    assert w.k_strength.dtype == np.float64
    # Every slot starts with strength 1.0
    assert (w.k_strength == 1.0).all()
```

- [ ] **Step 2.2: Run test, expect failure**

```bash
uv run pytest tests/test_state.py::test_k_strength_field_initialised_to_one -v
```

Expected: FAIL — `AttributeError: 'World' object has no attribute 'k_strength'`.

- [ ] **Step 2.3: Add the field to `World.__init__`**

Edit `world/state.py` — after the existing `self.k_refractory_until = np.zeros(K, dtype=np.float64)` line:

```python
        # Plan A — per-node strength field (R2 strength-modulated decay).
        # Default 1.0 so newly-allocated nodes are not immediately decayed away.
        self.k_strength = np.ones(K, dtype=np.float64)
```

- [ ] **Step 2.4: Run test, expect pass**

```bash
uv run pytest tests/test_state.py -q
```

Expected: all tests pass (existing 11 + new 1).

- [ ] **Step 2.5: Commit**

```bash
git add world/state.py tests/test_state.py
git commit -m "feat(state): add k_strength field, initialised to 1.0 per node slot

R2 amendment: per-node strength field needed for strength-modulated decay
and use-dependent persistence (long-term memory)."
```

---

## Task 3: Persist `k_strength` in snapshots

**Files:**
- Modify: `world/snapshot.py:13-58`
- Test: `tests/test_snapshot.py` (new test added at end)

- [ ] **Step 3.1: Write the failing test**

Append to `tests/test_snapshot.py`:

```python
def test_snapshot_preserves_k_strength(tmp_path):
    """k_strength must round-trip through save/load."""
    from world.config import WorldConfig
    from world.state import World
    from world.snapshot import save_snapshot, load_snapshot

    cfg = WorldConfig(n_initial_vibrations=0, n_nodes_max=8)
    w = World(cfg)
    # Set distinctive strengths on a few nodes
    w.k_strength[0] = 17.5
    w.k_strength[3] = 99.9
    p = tmp_path / "snapshot_t000000.00.npz"
    save_snapshot(w, p)
    w2 = load_snapshot(p)
    assert w2.k_strength[0] == 17.5
    assert w2.k_strength[3] == 99.9
    # Untouched slots round-trip too
    assert w2.k_strength[1] == 1.0
```

- [ ] **Step 3.2: Run test, expect failure**

```bash
uv run pytest tests/test_snapshot.py::test_snapshot_preserves_k_strength -v
```

Expected: FAIL — `assert 1.0 == 17.5` (because save_snapshot doesn't store the field, the load creates a fresh World with default 1.0).

- [ ] **Step 3.3: Update `save_snapshot` to include `k_strength`**

Edit `world/snapshot.py` — in `save_snapshot`, add `k_strength=world.k_strength` to the `np.savez(...)` call alongside the other `k_*` arrays.

- [ ] **Step 3.4: Update `load_snapshot` to restore `k_strength`**

Edit `world/snapshot.py` — in `load_snapshot`, after the existing block restoring `k_charge` and `k_refractory_until`, add:

```python
    if "k_strength" in data.files:
        w.k_strength[:] = data["k_strength"]
```

- [ ] **Step 3.5: Run test, expect pass + verify suite**

```bash
uv run pytest tests/test_snapshot.py -q
uv run pytest -q
```

Expected: full suite still 155+ green, new test passes.

- [ ] **Step 3.6: Commit**

```bash
git add world/snapshot.py tests/test_snapshot.py
git commit -m "feat(snapshot): persist k_strength across save/load

R2 amendment: strength field is required for memory; must round-trip
through checkpoints so state is preserved across reloads."
```

---

## Task 4: R1 — Recycling regeneration (displace, not allocate)

**Files:**
- Modify: `world/physics.py:183-263` (the `ambient_regeneration` function)
- Test: `tests/test_amendment_R1_recycling_regen.py` (create)

- [ ] **Step 4.1: Write the failing test**

Create `tests/test_amendment_R1_recycling_regen.py`:

```python
"""Tests for R1: recycling regeneration that doesn't saturate the buffer."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import ambient_regeneration


def _make_full_world(n_max: int = 32) -> World:
    """Allocate a world whose vibration buffer is already full."""
    cfg = WorldConfig(
        n_initial_vibrations=n_max,  # fill the buffer at construction
        n_vibrations_max=n_max,
        box_size=(100.0, 100.0, 100.0),
        lambda_gen=1000.0,  # extreme: would normally try to allocate every tick
        lambda_dec=0.0,     # disable decay so the test is deterministic
        rng_seed=42,
    )
    return World(cfg)


def test_recycling_regen_keeps_buffer_size_constant():
    """When buffer is full, regen must displace existing vibrations, not append."""
    w = _make_full_world(n_max=32)
    n_alive_before = int(w.s_alive.sum())
    assert n_alive_before == 32  # buffer is full at construction

    # Run regen for 100 ticks; total alive count must stay ≤ buffer size
    for _ in range(100):
        ambient_regeneration(w, dt=1.0 / 60.0)
        assert int(w.s_alive.sum()) <= 32, (
            f"R1 violation: alive count {int(w.s_alive.sum())} exceeded buffer 32"
        )


def test_recycling_regen_picks_far_field_vibrations():
    """The displaced vibration should come from the far field, not from any active region.

    Active region = within 2× r_2 of any existing node. With no nodes, all
    vibrations are 'far field' and any can be picked.
    """
    w = _make_full_world(n_max=32)
    # Mark a region near (50, 50, 50) as 'active' by placing a node there.
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_alive[0] = True
    w.k_level[0] = 4
    w.k_count = 1
    # Move all 32 vibrations into a small ball around the active node
    w.s_pos[:32] = [50.5, 50.5, 50.5]
    # Run several regen ticks; even with extreme lambda_gen, no vibration
    # should be displaced because they are all in the active region.
    pos_before = w.s_pos[:32].copy()
    for _ in range(20):
        ambient_regeneration(w, dt=1.0 / 60.0)
    # Positions should be approximately unchanged: no displacement happened.
    moved = np.any(np.abs(w.s_pos[:32] - pos_before) > 1.0, axis=1).sum()
    assert moved == 0, f"R1 violation: {moved} vibrations were displaced from the active region"
```

- [ ] **Step 4.2: Run tests, expect failure**

```bash
uv run pytest tests/test_amendment_R1_recycling_regen.py -v
```

Expected: tests fail or behave inconsistently — current `ambient_regeneration` allocates new slots and ignores active regions.

- [ ] **Step 4.3: Replace `ambient_regeneration` with the recycling rule**

Edit `world/physics.py` — replace the entire `ambient_regeneration(world, dt)` function. Key changes:

1. Compute the target ambient density from `lambda_gen / lambda_dec` (current ratio).
2. If current density ≥ target, return (0, 0).
3. While current density < target AND we've made fewer than N_per_tick displacements:
   - Pick a candidate vibration that is **far from any active region** — i.e. its position is more than `2.0 * cfg.r_2` from every alive node. Iterate randomly through alive vibrations to find one.
   - If found: move it to a uniformly random position in the box. Re-sample its frequency, polarity, velocity from the same distributions used in `_seed`. **Do not change `s_alive` count.**
   - If no far-field vibration exists, stop.
4. If buffer has unused slots AND no far-field vibration was found, fall back to allocating a fresh slot (preserves legacy behaviour for sparse worlds).

Pseudocode skeleton (full implementation lives in `world/physics.py`):

```python
def ambient_regeneration(world, dt):
    cfg = world.config
    # Target density = lambda_gen / lambda_dec (existing convention)
    if cfg.lambda_dec <= 0:
        target_density = 0.0
    else:
        target_density = cfg.lambda_gen / cfg.lambda_dec
    box_volume = cfg.box_size[0] * cfg.box_size[1] * cfg.box_size[2]
    target_count = int(target_density * box_volume)
    current_count = int(world.s_alive.sum())
    deficit = max(0, target_count - current_count)
    if deficit == 0:
        return (0, 0)

    n_displaced = 0
    n_allocated = 0
    # Snapshot of active node positions (level >= 4)
    active_mask = world.k_alive[:world.k_count] & (world.k_level[:world.k_count] >= 4)
    active_pos = world.k_pos[:world.k_count][active_mask]
    safe_radius_sq = (2.0 * cfg.r_2) ** 2

    # Try displacement first; fall back to allocation only if no far-field is available
    alive_idx = np.where(world.s_alive)[0]
    world.rng.shuffle(alive_idx)
    box = np.asarray(cfg.box_size, dtype=np.float64)

    for i in alive_idx:
        if deficit <= 0:
            break
        if len(active_pos):
            d = world.s_pos[i] - active_pos
            d -= box * np.round(d / box)  # periodic
            d2 = (d * d).sum(axis=1)
            if (d2 < safe_radius_sq).any():
                continue  # this vibration is in an active region; skip
        # Displace: move to a uniformly random position
        world.s_pos[i] = world.rng.uniform([0, 0, 0], box)
        world.s_vel[i] = world._sample_velocities_3d(1)[0]
        world.s_freq[i] = world._sample_frequencies(1)[0]
        world.s_pol[i] = bool(world.rng.random() < cfg.polarity_split)
        n_displaced += 1
        deficit -= 1

    # Fallback: allocate fresh slots if buffer not full
    free_idx = np.where(~world.s_alive)[0]
    for i in free_idx[:deficit]:
        world.s_pos[i] = world.rng.uniform([0, 0, 0], box)
        world.s_vel[i] = world._sample_velocities_3d(1)[0]
        world.s_freq[i] = world._sample_frequencies(1)[0]
        world.s_pol[i] = bool(world.rng.random() < cfg.polarity_split)
        world.s_alive[i] = True
        if i + 1 > world.n_alive:
            world.n_alive = i + 1
        n_allocated += 1
    return (n_displaced, n_allocated)
```

- [ ] **Step 4.4: Run tests, expect pass + full suite green**

```bash
uv run pytest tests/test_amendment_R1_recycling_regen.py -v
uv run pytest -q
```

Expected: new R1 tests pass, full suite still green.

- [ ] **Step 4.5: Commit**

```bash
git add world/physics.py tests/test_amendment_R1_recycling_regen.py
git commit -m "feat(physics): R1 — recycling ambient regeneration (displace, not allocate)

When buffer is full, regen displaces a far-field vibration instead of
silently no-op'ing. Active regions (within 2*r_2 of any node) are
protected. Fallback to allocation when buffer has unused slots."
```

---

## Task 5: R2 — Strength-aware decay for level-5+ nodes

**Files:**
- Modify: `world/physics.py` (add new function `decay_high_level_nodes`, wire into `tick`)
- Test: `tests/test_amendment_R2_strength_decay.py` (create)

- [ ] **Step 5.1: Write the failing test**

Create `tests/test_amendment_R2_strength_decay.py`:

```python
"""Tests for R2: strength-modulated decay for level-5+ molecules."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import decay_high_level_nodes


def _make_world_with_molecule(strength: float, level: int = 5) -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=16,
        n_nodes_max=8,
        lambda_dec_mol=1.0,  # aggressive decay rate for tests
        rng_seed=42,
    )
    w = World(cfg)
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = level
    w.k_alive[0] = True
    w.k_strength[0] = strength
    w.k_count = 1
    return w


def test_weak_molecule_decays_fast():
    """Strength=1 with lambda_dec_mol=1.0 → ~63% decay over 1s."""
    w = _make_world_with_molecule(strength=1.0)
    # Run 60 ticks at dt=1/60 (1 simulated second)
    n_decayed = 0
    rng_seed = 42
    np.random.seed(rng_seed)
    # Repeat experiment many times to check decay probability
    n_trials = 200
    n_alive_at_end = 0
    for trial in range(n_trials):
        w = _make_world_with_molecule(strength=1.0)
        w.rng = np.random.default_rng(trial)  # different seed per trial
        for _ in range(60):
            decay_high_level_nodes(w, dt=1.0 / 60.0)
        if w.k_alive[0]:
            n_alive_at_end += 1
    survival_rate = n_alive_at_end / n_trials
    # With lambda=1, prob of survival over 1s is exp(-1) ≈ 0.368
    assert 0.25 < survival_rate < 0.50, f"weak survival {survival_rate:.3f} out of [0.25, 0.50]"


def test_strong_molecule_persists():
    """Strength=100 with lambda_dec_mol=1.0 → ~99% survival over 1s."""
    n_trials = 200
    n_alive_at_end = 0
    for trial in range(n_trials):
        w = _make_world_with_molecule(strength=100.0)
        w.rng = np.random.default_rng(trial)
        for _ in range(60):
            decay_high_level_nodes(w, dt=1.0 / 60.0)
        if w.k_alive[0]:
            n_alive_at_end += 1
    survival_rate = n_alive_at_end / n_trials
    # exp(-1/100) ≈ 0.99
    assert survival_rate >= 0.95, f"strong survival {survival_rate:.3f} below 0.95"


def test_only_level_5_plus_decay():
    """Atoms (level 4) are not subject to R2 decay — they stay forever."""
    w = _make_world_with_molecule(strength=1.0, level=4)
    for _ in range(600):
        decay_high_level_nodes(w, dt=1.0 / 60.0)
    assert w.k_alive[0], "level-4 atoms must not decay under R2"


def test_disabled_when_lambda_dec_mol_zero():
    """When lambda_dec_mol=0, R2 must be a no-op."""
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=16, n_nodes_max=8,
        lambda_dec_mol=0.0,
    )
    w = World(cfg)
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = 5
    w.k_alive[0] = True
    w.k_strength[0] = 1.0
    w.k_count = 1
    for _ in range(600):
        decay_high_level_nodes(w, dt=1.0 / 60.0)
    assert w.k_alive[0], "R2 must not fire when lambda_dec_mol == 0"
```

- [ ] **Step 5.2: Run tests, expect failure**

```bash
uv run pytest tests/test_amendment_R2_strength_decay.py -v
```

Expected: FAIL — `decay_high_level_nodes` does not exist yet.

- [ ] **Step 5.3: Implement `decay_high_level_nodes`**

Edit `world/physics.py` — add this function after the existing `decay_unstable_nodes`:

```python
def decay_high_level_nodes(world, dt: float) -> int:
    """R2: strength-modulated decay for level-5+ molecules.

    Per-tick decay probability for each level-5+ alive node:
        p = lambda_dec_mol * dt / max(strength, 1.0)

    When a molecule decays, it disappears (k_alive=False). Constituent
    atoms (level 4) inside its composition span are reset to alive=True so
    they re-enter the available pool — no atoms are lost.

    Returns the count of nodes that decayed this tick.
    """
    cfg = world.config
    if cfg.lambda_dec_mol <= 0.0:
        return 0
    K = world.k_count
    if K == 0:
        return 0
    # Mask alive level-5+ nodes
    mask = world.k_alive[:K] & (world.k_level[:K] >= 5)
    if not mask.any():
        return 0
    indices = np.where(mask)[0]
    strengths = np.maximum(world.k_strength[indices], 1.0)
    p_decay = cfg.lambda_dec_mol * dt / strengths
    rolls = world.rng.random(len(indices))
    decayed_mask = rolls < p_decay
    n_decayed = int(decayed_mask.sum())
    for i in indices[decayed_mask]:
        # Mark this node dead. (Atoms it contains don't share a slot, so
        # they remain alive in their own slots; nothing further to do.)
        world.k_alive[i] = False
        world.k_strength[i] = 1.0  # reset for slot reuse
    return n_decayed
```

- [ ] **Step 5.4: Wire into `tick`**

Edit `tick` in `world/physics.py` — add `decay_high_level_nodes(world, dt)` between `decay_unstable_nodes(...)` and `ambient_regeneration(...)`:

```python
def tick(world, dt: float) -> None:
    box = np.asarray(world.config.box_size, dtype=np.float64)
    move_vibrations(world.s_pos, world.s_vel, world.s_alive, box, dt)
    apply_scale_repulsion(world, dt)
    move_nodes(world, dt)
    bind_vibrations_to_electrons(world)
    bind_nodes_upward(world)
    decay_unstable_nodes(world, dt)
    decay_high_level_nodes(world, dt)   # NEW (R2)
    ambient_regeneration(world, dt)
    neuron_dynamics(world, dt)
    world.t += dt
```

- [ ] **Step 5.5: Run tests, expect pass + suite green**

```bash
uv run pytest tests/test_amendment_R2_strength_decay.py -v
uv run pytest -q
```

Expected: 4 new tests pass, full suite green (note: `lambda_dec_mol` defaults to 0 from Task 1's safe-defaults policy in test fixtures unless explicitly enabled — wait, in `WorldConfig` we set default to 0.001. Re-check Task 1 default.)

**NOTE on default value:** In Task 1 we set `lambda_dec_mol: float = 0.001`. For the existing test suite to remain unaffected, that default needs to be `0.0` (off) instead. Edit `world/config.py` to change `lambda_dec_mol` default to `0.0`:

```python
    lambda_dec_mol: float = 0.0           # 0 = disabled; set > 0 to enable R2 decay
```

Re-run full suite:

```bash
uv run pytest -q
```

Expected: 155+ tests pass.

- [ ] **Step 5.6: Commit**

```bash
git add world/physics.py world/config.py tests/test_amendment_R2_strength_decay.py
git commit -m "feat(physics): R2 — strength-modulated decay for level-5+ molecules

Per-tick decay probability scales inversely with strength, so weak
molecules fade in minutes while strong (heavily-reinforced) molecules
persist effectively indefinitely. Default lambda_dec_mol=0 keeps legacy
configs unaffected."
```

---

## Task 6: R2-strengthening — strength gain from nearby firings

**Files:**
- Modify: `world/physics.py` (modify `neuron_dynamics` to add the strengthening pass)
- Test: extend `tests/test_amendment_R2_strength_decay.py`

- [ ] **Step 6.1: Write the failing test**

Append to `tests/test_amendment_R2_strength_decay.py`:

```python
def test_molecule_near_firing_atom_gets_strengthened():
    """Each tick, level-5+ molecules within r_strengthen of a firing atom
    should have their strength incremented by dt."""
    from world.physics import neuron_dynamics

    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=128,
        n_nodes_max=4,
        rng_seed=42,
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=8, r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.5,
        r_strengthen=10.0,
    )
    w = World(cfg)
    # Atom at (50, 50, 50) — will fire when input vibrations arrive
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = 4
    w.k_alive[0] = True
    # Molecule at (52, 50, 50) — within r_strengthen=10 of atom
    w.k_pos[1] = [52.0, 50.0, 50.0]
    w.k_level[1] = 5
    w.k_alive[1] = True
    w.k_strength[1] = 1.0
    # Molecule at (100, 50, 50) — outside r_strengthen
    w.k_pos[2] = [100.0, 50.0, 50.0]
    w.k_level[2] = 5
    w.k_alive[2] = True
    w.k_strength[2] = 1.0
    w.k_count = 3
    # Seed 5 vibrations at the atom to make it fire
    for i in range(5):
        w.s_pos[i] = [50.0, 50.0, 50.0]
        w.s_freq[i] = 1000.0
        w.s_alive[i] = True
    w.n_alive = 5

    initial_strength_near = w.k_strength[1]
    initial_strength_far = w.k_strength[2]
    neuron_dynamics(w, dt=0.001)

    assert w.k_strength[1] > initial_strength_near, "near molecule must be strengthened"
    assert w.k_strength[2] == initial_strength_far, "far molecule must not be strengthened"
```

- [ ] **Step 6.2: Run test, expect failure**

```bash
uv run pytest tests/test_amendment_R2_strength_decay.py::test_molecule_near_firing_atom_gets_strengthened -v
```

Expected: FAIL — current `neuron_dynamics` doesn't touch `k_strength`.

- [ ] **Step 6.3: Add the strengthening pass to `neuron_dynamics`**

Edit `world/physics.py` — inside the `neuron_dynamics` function, after the existing firing loop produces `firing_atoms`, add this strengthening block (just before the existing `for ai in firing_atoms:` loop, OR after — it's clearer to do it at the end so the just-fired atom contributes to nearby strengthening on the same tick):

```python
    # R2 strengthening: every level-5+ molecule within r_strengthen of any
    # firing atom on this tick gets strength += dt.
    if len(firing_atoms) > 0:
        K = world.k_count
        molecule_mask = world.k_alive[:K] & (world.k_level[:K] >= 5)
        if molecule_mask.any():
            molecule_indices = np.where(molecule_mask)[0]
            molecule_pos = world.k_pos[molecule_indices]
            r2 = cfg.r_strengthen ** 2
            box = np.asarray(cfg.box_size, dtype=np.float64)
            for ai in firing_atoms:
                ap = world.k_pos[ai]
                d = molecule_pos - ap
                d -= box * np.round(d / box)  # periodic
                d2 = (d * d).sum(axis=1)
                near_mask = d2 <= r2
                world.k_strength[molecule_indices[near_mask]] += dt
```

- [ ] **Step 6.4: Run test, expect pass + suite green**

```bash
uv run pytest tests/test_amendment_R2_strength_decay.py -v
uv run pytest -q
```

Expected: all 5 R2 tests pass, full suite green.

- [ ] **Step 6.5: Commit**

```bash
git add world/physics.py tests/test_amendment_R2_strength_decay.py
git commit -m "feat(physics): R2 strengthening — molecules near firings gain strength

Level-5+ molecules within r_strengthen of any firing atom on this tick
gain strength += dt. Combined with R2 decay (per-tick rate inversely
proportional to strength), this gives use-dependent persistence:
heavily-reinforced structures survive indefinitely; one-off coincidences
fade. Long-term memory."
```

---

## Task 7: PHASE3-R1 — Molecule + molecule binding

**Files:**
- Modify: `world/physics.py:75-92` (the `_UPGRADE_TARGET` table) + behaviour gate
- Test: `tests/test_amendment_PHASE3R1_molecule_fusion.py` (create)

- [ ] **Step 7.1: Write the failing test**

Create `tests/test_amendment_PHASE3R1_molecule_fusion.py`:

```python
"""Tests for PHASE3-R1: molecule + molecule binding."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import bind_nodes_upward


def _world_with_two_molecules(level_a: int, level_b: int,
                              freq_a: float, freq_b: float,
                              mol_fusion_enabled: bool = True,
                              freq_tolerance: float = 0.05) -> World:
    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=16,
        n_nodes_max=8,
        box_size=(100.0, 100.0, 100.0),
        r_2=20.0,
        freq_ratio=0.08,
        freq_tolerance=freq_tolerance,
        mol_fusion_enabled=mol_fusion_enabled,
        rng_seed=42,
    )
    w = World(cfg)
    # Two molecules placed within r_2 of each other
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = level_a
    w.k_freq[0] = freq_a
    w.k_alive[0] = True
    w.k_pos[1] = [55.0, 50.0, 50.0]  # within r_2 = 20
    w.k_level[1] = level_b
    w.k_freq[1] = freq_b
    w.k_alive[1] = True
    w.k_count = 2
    return w


def test_two_level5_molecules_bind_to_level6():
    """When mol_fusion_enabled, two level-5 molecules with frequency ratio
    near freq_ratio should bind into a level-6."""
    # freq_a / freq_b = 0.08 (matches freq_ratio)
    w = _world_with_two_molecules(5, 5, freq_a=1000.0, freq_b=12500.0)
    n_bindings = bind_nodes_upward(w)
    assert n_bindings == 1
    # The newly-allocated node should be level 6
    assert w.k_count == 3
    assert w.k_level[2] == 6
    # The two parents should be deactivated
    assert not w.k_alive[0]
    assert not w.k_alive[1]


def test_level5_level6_bind_to_level7():
    w = _world_with_two_molecules(5, 6, freq_a=1000.0, freq_b=12500.0)
    n_bindings = bind_nodes_upward(w)
    assert n_bindings == 1
    assert w.k_count == 3
    assert w.k_level[2] == 7


def test_disabled_when_flag_off():
    """With mol_fusion_enabled=False, level-5 + level-5 must NOT bind."""
    w = _world_with_two_molecules(5, 5, freq_a=1000.0, freq_b=12500.0,
                                   mol_fusion_enabled=False)
    n_bindings = bind_nodes_upward(w)
    assert n_bindings == 0
    assert w.k_count == 2
    assert w.k_alive[0] and w.k_alive[1]


def test_atom_plus_molecule_still_works_when_fusion_enabled():
    """Existing atom→molecule binding must still work with the flag on."""
    w = _world_with_two_molecules(4, 5, freq_a=1000.0, freq_b=12500.0,
                                   mol_fusion_enabled=True)
    n_bindings = bind_nodes_upward(w)
    assert n_bindings == 1
    assert w.k_level[2] == 6  # (4,5)→6 was already in the table
```

- [ ] **Step 7.2: Run tests, expect failure**

```bash
uv run pytest tests/test_amendment_PHASE3R1_molecule_fusion.py -v
```

Expected: 3 fail (level5+level5, level5+level6, atom+molecule with fusion enabled), 1 passes (disabled-flag test).

- [ ] **Step 7.3: Add new entries to `_UPGRADE_TARGET` and gate by config flag**

Edit `world/physics.py:75-92` — extend `_UPGRADE_TARGET`:

```python
_UPGRADE_TARGET = {
    # Phase 1: vibrations → electrons → pairs → triads → atoms
    (1, 1): 2,
    (1, 2): 3, (2, 1): 3,
    (1, 3): 4, (3, 1): 4,
    # Phase 2: atoms binding into molecules. Each upgrade adds one atom; the
    # upgrade table only allows level-4 (atom) on at least one side, so
    # molecules cannot bind to each other.
    (4, 4): 5,
    (4, 5): 6, (5, 4): 6,
    (4, 6): 7, (6, 4): 7,
    (4, 7): 8, (7, 4): 8,
    (4, 8): 9, (8, 4): 9,
    (4, 9): 10, (9, 4): 10,
    (4, 10): 11, (10, 4): 11,
    # Cap at level 11 (deca-atomic). Phase 3+ may revisit.
}

# PHASE3-R1: additional molecule+molecule entries, gated by cfg.mol_fusion_enabled.
# These are appended to the lookup at runtime so legacy behaviour is preserved
# when the flag is off.
_UPGRADE_TARGET_FUSION = {
    (5, 5): 6,
    (5, 6): 7, (6, 5): 7,
    (5, 7): 8, (7, 5): 8,
    (6, 6): 7,
    (6, 7): 8, (7, 6): 8,
    (7, 7): 8,
    (5, 8): 9, (8, 5): 9,
    (6, 8): 9, (8, 6): 9,
    (7, 8): 9, (8, 7): 9,
    (8, 8): 9,
}
```

Then modify the lookup site inside `bind_nodes_upward`. Replace exactly this line in `world/physics.py:123`:

```python
            target = _UPGRADE_TARGET.get((li, lj))
```

with:

```python
            target = _UPGRADE_TARGET.get((li, lj))
            if target is None and cfg.mol_fusion_enabled:
                target = _UPGRADE_TARGET_FUSION.get((li, lj))
```

This keeps the existing flow intact (legacy lookup first, then fusion lookup as a fallback when the flag is on). Nothing else inside `bind_nodes_upward` changes.

- [ ] **Step 7.4: Run tests, expect pass + suite green**

```bash
uv run pytest tests/test_amendment_PHASE3R1_molecule_fusion.py -v
uv run pytest -q
```

Expected: all 4 tests pass, full suite green.

- [ ] **Step 7.5: Commit**

```bash
git add world/physics.py tests/test_amendment_PHASE3R1_molecule_fusion.py
git commit -m "feat(physics): PHASE3-R1 — molecule + molecule binding

Level-5+ molecules can bind into higher-level structures when
mol_fusion_enabled=True. Off by default; legacy behaviour preserved.
Lets structures grow tall (towards level 9), not just wide."
```

---

## Task 8: Tuned PHASE4 emissions — frequency-band fan

**Files:**
- Modify: `world/physics.py:392-425` (the `_emit_vibrations` function)
- Test: `tests/test_tuned_emissions.py` (create)

- [ ] **Step 8.1: Write the failing test**

Create `tests/test_tuned_emissions.py`:

```python
"""Tests for tuned PHASE4 emissions: frequency-band fan."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import _emit_vibrations


def _world_for_emit(emit_band_ratios=(0.08, 1.0, 12.5)):
    cfg = WorldConfig(
        n_initial_vibrations=0,
        n_vibrations_max=64,
        n_nodes_max=4,
        rng_seed=42,
        neuron_dynamics_enabled=True,
        n_emit=12,
        emit_freq=10000.0,
        emit_band_ratios=emit_band_ratios,
    )
    w = World(cfg)
    w.k_pos[0] = [50.0, 50.0, 50.0]
    w.k_level[0] = 4
    w.k_alive[0] = True
    w.k_count = 1
    return w


def test_emissions_span_three_frequency_bands():
    """With emit_band_ratios=(0.08, 1.0, 12.5), emitted vibrations should
    populate three distinct frequency clusters around base/0.08*base/12.5*base."""
    w = _world_for_emit()
    _emit_vibrations(w, atom_idx=0)
    alive_idx = np.where(w.s_alive)[0]
    assert len(alive_idx) == 12
    freqs = w.s_freq[alive_idx]
    base = 10000.0
    # Define each band as ±20% of the centre
    n_low = int(np.sum((freqs > 0.7 * 0.08 * base) & (freqs < 1.3 * 0.08 * base)))
    n_mid = int(np.sum((freqs > 0.7 * base) & (freqs < 1.3 * base)))
    n_high = int(np.sum((freqs > 0.7 * 12.5 * base) & (freqs < 1.3 * 12.5 * base)))
    # Each band should hold roughly 1/3 of the 12 emissions (≥ 2)
    assert n_low >= 2 and n_mid >= 2 and n_high >= 2, (
        f"emission distribution: low={n_low}, mid={n_mid}, high={n_high}"
    )


def test_emissions_position_at_atom():
    """Every emission spawns at the firing atom's position (within ε)."""
    w = _world_for_emit()
    _emit_vibrations(w, atom_idx=0)
    alive_idx = np.where(w.s_alive)[0]
    assert (np.abs(w.s_pos[alive_idx] - [50.0, 50.0, 50.0]) < 0.001).all()


def test_emissions_have_isotropic_velocities():
    """Velocity magnitudes should equal cfg.emit_speed (isotropic directions)."""
    w = _world_for_emit()
    _emit_vibrations(w, atom_idx=0)
    alive_idx = np.where(w.s_alive)[0]
    speeds = np.linalg.norm(w.s_vel[alive_idx], axis=1)
    expected = w.config.emit_speed
    assert np.allclose(speeds, expected, rtol=1e-6)
```

- [ ] **Step 8.2: Run tests, expect failure**

```bash
uv run pytest tests/test_tuned_emissions.py -v
```

Expected: `test_emissions_span_three_frequency_bands` fails (current code emits all at one frequency); the other two tests may already pass.

- [ ] **Step 8.3: Modify `_emit_vibrations` to use the band ratios**

Edit `world/physics.py:392-425` — change the line that sets `world.s_freq[fi] = cfg.emit_freq` to sample from the band:

```python
def _emit_vibrations(world, atom_idx: int) -> None:
    """Emit n_emit vibrations isotropically around the firing atom's position.

    Frequencies are drawn uniformly across the configured emission band
    ratios (e.g. [freq_ratio, 1.0, 1/freq_ratio]) so emitted vibrations can
    climb the binding hierarchy via the existing freq_ratio rule.
    """
    cfg = world.config
    n = cfg.n_emit
    free_mask = ~world.s_alive
    free_idx = np.where(free_mask)[0][:n]
    if len(free_idx) == 0:
        return
    if len(free_idx) < n:
        n = len(free_idx)
        free_idx = free_idx[:n]
    box = np.asarray(cfg.box_size, dtype=np.float64)
    pos = world.k_pos[atom_idx]
    # Isotropic unit vectors via Marsaglia
    z = world.rng.uniform(-1.0, 1.0, size=n)
    phi = world.rng.uniform(0.0, 2 * np.pi, size=n)
    sqrt_omz2 = np.sqrt(1 - z * z)
    vx = sqrt_omz2 * np.cos(phi) * cfg.emit_speed
    vy = sqrt_omz2 * np.sin(phi) * cfg.emit_speed
    vz = z * cfg.emit_speed
    # Frequency band fan: assign each emission to one of the band ratios.
    band_ratios = np.asarray(cfg.emit_band_ratios, dtype=np.float64)
    band_assignments = world.rng.integers(0, len(band_ratios), size=n)
    # Small per-emission jitter (±5%) so within-band binding is possible
    jitter = world.rng.uniform(0.95, 1.05, size=n)
    base_freqs = band_ratios[band_assignments] * cfg.emit_freq * jitter
    for k, fi in enumerate(free_idx):
        world.s_pos[fi] = pos % box
        world.s_vel[fi, 0] = vx[k]
        world.s_vel[fi, 1] = vy[k]
        world.s_vel[fi, 2] = vz[k]
        world.s_freq[fi] = base_freqs[k]
        world.s_pol[fi] = bool(world.rng.random() < cfg.polarity_split)
        world.s_alive[fi] = True
    high = int(free_idx.max()) + 1
    if high > world.n_alive:
        world.n_alive = high
```

- [ ] **Step 8.4: Run tests, expect pass + suite green**

```bash
uv run pytest tests/test_tuned_emissions.py -v
uv run pytest -q
```

Expected: 3 new tests pass, full suite green (155+ + new tests).

- [ ] **Step 8.5: Commit**

```bash
git add world/physics.py tests/test_tuned_emissions.py
git commit -m "feat(physics): tuned PHASE4 emissions across a frequency band

Firings now emit vibrations across three frequency-ratio bands so
emitted vibrations can climb the binding hierarchy via the existing
freq_ratio rule. Default emit_band_ratios=(0.08, 1.0, 12.5) — tuned for
freq_ratio=0.08. Activity-driven growth emerges from existing physics."
```

---

## Task 9: Integration test F1 — Sustained run

**Files:**
- Create: `tests/test_substrate_growth_e2e.py`

- [ ] **Step 9.1: Write the integration test**

Create `tests/test_substrate_growth_e2e.py`:

```python
"""End-to-end integration tests for the substrate growth foundation
(Plan A). These tests instantiate the full physics with all amendments
enabled and verify the F1-F4 acceptance criteria from the foundation
spec §6.1."""
import numpy as np
import pytest
from dataclasses import replace
from world.config import WorldConfig
from world.state import World
from world.physics import tick


def _growth_config(rng_seed: int = 42) -> WorldConfig:
    """Standard config for growth-foundation acceptance tests."""
    return WorldConfig(
        n_initial_vibrations=200,
        n_vibrations_max=512,
        n_nodes_max=128,
        box_size=(60.0, 60.0, 60.0),
        r_1=5.0, r_2=20.0,
        freq_ratio=0.08, freq_tolerance=0.10,
        pair_decay_time=10.0, triad_decay_time=60.0,
        lambda_gen=0.001, lambda_dec=0.001,
        rng_seed=rng_seed,
        # PHASE4 dynamics
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=8, r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.3, emit_speed=15.0,
        # Plan A amendments
        lambda_dec_mol=0.01,
        r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=True,
    )


def _inject_burst(world, position, n=5, freq=10000.0):
    """Helper: place n vibrations at position with zero velocity."""
    free_idx = np.where(~world.s_alive)[0][:n]
    for i in free_idx:
        world.s_pos[i] = np.asarray(position) + world.rng.uniform(-0.5, 0.5, 3)
        world.s_vel[i] = 0.0
        world.s_freq[i] = freq + world.rng.uniform(-100, 100)
        world.s_pol[i] = bool(world.rng.random() < 0.5)
        world.s_alive[i] = True
    if len(free_idx):
        world.n_alive = max(world.n_alive, int(free_idx.max()) + 1)


def _evolve(world, n_seconds, burst_position=None, burst_period_s=0.1):
    """Tick forward, optionally injecting bursts at burst_position every burst_period_s."""
    dt = world.config.dt
    n_ticks = int(n_seconds / dt)
    burst_step = max(1, int(burst_period_s / dt)) if burst_position is not None else None
    for k in range(n_ticks):
        if burst_step and (k + 1) % burst_step == 0:
            _inject_burst(world, burst_position)
        tick(world, dt)


@pytest.mark.slow
def test_F1_sustained_run_does_not_explode_or_collapse():
    """F1: 60-min sim with periodic input maintains a steady-state population.

    Pass: total alive vibration count stays in [25%, 200%] of mean for ≥80% of run.
    """
    w = World(_growth_config())
    burst_pos = [30.0, 30.0, 30.0]
    samples = []
    dt = w.config.dt
    # Sample every 60 simulated seconds across a 60-min run = 60 samples
    for minute in range(60):
        _evolve(w, n_seconds=60.0, burst_position=burst_pos, burst_period_s=0.5)
        samples.append(int(w.s_alive.sum()))

    mean_count = float(np.mean(samples))
    min_count = float(np.min(samples))
    max_count = float(np.max(samples))
    in_band = sum(1 for s in samples if 0.25 * mean_count <= s <= 2.0 * mean_count)
    pct_in_band = in_band / len(samples)

    print(f"F1 stats: mean={mean_count:.0f}, min={min_count:.0f}, "
          f"max={max_count:.0f}, in-band={pct_in_band*100:.0f}%")
    assert pct_in_band >= 0.8, (
        f"F1 violation: only {pct_in_band*100:.0f}% of samples in [0.25×, 2.0×] mean"
    )
```

- [ ] **Step 9.2: Run F1, expect pass (slow)**

```bash
uv run pytest tests/test_substrate_growth_e2e.py::test_F1_sustained_run_does_not_explode_or_collapse -v -s
```

Expected: PASS within ~5-10 wall-clock minutes. If it fails, the substrate is exploding or collapsing — diagnose by adjusting `lambda_dec_mol`, `lambda_gen`, or `r_strengthen` until F1 holds. Iterate within reasonable bounds; if no parameter set works, escalate to spec review.

- [ ] **Step 9.3: Commit**

```bash
git add tests/test_substrate_growth_e2e.py
git commit -m "test(growth): F1 — sustained run does not explode or collapse

60-min simulation with periodic input bursts; total vibration count
stays in [25%, 200%] of mean for ≥80% of samples. First of four F1-F4
acceptance criteria from the substrate growth foundation."
```

---

## Task 10: Integration tests F2, F3a, F3b, F4

**Files:**
- Modify: `tests/test_substrate_growth_e2e.py` (extend)

- [ ] **Step 10.1: Add F2 (activity-coupled growth)**

Append to `tests/test_substrate_growth_e2e.py`:

```python
@pytest.mark.slow
def test_F2_activity_coupled_growth_at_input_location():
    """F2: input only at A. After 5 sim min, level-5+ density at A
    must be ≥ 3× density at distant B (median across 3 rng seeds).

    Pass: median(density_A / density_B) ≥ 3.
    """
    ratios = []
    A = np.array([15.0, 30.0, 30.0])
    B = np.array([45.0, 30.0, 30.0])
    measurement_radius = 8.0
    for seed in [42, 43, 44]:
        w = World(replace(_growth_config(), rng_seed=seed))
        _evolve(w, n_seconds=300.0, burst_position=A.tolist(), burst_period_s=0.5)
        # Count level-5+ alive nodes near A vs near B
        K = w.k_count
        mask5 = w.k_alive[:K] & (w.k_level[:K] >= 5)
        if not mask5.any():
            ratios.append(0.0)
            continue
        positions = w.k_pos[:K][mask5]
        d_A = np.linalg.norm(positions - A, axis=1)
        d_B = np.linalg.norm(positions - B, axis=1)
        n_A = int((d_A < measurement_radius).sum())
        n_B = int((d_B < measurement_radius).sum())
        ratio = n_A / max(n_B, 1)
        ratios.append(ratio)
        print(f"  seed {seed}: A={n_A}, B={n_B}, ratio={ratio:.2f}")
    median_ratio = float(np.median(ratios))
    assert median_ratio >= 3.0, f"F2 violation: median ratio {median_ratio:.2f} < 3.0"
```

- [ ] **Step 10.2: Run F2**

```bash
uv run pytest tests/test_substrate_growth_e2e.py::test_F2_activity_coupled_growth_at_input_location -v -s
```

Expected: PASS. If median ratio is below 3, growth-amendment parameters need re-tuning (likely `r_strengthen`, `lambda_dec_mol`, or `emit_band_ratios`).

- [ ] **Step 10.3: Add F3a (weak structures decay)**

Append:

```python
@pytest.mark.slow
def test_F3a_weak_structures_decay_after_input_stops():
    """F3a: After F2-style training, stop input. After 5 more min,
    density at A must drop ≥ 80% toward B's baseline."""
    A = np.array([15.0, 30.0, 30.0])
    B = np.array([45.0, 30.0, 30.0])
    measurement_radius = 8.0
    decay_fractions = []
    for seed in [42, 43, 44]:
        w = World(replace(_growth_config(), rng_seed=seed))
        # 5-min training at A
        _evolve(w, n_seconds=300.0, burst_position=A.tolist(), burst_period_s=0.5)
        K = w.k_count
        mask5 = w.k_alive[:K] & (w.k_level[:K] >= 5)
        positions = w.k_pos[:K][mask5]
        d_A = np.linalg.norm(positions - A, axis=1)
        n_A_before = int((d_A < measurement_radius).sum())
        # Filter to UNREINFORCED (strength <= 5) — the "weak" subset that should decay
        weak_mask_before = mask5 & (w.k_strength[:K] <= 5.0)
        weak_positions_before = w.k_pos[:K][weak_mask_before]
        d_A_weak = np.linalg.norm(weak_positions_before - A, axis=1)
        n_A_weak_before = int((d_A_weak < measurement_radius).sum())
        # 5-min silence
        _evolve(w, n_seconds=300.0, burst_position=None)
        K = w.k_count
        mask5_after = w.k_alive[:K] & (w.k_level[:K] >= 5)
        positions_after = w.k_pos[:K][mask5_after]
        d_A_after = np.linalg.norm(positions_after - A, axis=1)
        # Count weak structures still alive at A
        weak_mask_after = mask5_after & (w.k_strength[:K] <= 5.0)
        weak_positions_after = w.k_pos[:K][weak_mask_after]
        d_A_weak_after = np.linalg.norm(weak_positions_after - A, axis=1)
        n_A_weak_after = int((d_A_weak_after < measurement_radius).sum())
        decay_fraction = 1.0 - (n_A_weak_after / max(n_A_weak_before, 1))
        decay_fractions.append(decay_fraction)
        print(f"  seed {seed}: weak A {n_A_weak_before}→{n_A_weak_after}, "
              f"decay={decay_fraction*100:.0f}%")
    median_decay = float(np.median(decay_fractions))
    assert median_decay >= 0.8, f"F3a violation: median decay {median_decay*100:.0f}% < 80%"
```

- [ ] **Step 10.4: Run F3a**

```bash
uv run pytest tests/test_substrate_growth_e2e.py::test_F3a_weak_structures_decay_after_input_stops -v -s
```

Expected: PASS.

- [ ] **Step 10.5: Add F3b (strong structures persist)**

Append:

```python
@pytest.mark.slow
def test_F3b_strong_structures_persist_after_input_stops():
    """F3b: structures with strength > 50 (heavily reinforced) decay
    < 20% over the same 5-min silent period."""
    A = np.array([15.0, 30.0, 30.0])
    measurement_radius = 8.0
    persistence_fractions = []
    for seed in [42, 43, 44]:
        w = World(replace(_growth_config(), rng_seed=seed))
        # Long training (10 min) so some structures reach strength > 50
        _evolve(w, n_seconds=600.0, burst_position=A.tolist(), burst_period_s=0.5)
        K = w.k_count
        strong_mask_before = (
            w.k_alive[:K] & (w.k_level[:K] >= 5) & (w.k_strength[:K] > 50.0)
        )
        n_strong_before = int(strong_mask_before.sum())
        if n_strong_before == 0:
            print(f"  seed {seed}: no strong structures formed (n=0)")
            persistence_fractions.append(1.0)  # trivially persistent
            continue
        # 5-min silence
        _evolve(w, n_seconds=300.0, burst_position=None)
        K = w.k_count
        strong_mask_after = (
            w.k_alive[:K] & (w.k_level[:K] >= 5) & (w.k_strength[:K] > 50.0)
        )
        n_strong_after = int(strong_mask_after.sum())
        persistence = n_strong_after / max(n_strong_before, 1)
        persistence_fractions.append(persistence)
        print(f"  seed {seed}: strong before={n_strong_before}, after={n_strong_after}, "
              f"persistence={persistence*100:.0f}%")
    median_persistence = float(np.median(persistence_fractions))
    assert median_persistence >= 0.8, (
        f"F3b violation: median persistence {median_persistence*100:.0f}% < 80%"
    )
```

- [ ] **Step 10.6: Run F3b**

```bash
uv run pytest tests/test_substrate_growth_e2e.py::test_F3b_strong_structures_persist_after_input_stops -v -s
```

Expected: PASS. If `n_strong_before == 0` consistently, increase the training duration or reduce `r_strengthen`/`lambda_dec_mol` to allow strength to build up faster.

- [ ] **Step 10.7: Add F4 (molecule fusion)**

Append:

```python
@pytest.mark.slow
def test_F4_molecule_fusion_produces_level_7_plus_structures():
    """F4: 30-min sim with sustained input must produce level-7+ molecules.

    Control: same run with mol_fusion_enabled=False produces zero level-7+.
    """
    A = [30.0, 30.0, 30.0]
    # Treatment: mol_fusion enabled
    w_treat = World(_growth_config())
    _evolve(w_treat, n_seconds=1800.0, burst_position=A, burst_period_s=0.5)
    K_t = w_treat.k_count
    n_l7_treat = int((w_treat.k_alive[:K_t] & (w_treat.k_level[:K_t] >= 7)).sum())
    # Control: mol_fusion disabled
    w_ctrl = World(replace(_growth_config(), mol_fusion_enabled=False))
    _evolve(w_ctrl, n_seconds=1800.0, burst_position=A, burst_period_s=0.5)
    K_c = w_ctrl.k_count
    n_l7_ctrl = int((w_ctrl.k_alive[:K_c] & (w_ctrl.k_level[:K_c] >= 7)).sum())
    print(f"F4: treatment level-7+={n_l7_treat}, control level-7+={n_l7_ctrl}")
    assert n_l7_treat > 0, "F4 violation: zero level-7+ structures with fusion enabled"
    assert n_l7_ctrl == 0, "F4 violation: control produced level-7+ without fusion enabled"
```

- [ ] **Step 10.8: Run F4**

```bash
uv run pytest tests/test_substrate_growth_e2e.py::test_F4_molecule_fusion_produces_level_7_plus_structures -v -s
```

Expected: PASS within ~10–15 wall-clock minutes per case. If the treatment produces zero level-7+, extend the training duration or lower `freq_tolerance` to allow more molecule pairs to qualify for fusion.

- [ ] **Step 10.9: Commit**

```bash
git add tests/test_substrate_growth_e2e.py
git commit -m "test(growth): F2/F3a/F3b/F4 — full substrate growth acceptance suite

F2: activity-coupled growth (3× density at input location vs distant).
F3a: weak unreinforced structures decay ≥ 80% in 5-min silence.
F3b: strong (strength > 50) structures persist ≥ 80% in same silence.
F4: molecule fusion produces level-7+ structures (zero in control).
Plan A foundation acceptance — substrate is now ready for Plan B (STDP)."
```

---

## Task 11: Document amendment status in the dashboard

**Files:**
- Modify: `db/seed.sql` (mark amendments R1, R2, PHASE3-R1 as `implemented`)

- [ ] **Step 11.1: Update amendment statuses with the new commit SHA**

```bash
# Get the SHA of the F4 commit (last one)
COMMIT_SHA=$(git rev-parse HEAD)

# Connect to Postgres and update the amendments
docker exec vibrasim-postgres psql -U vibrasim -d vibrasim -c "
UPDATE amendments SET status = 'implemented', impl_commit = '$COMMIT_SHA',
                      decided_at = NOW()
WHERE number IN ('R1', 'R2', 'PHASE3-R1');
"
```

- [ ] **Step 11.2: Verify in dashboard**

```bash
docker exec vibrasim-postgres psql -U vibrasim -d vibrasim -c "
SELECT number, title, status, impl_commit FROM amendments
WHERE number IN ('R1', 'R2', 'PHASE3-R1');
"
```

Expected output: status `implemented` for all three, `impl_commit` set to the recent SHA.

- [ ] **Step 11.3: No commit needed** — the seed.sql is unchanged; only DB state. Document the SHA and amendment IDs in the next session note via the dashboard.

---

## Plan A complete

After Task 11, the substrate has all four growth amendments in place (R1, R2, PHASE3-R1, tuned emissions, k_strength) plus F1-F4 acceptance tests passing. The substrate now grows where it fires, decays where it doesn't, retains long-term memory via the strength field, and produces tall structures via molecule fusion.

**Verify final state:**

```bash
uv run pytest -q                    # full suite green (≥165 tests)
uv run pytest -m slow -v            # F1-F4 all pass (slow tests, ~30 wall min total)
git log --oneline -10               # 8 new commits on Plan A topic
```

**Next plans** (each gets its own spec → plan → implementation cycle):

- **Plan B** — STDP + bridge orientation vectors (uses `k_strength`)
- **Plan C** — Audio I/O (independent of substrate amendments)
- **Plan D** — Video I/O (independent)
- **Plan E** — Reward channel + closed-loop orchestrator (depends on A, C, D)
- **Plan F** — Brain checkpoint / resume (depends on A; partially done — `k_strength` already round-trips)
- **Plan G** — End-to-end demo (M1-M4 acceptance, depends on everything)

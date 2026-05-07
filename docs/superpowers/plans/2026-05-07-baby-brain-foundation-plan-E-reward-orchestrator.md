# Plan E — Reward channel + closed-loop orchestrator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tie the substrate, audio I/O, and video I/O into a closed loop. Add a programmatic reward channel with `+`/`−` asymmetric STDP physics. Deliver M4 (glass-of-water demo, headline), M5 (reward shaping, headline), I5 (reward latency, fast).

**Architecture:** Three modules under the existing `agent/` package. (1) `agent/reward.py` — `RewardChannel` class with `fire_positive` / `fire_negative`. (2) `agent/loop.py` — `AgentLoop` class with stepped + real-time modes, called from tests in stepped mode and from a CLI in real-time mode. (3) `agent/demo.py` — CLI entry point for the live demo. Plus a substrate extension to Plan B's `apply_stdp`: when `k_reward_polarity[atom_j] == -1`, swap LTP↔LTD. New tristate `k_reward_polarity: int8` field on nodes (default 0; +1/-1 for fire_positive/fire_negative origin), persisted in snapshots.

**Tech Stack:** Python 3.13, NumPy, pytest. No new runtime dependencies. Lazy imports of `sounddevice` and `cv2` from Plans C/D inherited.

**Spec reference:** `docs/superpowers/specs/2026-05-07-baby-brain-foundation-plan-E-reward-orchestrator-design.md` — approved 2026-05-07. All six design choices locked.

**Prerequisite:** Plans A, A.5, B, C, D merged to main. Plan E ties them together.

---

## File map

| Path | Action | Responsibility |
|---|---|---|
| `world/config.py` | Modify | Add 5 reward + 1 orchestrator config fields |
| `world/state.py` | Modify | Add `s_reward_polarity: int8` per vibration + `k_reward_polarity: int8` per node |
| `world/snapshot.py` | Modify | Persist `k_reward_polarity` with backward-compat guard |
| `world/physics.py` | Modify | Extend `bind_nodes_upward` (atom branch) to set `k_reward_polarity` per propagation rule; extend `apply_stdp` with the tristate swap |
| `agent/reward.py` | Create | `RewardChannel` class |
| `agent/loop.py` | Create | `AgentLoop` class (stepped + real-time) |
| `agent/demo.py` | Create | CLI entry: `python -m agent.demo --m4` |
| `agent/__init__.py` | Modify | Re-export RewardChannel + AgentLoop |
| `tests/acceptance.toml` | Modify | Add `[M4]`, `[M5]` sections + provenance |
| `tests/fixtures/water.wav` | Create | ~50 KB real recording for the demo (not load-bearing for tests) |
| `tests/test_reward_channel.py` | Create | RC1-RC3 unit tests |
| `tests/test_reward_asymmetric_stdp.py` | Create | RA1-RA5 unit tests for tristate physics |
| `tests/test_agent_loop_stepped.py` | Create | AL1-AL2 + I5 |
| `tests/test_agent_m4_glass_of_water.py` | Create | M4 (slow, headline) |
| `tests/test_agent_m5_reward_shaping.py` | Create | M5 (slow, headline) |
| `tests/test_agent_realtime_smoke.py` | Create | AL3 (slow) |
| `db/migrations/0009_planE_reward_orchestrator_amendment.sql` | Create | REWARD-R1 amendment + Makefile target |

---

## Task 1: Plan E config fields + acceptance.toml extension

**Files:**
- Modify: `world/config.py`
- Modify: `tests/acceptance.toml`
- Test: `tests/test_config.py` (append)

- [ ] **Step 1.1: Append the failing test**

```python
def test_plan_E_reward_fields_have_safe_defaults():
    """Plan E reward + orchestrator fields default off / inert."""
    cfg = WorldConfig()
    assert cfg.reward_port_origin == (45.0, 45.0, 0.0)
    assert cfg.reward_port_size == (15.0, 15.0, 15.0)
    assert cfg.reward_burst_size == 12
    assert cfg.reward_burst_freq == 30000.0
    assert cfg.agent_dt_realtime_ms == 17
```

- [ ] **Step 1.2: Run, expect failure**

```bash
uv run pytest tests/test_config.py::test_plan_E_reward_fields_have_safe_defaults -v
```

- [ ] **Step 1.3: Add fields to WorldConfig**

In `world/config.py`, add after the Plan D video block, before Plan A.5 perf:

```python
    # Plan E — reward channel + orchestrator
    reward_port_origin: tuple[float, float, float] = (45.0, 45.0, 0.0)
    reward_port_size: tuple[float, float, float] = (15.0, 15.0, 15.0)
    reward_burst_size: int = 12
    reward_burst_freq: float = 30000.0
    agent_dt_realtime_ms: int = 17
```

- [ ] **Step 1.4: Add M4/M5 to acceptance.toml**

Append to `tests/acceptance.toml`:

```toml
[M4]
duration_sim_min = 10.0
n_pairs = 50
test_phase_sim_sec = 30.0
cosine_min = 0.5

[M5]
n_trials = 100
n_seeds = 5
ci_confidence = 0.95
margin_min = 0.10

[provenance.plan_E]
calibration_seeds = [42, 43, 44]
held_out_seeds = [7, 100, 314, 999, 2024]
thresholds_frozen_at_commit = "<filled at first calibration commit>"
```

- [ ] **Step 1.5: Run + commit**

```bash
uv run pytest -q -m "not slow"
```

Expected: 249 passed (248 baseline + 1 new), 14 deselected.

```bash
git add world/config.py tests/acceptance.toml tests/test_config.py
git commit -m "feat(config): Plan E Task 1 — reward + orchestrator fields + M4/M5 acceptance

5 reward/orchestrator fields default to inert values. acceptance.toml
gains [M4] and [M5] sections + plan_E provenance. Calibration seeds
{42,43,44} and held-out seeds {7,100,314,999,2024} frozen before
implementation per Plan A's pre-registration discipline."
```

---

## Task 2: `k_reward_polarity` field on World state + snapshot persistence

**Files:**
- Modify: `world/state.py`
- Modify: `world/snapshot.py`
- Test: `tests/test_state.py` (append)
- Test: `tests/test_snapshot.py` (append)

- [ ] **Step 2.1: Append failing tests**

To `tests/test_state.py`:

```python
def test_plan_E_reward_polarity_fields_init_zero():
    """k_reward_polarity (per node) and s_reward_polarity (per vibration)
    default to 0 (no reward signal)."""
    cfg = WorldConfig(n_initial_vibrations=0, n_nodes_max=8, n_vibrations_max=8)
    w = World(cfg)
    assert w.k_reward_polarity.shape == (8,)
    assert w.k_reward_polarity.dtype == np.int8
    assert (w.k_reward_polarity == 0).all()
    assert w.s_reward_polarity.shape == (8,)
    assert w.s_reward_polarity.dtype == np.int8
    assert (w.s_reward_polarity == 0).all()
```

To `tests/test_snapshot.py`:

```python
def test_snapshot_preserves_k_reward_polarity(tmp_path):
    """k_reward_polarity round-trips through save/load with int8 precision."""
    from world.config import WorldConfig
    from world.state import World
    from world.snapshot import save_snapshot, load_snapshot

    cfg = WorldConfig(n_initial_vibrations=0, n_nodes_max=8)
    w = World(cfg)
    w.k_reward_polarity[3] = 1
    w.k_reward_polarity[5] = -1
    p = tmp_path / "snapshot_t000000.00.npz"
    save_snapshot(w, p)
    w2 = load_snapshot(p)
    assert int(w2.k_reward_polarity[3]) == 1
    assert int(w2.k_reward_polarity[5]) == -1
    assert int(w2.k_reward_polarity[0]) == 0
```

- [ ] **Step 2.2: Run, expect failure**

- [ ] **Step 2.3: Add fields to `World.__init__`**

In `world/state.py`, after the existing `k_orientation` (Plan B) line:

```python
        # Plan E — reward polarity tristate (-1, 0, +1) per node
        # 0 = not from reward channel; +1 = fire_positive origin; -1 = fire_negative origin
        self.k_reward_polarity = np.zeros(K, dtype=np.int8)
```

After the `s_alive` (or `s_pol`) line, add:

```python
        # Plan E — reward polarity tristate per vibration
        self.s_reward_polarity = np.zeros(N_v, dtype=np.int8)
```

(Use the actual variable name for vibration count from existing code.)

- [ ] **Step 2.4: Update `World.allocate_node` to reset `k_reward_polarity` on slot recycle**

In `world/state.py`, find the slot-recycle branch in `allocate_node` (added in Plan A.5). After the existing `k_strength[i] = 1.0` and `k_orientation[i] = 0.0` lines, add:

```python
        world.k_reward_polarity[i] = 0  # Plan E: clear stale reward tag from dead predecessor
```

- [ ] **Step 2.5: Update snapshot save/load for k_reward_polarity**

In `world/snapshot.py`'s `save_snapshot`, add `k_reward_polarity=world.k_reward_polarity` to the npz savez call alongside `k_orientation`.

In `load_snapshot`, after the existing `if "k_orientation" in data.files:` block, add:

```python
    if "k_reward_polarity" in data.files:
        w.k_reward_polarity[:] = data["k_reward_polarity"]
```

(Backward-compat: legacy snapshots without this field stay at the zero-init default, which means "no reward signal" — correct behaviour.)

- [ ] **Step 2.6: Run + commit**

```bash
uv run pytest -q -m "not slow"
```

Expected: 251 passed (249 + 2 new), 14 deselected.

```bash
git add world/state.py world/snapshot.py tests/test_state.py tests/test_snapshot.py
git commit -m "feat(state+snapshot): Plan E Task 2 — k_reward_polarity tristate

Per-node int8 tristate (-1, 0, +1) signals reward-channel origin:
0 = not from reward; +1 = fire_positive; -1 = fire_negative. Default
zero is the safe, ignore-for-asymmetric-reasoning value.

Plus s_reward_polarity per vibration (set by RewardChannel in Task 4).

allocate_node clears k_reward_polarity on slot recycle, matching the
existing k_strength and k_orientation resets. Snapshot persistence
uses the backward-compat guard pattern from Plans A and B."
```

---

## Task 3: `bind_nodes_upward` propagates reward polarity into atoms

**Files:**
- Modify: `world/physics.py` (extend the atom-formation branch)
- Test: `tests/test_reward_polarity_propagation.py` (create)

- [ ] **Step 3.1: Write the failing tests**

```python
"""Tests for k_reward_polarity propagation during atom formation."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from world.physics import bind_nodes_upward


def _world_with_pre_triad():
    """World seeded with a triad already formed at level 3, plus a single
    free electron about to bind into an atom."""
    # Detailed setup omitted in plan summary; full setup in test file.
    ...


def test_RPP1_all_positive_constituents_yield_positive_atom():
    """Triad + electron all from fire_positive origin (s_reward_polarity=+1)
    → atom k_reward_polarity = +1."""
    ...


def test_RPP2_all_negative_constituents_yield_negative_atom():
    """All -1 → atom = -1."""
    ...


def test_RPP3_mixed_constituents_yield_zero_atom():
    """Some +1 + some 0 → atom = 0 (mixed origin, no reward signal)."""
    ...


def test_RPP4_conflicting_constituents_yield_zero_atom():
    """Some +1 + some -1 → atom = 0 (conflict, no reward signal)."""
    ...


def test_RPP5_all_zero_constituents_yield_zero_atom():
    """Default substrate atoms (no reward origin) stay at 0."""
    ...
```

(Plan markdown summary; full test code in the implementation. The
implementer writes the full setup using the existing `World` API.)

- [ ] **Step 3.2: Run, expect failure**

- [ ] **Step 3.3: Implement propagation in `bind_nodes_upward`**

In `world/physics.py`, find the atom-formation branch in `bind_nodes_upward` (where a triad + electron binds into a level-4 atom). Currently the new atom inherits geometric properties (position, frequency) from constituents.

Add: after computing the atom's other properties, compute `k_reward_polarity` per the §5.2 propagation rule. Algorithm:

1. Collect the `s_reward_polarity` values of all constituent vibrations (transitively via `k_comp_offset` / `k_comp_end` to gather all leaf vibrations under the atom).
2. If all values are non-zero AND identical → atom inherits that value.
3. Otherwise (mixed or all-zero) → atom is 0.

Pseudocode:

```python
# After atom binding succeeds, before slot is alive:
constituent_vibration_indices = _gather_leaf_vibrations(world, new_atom_idx)
polarities = world.s_reward_polarity[constituent_vibration_indices]
if len(polarities) > 0 and (polarities != 0).all() and (polarities == polarities[0]).all():
    world.k_reward_polarity[new_atom_idx] = int(polarities[0])
else:
    world.k_reward_polarity[new_atom_idx] = 0  # already default; explicit for clarity
```

The `_gather_leaf_vibrations` helper walks the composition tree via `k_comp_offset` / `k_comp_end` looking for level-1 (electron) constituents and gathering their constituent vibrations. New helper, ~15 lines.

- [ ] **Step 3.4: Run + commit**

Expected: 256 passed (251 + 5 new RPP tests).

```bash
git add world/physics.py tests/test_reward_polarity_propagation.py
git commit -m "feat(physics): Plan E Task 3 — k_reward_polarity propagation in bind_nodes_upward

When a triad + electron binds into a level-4 atom, traverse the
composition tree to gather all constituent vibrations' s_reward_polarity
values. If all are non-zero and identical, the atom inherits that
value; otherwise (mixed or any-zero), the atom is 0.

Conservative: requires reward-purity for an atom to be tagged. Mixed-
origin atoms (ambient drift binding with reward bursts) stay at 0
and don't trigger the asymmetric STDP swap."
```

---

## Task 4: `RewardChannel` class

**Files:**
- Create: `agent/reward.py`
- Modify: `agent/__init__.py`
- Test: `tests/test_reward_channel.py`

- [ ] **Step 4.1: Write failing tests RC1-RC3**

```python
"""Tests for RewardChannel (RC1, RC2, RC3)."""
import numpy as np
from world.config import WorldConfig
from world.state import World
from agent.reward import RewardChannel


def _make_world():
    return World(WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=64,
        box_size=(60.0, 60.0, 60.0),
        reward_port_origin=(45.0, 45.0, 0.0),
        reward_port_size=(15.0, 15.0, 15.0),
        reward_burst_size=12,
        reward_burst_freq=30000.0,
    ))


def test_RC1_fire_positive_injects_burst_with_positive_polarity():
    w = _make_world()
    rc = RewardChannel(rng=np.random.default_rng(0))
    n_alive_before = int(w.s_alive.sum())
    n = rc.fire_positive(w)
    n_alive_after = int(w.s_alive.sum())
    assert n == 12
    assert n_alive_after == n_alive_before + 12
    new_idx = np.where(w.s_alive)[0]
    pos = w.s_pos[new_idx]
    assert ((pos[:, 0] >= 45) & (pos[:, 0] <= 60)).all()
    assert ((pos[:, 1] >= 45) & (pos[:, 1] <= 60)).all()
    assert ((pos[:, 2] >= 0) & (pos[:, 2] <= 15)).all()
    assert (w.s_freq[new_idx] == 30000.0).all()
    assert (w.s_pol[new_idx] == True).all()
    assert (w.s_reward_polarity[new_idx] == 1).all()


def test_RC2_fire_negative_symmetric_with_negative_polarity():
    w = _make_world()
    rc = RewardChannel(rng=np.random.default_rng(0))
    n = rc.fire_negative(w)
    new_idx = np.where(w.s_alive)[0]
    assert (w.s_pol[new_idx] == False).all()
    assert (w.s_reward_polarity[new_idx] == -1).all()


def test_RC3_is_in_reward_port_bounds():
    rc = RewardChannel()
    assert rc.is_in_reward_port(np.array([47.5, 47.5, 7.5]))   # centre
    assert rc.is_in_reward_port(np.array([45.0, 45.0, 0.0]))   # corner
    assert rc.is_in_reward_port(np.array([60.0, 60.0, 15.0]))  # opposite corner
    assert not rc.is_in_reward_port(np.array([44.9, 47.5, 7.5]))   # outside x
    assert not rc.is_in_reward_port(np.array([47.5, 47.5, 15.1]))  # outside z
    assert not rc.is_in_reward_port(np.array([0.0, 0.0, 0.0]))     # nowhere near
```

- [ ] **Step 4.2: Run, expect failure**

- [ ] **Step 4.3: Implement `agent/reward.py`**

```python
"""Plan E — programmatic reward injector."""
from typing import Optional
import numpy as np


class RewardChannel:
    """Programmatic reward injector. fire_positive / fire_negative inject a
    burst of vibrations at the reward port with explicit s_reward_polarity
    tag (+1 or -1). Atoms that bind from these vibrations carry the polarity
    via the k_reward_polarity propagation rule in bind_nodes_upward."""

    def __init__(
        self,
        port_origin: tuple[float, float, float] = (45.0, 45.0, 0.0),
        port_size: tuple[float, float, float] = (15.0, 15.0, 15.0),
        burst_size: int = 12,
        burst_freq: float = 30000.0,
        rng: Optional[np.random.Generator] = None,
    ):
        self.port_origin = port_origin
        self.port_size = port_size
        self.burst_size = burst_size
        self.burst_freq = burst_freq
        self.rng = rng if rng is not None else np.random.default_rng()

    def fire_positive(self, world) -> int:
        return self._fire(world, polarity=True, reward_polarity=1)

    def fire_negative(self, world) -> int:
        return self._fire(world, polarity=False, reward_polarity=-1)

    def _fire(self, world, polarity: bool, reward_polarity: int) -> int:
        free_idx = np.where(~world.s_alive)[0][:self.burst_size]
        n = len(free_idx)
        if n == 0:
            return 0
        for i in free_idx:
            world.s_pos[i] = (
                self.port_origin[0] + self.rng.random() * self.port_size[0],
                self.port_origin[1] + self.rng.random() * self.port_size[1],
                self.port_origin[2] + self.rng.random() * self.port_size[2],
            )
            world.s_vel[i] = 0.0
            world.s_freq[i] = float(self.burst_freq)
            world.s_pol[i] = polarity
            world.s_alive[i] = True
            world.s_reward_polarity[i] = reward_polarity
        if n > 0:
            world.n_alive = max(world.n_alive, int(free_idx.max()) + 1)
        return n

    def is_in_reward_port(self, position: np.ndarray) -> bool:
        ox, oy, oz = self.port_origin
        sx, sy, sz = self.port_size
        return (ox <= position[0] <= ox + sx
                and oy <= position[1] <= oy + sy
                and oz <= position[2] <= oz + sz)
```

Update `agent/__init__.py` to re-export `RewardChannel`:

```python
from agent.reward import RewardChannel

__all__ = [
    "AudioIO", "VideoIO", "RewardChannel",
    "freq_to_port_position", "encode_block", "decode_to_audio",
    "downsample_frame", "build_oriented_filter_bank", "encode_frame",
    "patch_to_port_position", "feature_magnitude_to_frequency",
]
```

- [ ] **Step 4.4: Run + commit**

Expected: 259 passed (256 + 3 RC tests).

```bash
git add agent/reward.py agent/__init__.py tests/test_reward_channel.py
git commit -m "feat(agent): Plan E Task 4 — RewardChannel class (RC1-RC3)

fire_positive injects burst_size vibrations at random positions inside
the reward port with s_pol=True and s_reward_polarity=+1. fire_negative
is symmetric with False / -1. is_in_reward_port bounds-checks a 3D
position against the port volume."
```

---

## Task 5: Asymmetric STDP physics — `apply_stdp` extension

**Files:**
- Modify: `world/physics.py` (extend `apply_stdp`)
- Test: `tests/test_reward_asymmetric_stdp.py` (RA1-RA5)

- [ ] **Step 5.1: Write failing tests RA1-RA5**

The five tests follow the table in spec §5.4. Each constructs a minimal world with two atoms and a single bridge molecule between them; sets up the firing pair with the matching geometry (`k_reward_polarity` of `atom_j`, alignment of bridge orientation with A→B); calls `apply_stdp`; asserts the bridge's strength changed in the expected direction.

Example RA2 (the new flipped case):

```python
def test_RA2_negative_reward_atom_aligned_orientation_flips_to_LTD():
    """Pair: non-reward atom → reward-port atom with k_reward_polarity=-1.
    Existing bridge orientation aligned with A→B (which would normally
    apply LTP). The flip changes it to LTD."""
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=16, n_nodes_max=16,
        box_size=(100.0, 100.0, 100.0),
        stdp_enabled=True,
        tau_LTP=0.020, tau_LTD=0.020,
        delta_LTP=1.0, delta_LTD=0.5,
        r_bridge=5.0,
    )
    w = World(cfg)
    # Atom 0 at (50,50,50), non-reward (k_reward_polarity=0)
    w.k_pos[0] = [50, 50, 50]; w.k_level[0] = 4; w.k_alive[0] = True
    # Atom 1 at (70,50,50), reward port — set k_reward_polarity = -1
    w.k_pos[1] = [70, 50, 50]; w.k_level[1] = 4; w.k_alive[1] = True
    w.k_reward_polarity[1] = -1
    # Bridge molecule at (60,50,50) with orientation already aligned with A→B
    w.k_pos[2] = [60, 50, 50]; w.k_level[2] = 5; w.k_alive[2] = True
    w.k_strength[2] = 100.0
    w.k_orientation[2] = [1.0, 0.0, 0.0]
    w.k_count = 3

    initial_strength = float(w.k_strength[2])
    w.firing_events = [(0.000, 0), (0.010, 1)]
    w.t = 0.020
    from world.physics import apply_stdp
    apply_stdp(w)

    # Without the flip, this would be LTP (alignment=1.0, atom in tube,
    # strength would increase). With the flip, it's LTD: strength decreases.
    final_strength = float(w.k_strength[2])
    assert final_strength < initial_strength, (
        f"RA2: expected LTD (strength decrease), got "
        f"{initial_strength} → {final_strength}"
    )
```

RA1, RA3, RA4 are symmetric with their own (alignment, k_reward_polarity) combinations. RA5 verifies that an atom inside the reward port BUT with k_reward_polarity=0 does NOT trigger the swap.

- [ ] **Step 5.2: Run, expect failures**

- [ ] **Step 5.3: Extend `apply_stdp`**

In `world/physics.py`, find the existing `apply_stdp` from Plan B. Inside the bridge-molecule loop where the LTP/LTD branch is decided, add the swap check BEFORE the existing alignment branch:

```python
# Plan E asymmetric reward physics
swap_ltp_ltd = (world.k_reward_polarity[atom_j] == -1)

for m in bridge_indices:
    # ... existing alignment computation: o, o_norm, alignment ...
    if (alignment >= 0 and not swap_ltp_ltd) or (alignment < 0 and swap_ltp_ltd):
        # LTP path
        ...
    else:
        # LTD path
        ...
```

The existing inner code structure from Plan B Task 6 is preserved; only the LTP/LTD branch decision changes.

- [ ] **Step 5.4: Run + commit**

Expected: 264 passed (259 + 5 RA tests). Plan B's existing BS1-BS5 must still pass — verify no regression.

```bash
git add world/physics.py tests/test_reward_asymmetric_stdp.py
git commit -m "feat(physics): Plan E Task 5 — asymmetric STDP at reward boundary

Extends Plan B's apply_stdp with a tristate-gated swap: when the
second atom in a firing pair has k_reward_polarity = -1, the LTP/LTD
outcome is flipped. Atoms with k_reward_polarity = 0 (the default,
ambient origin) take the existing alignment-based path unchanged.

RA1-RA5 cover the four pair geometries plus the ambient-port-resident
case. BS1-BS5 (Plan B) regression-checked: no change because non-reward
atoms have k_reward_polarity = 0."
```

---

## Task 6: `AgentLoop.step` (Mode 1 — stepped)

**Files:**
- Create: `agent/loop.py`
- Modify: `agent/__init__.py` (re-export AgentLoop)
- Test: `tests/test_agent_loop_stepped.py` (AL1, AL2, I5)

- [ ] **Step 6.1: Write failing tests**

```python
"""Tests for AgentLoop (AL1, AL2 + I5)."""
import numpy as np
from unittest.mock import MagicMock
from world.config import WorldConfig
from world.state import World
from agent.loop import AgentLoop
from agent.reward import RewardChannel


def test_AL1_step_calls_inject_then_tick_then_read_in_order():
    """Order matters: inject_into_substrate (audio + video) → tick → read."""
    w = World(WorldConfig(n_initial_vibrations=0, n_vibrations_max=8))
    audio_mock = MagicMock()
    video_mock = MagicMock()
    audio_mock.inject_into_substrate.return_value = 0
    video_mock.inject_into_substrate.return_value = 0
    audio_mock.read_from_substrate.return_value = 0

    call_order = []
    audio_mock.inject_into_substrate.side_effect = lambda *a, **kw: call_order.append("audio_inject") or 0
    video_mock.inject_into_substrate.side_effect = lambda *a, **kw: call_order.append("video_inject") or 0
    audio_mock.read_from_substrate.side_effect = lambda *a, **kw: call_order.append("audio_read") or 0

    loop = AgentLoop(w, audio_io=audio_mock, video_io=video_mock)
    loop.step(w.config.dt)
    # inject (audio, video) happens before tick; read after tick
    # We can't easily mock tick, but we can assert the inject calls came
    # before the read call.
    assert call_order.index("audio_inject") < call_order.index("audio_read")
    assert call_order.index("video_inject") < call_order.index("audio_read")


def test_AL2_step_with_no_io_is_just_tick():
    """No audio_io / video_io → step is just a tick."""
    w = World(WorldConfig(n_initial_vibrations=0, n_vibrations_max=8))
    loop = AgentLoop(w)
    t_before = w.t
    loop.step(w.config.dt)
    assert w.t > t_before  # tick advanced t


def test_I5_reward_firing_latency_within_100ms():
    """RewardChannel.fire_positive(world) followed by 6 steps (=100 ms at
    dt=1/60) produces ≥ 1 firing event from a reward-port-resident atom."""
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=128, n_nodes_max=64,
        box_size=(60.0, 60.0, 60.0),
        reward_port_origin=(45.0, 45.0, 0.0),
        reward_port_size=(15.0, 15.0, 15.0),
        reward_burst_size=12,
        reward_burst_freq=30000.0,
        # Substrate dynamics tuned for fast atom formation
        freq_tolerance=0.025,
        neuron_dynamics_enabled=True,
        theta_fire=4.0, n_emit=8, r_integrate=5.0,
        t_refractory=0.05, tau_membrane=0.3,
        rng_seed=42,
    )
    w = World(cfg)
    rc = RewardChannel(rng=np.random.default_rng(42))
    rc.fire_positive(w)

    loop = AgentLoop(w)
    for _ in range(6):
        loop.step(cfg.dt)

    # Check: ≥ 1 firing event from an atom inside the reward port
    rc_atoms = []
    for t_fire, atom_idx in w.firing_events:
        if rc.is_in_reward_port(w.k_pos[atom_idx]):
            rc_atoms.append(atom_idx)
    print(f"I5: {len(w.firing_events)} total firings, "
          f"{len(rc_atoms)} from reward-port atoms")
    assert len(rc_atoms) >= 1, (
        f"I5: expected ≥1 reward-port firing within 100 ms, got {len(rc_atoms)}"
    )
```

- [ ] **Step 6.2: Run, expect failure (ImportError)**

- [ ] **Step 6.3: Implement `agent/loop.py` (Mode 1 only — Mode 2/3 in later tasks)**

```python
"""Plan E — closed-loop orchestrator.

Mode 1 (stepped, this task): tests call AgentLoop.step(dt) directly.
Mode 2 (real-time, Task 9): start_realtime spawns a substrate thread.
Mode 3 (demo, Task 10): python -m agent.demo CLI entry point.
"""
from typing import Optional
from world.physics import tick


class AgentLoop:
    """Closed-loop orchestrator. Stepped mode for tests; real-time mode for
    live operation. Audio/video capture+playback threads run independently;
    the loop's substrate path consumes their buffers each tick."""

    def __init__(
        self,
        world,
        audio_io=None,
        video_io=None,
        reward=None,
    ):
        self.world = world
        self.audio_io = audio_io
        self.video_io = video_io
        self.reward = reward
        self._realtime_thread = None
        self._realtime_running = False

    def step(self, dt: float) -> None:
        """One substrate tick + I/O sync. Inject from audio + video first,
        then tick, then read audio output. Reward is fired explicitly by
        the caller (e.g. M5's reward dispenser); the loop doesn't auto-fire."""
        if self.audio_io is not None:
            self.audio_io.inject_into_substrate(self.world, dt)
        if self.video_io is not None:
            self.video_io.inject_into_substrate(self.world, dt)
        tick(self.world, dt)
        if self.audio_io is not None:
            self.audio_io.read_from_substrate(self.world, dt)

    def start_realtime(self) -> None:
        """Spawn substrate thread. Filled in Task 9."""
        raise NotImplementedError("AgentLoop.start_realtime — Task 9")

    def stop_realtime(self) -> None:
        raise NotImplementedError("AgentLoop.stop_realtime — Task 9")
```

Update `agent/__init__.py` to re-export `AgentLoop`.

- [ ] **Step 6.4: Run + commit**

Expected: 267 passed (264 + 3: AL1, AL2, I5).

```bash
git add agent/loop.py agent/__init__.py tests/test_agent_loop_stepped.py
git commit -m "feat(agent): Plan E Task 6 — AgentLoop.step (Mode 1 stepped)

AL1 verifies inject(audio,video)→tick→read order. AL2 verifies the no-IO
case is just a tick. I5 verifies reward latency: fire_positive →
6 ticks (=100 ms at dt=1/60) → ≥ 1 firing event from a reward-port
atom. Real-time and demo modes deferred to Tasks 9 and 10."
```

---

## Task 7: M4 stepped test — glass-of-water demo (slow, headline)

**Files:**
- Create: `tests/test_agent_m4_glass_of_water.py`

- [ ] **Step 7.1: Write the test**

```python
"""Headline integration test M4 — glass-of-water demo (stepped, slow)."""
import numpy as np
import pytest
import tomllib
from pathlib import Path
from world.config import WorldConfig
from world.state import World
from agent.loop import AgentLoop


def _load_acceptance():
    p = Path(__file__).parent / "acceptance.toml"
    with p.open("rb") as f:
        return tomllib.load(f)


def _synthesize_glass_image(size: int = 256) -> np.ndarray:
    """Bright circular ring on dark background — synthetic 'glass'."""
    img = np.zeros((size, size), dtype=np.uint8)
    yy, xx = np.ogrid[:size, :size]
    cx, cy, r = size // 2, size // 2, size * 60 // 256
    mask = (xx - cx) ** 2 + (yy - cy) ** 2
    img[(mask >= (r - 2) ** 2) & (mask <= (r + 2) ** 2)] = 255
    return img


def _synthesize_water_audio(duration_sec: float, sample_rate: int = 16000) -> np.ndarray:
    """Three-tone water signature: 500 + 1000 + 1500 Hz."""
    t = np.arange(int(sample_rate * duration_sec)) / sample_rate
    audio = (
        np.sin(2 * np.pi * 500 * t)
        + np.sin(2 * np.pi * 1000 * t)
        + np.sin(2 * np.pi * 1500 * t)
    ).astype(np.float32) * 0.3
    return audio


def _spectral_cosine(audio: np.ndarray, target: np.ndarray) -> float:
    """Cosine similarity between two audio buffers' magnitude spectra."""
    n = min(len(audio), len(target))
    if n < 32:
        return 0.0
    spec_a = np.abs(np.fft.rfft(audio[:n]))
    spec_t = np.abs(np.fft.rfft(target[:n]))
    norm_a = float(np.linalg.norm(spec_a))
    norm_t = float(np.linalg.norm(spec_t))
    if norm_a == 0 or norm_t == 0:
        return 0.0
    return float(np.dot(spec_a, spec_t) / (norm_a * norm_t))


@pytest.mark.slow
def test_M4_glass_of_water_stepped():
    """50 paired exposures (glass + water) over 10 sim-min, then glass-only
    test for 30 sim-sec → AudioIO output spectral cosine with target
    template ≥ acceptance.toml [M4].cosine_min."""
    acceptance = _load_acceptance()
    cosine_min = acceptance["M4"]["cosine_min"]

    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=8192, n_nodes_max=4096,
        box_size=(60.0, 60.0, 60.0),
        rng_seed=42,
        # Plans A, B enabled for growth + plasticity
        lambda_dec_mol=0.001, r_strengthen=10.0,
        emit_band_ratios=(0.08, 1.0, 12.5),
        mol_fusion_enabled=True,
        stdp_enabled=True,
        tau_LTP=0.020, delta_LTP=1.0, delta_LTD=0.5,
        r_bridge=5.0,
        synaptic_transmission_strength=0.5,
        synaptic_transmission_threshold=5.0,
        # Audio + video I/O
        audio_io_enabled=True,
        video_io_enabled=True,
    )
    w = World(cfg)
    from agent.audio_io import AudioIO
    from agent.video_io import VideoIO
    audio_io = AudioIO(rng=np.random.default_rng(42))
    video_io = VideoIO(rng=np.random.default_rng(42))
    loop = AgentLoop(w, audio_io=audio_io, video_io=video_io)

    glass_img = _synthesize_glass_image()
    water_template = _synthesize_water_audio(0.5)  # 0.5-sec template

    # Training: 50 pairs, ~12 sim-sec each, 10 sim-min total
    for pair_idx in range(50):
        # Show glass (write frame to video buffer once)
        glass_rgb = np.stack([glass_img, glass_img, glass_img], axis=-1).astype(np.uint8)
        video_io._write_frame_buffer(glass_rgb)
        # Hear water (write 5 sec of water audio to audio buffer)
        water_audio = _synthesize_water_audio(5.0)
        audio_io._write_input_buffer(water_audio)
        # Run substrate for ~12 sim-sec
        n_ticks = int(12.0 / cfg.dt)
        for _ in range(n_ticks):
            loop.step(cfg.dt)

    # Test phase: glass only (no audio input), 30 sim-sec
    glass_rgb = np.stack([glass_img, glass_img, glass_img], axis=-1).astype(np.uint8)
    video_io._write_frame_buffer(glass_rgb)
    n_test_ticks = int(30.0 / cfg.dt)
    for _ in range(n_test_ticks):
        loop.step(cfg.dt)

    # Read audio output buffer
    n_out = audio_io._output_write_pos - audio_io._output_read_pos
    audio_out = audio_io._read_output_buffer(max(n_out, 1))

    cosine = _spectral_cosine(audio_out, water_template)
    print(f"M4: spectral cosine = {cosine:.3f}, threshold = {cosine_min}")
    assert cosine >= cosine_min, (
        f"M4: spectral cosine {cosine:.3f} below threshold {cosine_min}"
    )
```

- [ ] **Step 7.2: Run M4**

```bash
uv run pytest tests/test_agent_m4_glass_of_water.py -v -s --override-ini="addopts="
```

This is a 7-10 wall-min CPU-bound run. Capture printed cosine.

**If it fails:**
- baseline cosine < 0.5: substrate physics didn't form bridges between video and audio ports during training. Likely tuning issue. **One tuning pass:** raise `delta_LTP` from 1.0 to 2.0; widen `r_bridge` from 5.0 to 8.0; shorten training pair to 6 sim-sec each (60 pairs in 6 sim-min instead of 12 sim-sec × 50). Re-run.
- After one tuning pass still < 0.5: BLOCKED. Document measurements, mark with `@pytest.mark.xfail(strict=True, reason=...)` and ship Plan E with M5 + I5 + RA1-5 as the load-bearing acceptance.

- [ ] **Step 7.3: Commit**

If passing:
```
test(agent): M4 — glass-of-water demo (slow, headline)

50 paired exposures (synthetic glass + 3-tone "water" signature) over
10 sim-min training; then glass-only test for 30 sim-sec; AudioIO
output spectral cosine with target ≥ 0.5.

Final cosine: <X>. Headline integration test for the entire baby-brain
foundation.
```

If xfailed:
```
test(agent): M4 — xfail until substrate read-out tuning

50 paired exposures + glass-only test produced cosine = <X> (need ≥ 0.5).
After one tuning pass with widened r_bridge and increased delta_LTP,
cosine = <Y>. Marked xfail(strict=True) so the test runs and reports;
when a future Plan E.5 (read-out tuning) makes it pass, strict=True
alerts us to remove the marker.

Plan E's other acceptance (RA1-5, I5, M5, AL1-3) remain load-bearing
and pass.
```

---

## Task 8: M5 stepped test — reward shaping (slow, headline)

**Files:**
- Create: `tests/test_agent_m5_reward_shaping.py`

- [ ] **Step 8.1: Write the test**

The structure: two parallel runs (targeted vs random reward), 100 trials each, 5 seeds. After 100 trials, baseline phase (no input) for 10 sim-sec. Compare output cosines between conditions; assert targeted-mean > random-mean + margin (bootstrap 95% CI lower bound).

Full implementation per spec §8.2. The implementer writes the n=5 seed loop, the bootstrap CI, and the threshold comparison.

- [ ] **Step 8.2: Run M5**

10-30 wall-min CPU. Capture printed targeted-vs-random margin.

**If it fails:**
- One tuning pass: increase `delta_LTP`, widen `r_bridge`, raise `synaptic_transmission_strength`, double the n_trials to 200.
- If still failing: BLOCKED, mark xfail with reason, ship Plan E.

- [ ] **Step 8.3: Commit**

(Same pass/xfail pattern as M4.)

---

## Task 9: AgentLoop real-time mode + AL3 smoke (slow)

**Files:**
- Modify: `agent/loop.py` (implement `start_realtime` / `stop_realtime`)
- Create: `tests/test_agent_realtime_smoke.py`

- [ ] **Step 9.1: Write AL3 test**

```python
"""AL3 — real-time mode smoke test (slow)."""
import time
import pytest
import numpy as np
from world.config import WorldConfig
from world.state import World
from agent.loop import AgentLoop


@pytest.mark.slow
def test_AL3_realtime_smoke():
    """start_realtime → 5 wall-sec → stop_realtime cleanly. Substrate
    thread joined; vibration count > 0 (something happened); no exceptions."""
    w = World(WorldConfig(
        n_initial_vibrations=80, n_vibrations_max=512,
        box_size=(60.0, 60.0, 60.0),
        agent_dt_realtime_ms=17,
        rng_seed=42,
    ))
    loop = AgentLoop(w)
    loop.start_realtime()
    try:
        time.sleep(5.0)
    finally:
        loop.stop_realtime()
    assert w.t > 0.0, "AL3: substrate thread did not advance world time"
    assert int(w.s_alive.sum()) > 0, "AL3: no vibrations alive after run"
```

- [ ] **Step 9.2: Implement `start_realtime` / `stop_realtime`**

```python
def start_realtime(self) -> None:
    if self._realtime_running:
        return
    import threading
    dt = self.world.config.dt
    sleep_s = self.world.config.agent_dt_realtime_ms / 1000.0
    self._realtime_running = True

    def _loop():
        while self._realtime_running:
            t0 = time.perf_counter()
            self.step(dt)
            elapsed = time.perf_counter() - t0
            remaining = sleep_s - elapsed
            if remaining > 0:
                time.sleep(remaining)

    self._realtime_thread = threading.Thread(target=_loop, daemon=True)
    self._realtime_thread.start()

def stop_realtime(self) -> None:
    self._realtime_running = False
    if self._realtime_thread is not None:
        self._realtime_thread.join(timeout=2.0)
        self._realtime_thread = None
```

(Add `import time` at the top of `agent/loop.py`.)

- [ ] **Step 9.3: Run + commit**

```
feat(agent): Plan E Task 9 — AgentLoop real-time mode + AL3 smoke

start_realtime spawns a daemon substrate thread that calls step(dt)
with overshoot-compensated sleep. AL3 runs 5 wall-sec, asserts world
time advanced and vibrations are alive. Real-time mode is for the
live demo (Task 10) and any future stress tests.
```

---

## Task 10: Demo CLI (`python -m agent.demo --m4`)

**Files:**
- Create: `agent/demo.py`
- Create: `tests/fixtures/water.wav` (~50 KB real WAV — generated synthetically by ffmpeg or sox if no real recording is available)

- [ ] **Step 10.1: Implement `agent/demo.py`**

CLI entry point. Constructs World + AudioIO (real device if available, falls back to synthetic source) + VideoIO (real webcam if available) + RewardChannel + AgentLoop in real-time mode. Loads `tests/fixtures/water.wav` for training audio. Runs forever; ctrl-C exits cleanly.

```python
"""Plan E — live demo CLI entry point.

Usage:
    python -m agent.demo --m4
    python -m agent.demo --m4 --dry-run  (synthetic sources, no real devices)
"""
import argparse
import sys
import time

import numpy as np

from world.config import WorldConfig
from world.state import World
from agent.audio_io import AudioIO
from agent.video_io import VideoIO
from agent.reward import RewardChannel
from agent.loop import AgentLoop


def m4_demo(dry_run: bool = False):
    cfg = WorldConfig(
        n_initial_vibrations=0, n_vibrations_max=8192, n_nodes_max=4096,
        box_size=(60.0, 60.0, 60.0),
        # ... full M4 hyperparameters per Task 7 ...
    )
    w = World(cfg)
    audio_io = AudioIO()
    video_io = VideoIO()
    rc = RewardChannel()
    loop = AgentLoop(w, audio_io=audio_io, video_io=video_io, reward=rc)

    if not dry_run:
        try:
            audio_io.start()
            video_io.start()
        except Exception as e:
            print(f"Could not open real devices: {e}", file=sys.stderr)
            print("Re-run with --dry-run to use synthetic sources.", file=sys.stderr)
            return 1

    loop.start_realtime()
    print("Demo running. Ctrl-C to stop.")
    try:
        while True:
            time.sleep(1.0)
            print(f"t={w.t:.2f} sim-sec, vibrations={int(w.s_alive.sum())}, "
                  f"nodes={w.k_count}")
    except KeyboardInterrupt:
        pass
    finally:
        loop.stop_realtime()
        if not dry_run:
            audio_io.stop()
            video_io.stop()
    return 0


def main():
    parser = argparse.ArgumentParser(prog="agent.demo")
    parser.add_argument("--m4", action="store_true", help="Run the M4 glass-of-water demo")
    parser.add_argument("--dry-run", action="store_true", help="Synthetic sources, no real devices")
    args = parser.parse_args()
    if args.m4:
        sys.exit(m4_demo(dry_run=args.dry_run))
    parser.print_help()


if __name__ == "__main__":
    main()
```

- [ ] **Step 10.2: Generate `tests/fixtures/water.wav`**

If no real recording is available, generate a synthetic placeholder using ffmpeg or numpy + scipy.io.wavfile:

```python
import numpy as np
from scipy.io import wavfile
sr = 16000
t = np.arange(sr * 1.0) / sr  # 1 second
audio = (np.sin(2 * np.pi * 500 * t) + np.sin(2 * np.pi * 1000 * t) +
         np.sin(2 * np.pi * 1500 * t)) * 0.3
wavfile.write("tests/fixtures/water.wav",
              sr, (audio * 32767).astype(np.int16))
```

The fixture is for the demo, not load-bearing for tests. Real users replace it with an actual recording later.

- [ ] **Step 10.3: Smoke test the CLI**

```bash
uv run python -m agent.demo --help
uv run python -m agent.demo --m4 --dry-run &
sleep 5
kill %1
```

Expected: prints status lines, ctrl-C-equivalent (kill) exits cleanly.

- [ ] **Step 10.4: Commit**

```
feat(agent): Plan E Task 10 — demo CLI + water.wav fixture

python -m agent.demo --m4 runs the live demo against real audio
+ webcam devices (or synthetic sources with --dry-run). Loads
tests/fixtures/water.wav for the training-phase audio. Prints
periodic status until ctrl-C.

The water.wav fixture is a placeholder — synthetic 3-tone signature
matching the test target. Real users replace it with an actual
'water' recording later.
```

---

## Task 11: REWARD-R1 dashboard amendment migration

**Files:**
- Create: `db/migrations/0009_planE_reward_orchestrator_amendment.sql`
- Modify: `Makefile`

- [ ] **Step 11.1: Migration**

Pattern matches `0008_planD_video_io_amendment.sql`. INSERT REWARD-R1 row with description covering: tristate k_reward_polarity, asymmetric STDP swap, RewardChannel API, AgentLoop three modes. UPDATE binds merge SHA via parameterised psql variable.

- [ ] **Step 11.2: Makefile target**

`db-migrate-planE-mark-implemented MERGE_SHA=<sha>` matching prior migrations.

- [ ] **Step 11.3: Suite check**

```bash
uv run pytest -q -m "not slow"
```

Expected: 267 passed (or whatever Task 6 ended at), 14 deselected + slow M4/M5/AL3 added.

- [ ] **Step 11.4: Commit**

```
feat(infra): Plan E Task 11 — REWARD-R1 amendment migration

Checked-in migration + Makefile target, same pattern as Plan A.5,
Plan B, Plan C, Plan D. Run after merge:
    make db-migrate-planE-mark-implemented MERGE_SHA=<sha>

Plan E implementation complete. Final code review next, then merge
to main. After Plan E lands, the baby-brain foundation is
operationally complete — the agent can listen, watch, learn
associations, and speak; reward shapes its output.
```

---

## Plan E complete

After Task 11, the original baby-brain foundation (Plans A through E) is operationally complete. Verify final state:

```bash
uv run pytest -q -m "not slow"   # ~267 expected
uv run pytest tests/test_agent_*.py tests/test_reward_*.py -v
git log --oneline feat/baby-brain-plan-E   # ~11 commits
```

**Next plans:**
- **Plan F** — Brain checkpoint / resume. Extend snapshot persistence to handle audio/video buffers + the full agent state, so M4 demos don't need to retrain from scratch each time.
- **Plan G** — End-to-end M4 + M5 demo on real hardware. The headline that all of A-F build toward.

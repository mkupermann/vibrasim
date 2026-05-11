# Flux Substrate F1a — Binding Mechanism + T3 Crystallization

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the single binding rule from spec §3 + the `Node` structures container from spec §5.4, sufficient to make Phase-1 test T3 (crystallization at cold zones) pass. No bridges, no plasticity, no decay — those are F1b.

**Architecture:** Free vibrations within distance `r` and matching frequency may bind into a `Node` with probability `sigmoid(α * pred_coherence + β * (T_crit - T_local))`. Binding is exothermic: a fraction `η` of total binding energy is exported as heat; the rest stays in the new node. Quanta consumed by binding leave the `Quanta` pool. Nodes accumulate at cold zones (low T) because the rule gates them by `T_crit - T_local`. T3 verifies this preference geometrically: more than 5× as many nodes form in the upper (cold) half of the cube as in the lower (hot) half.

**Tech Stack:** Python 3.13, numpy (already a dep), pytest. No new dependencies.

**Spec reference:** `docs/superpowers/specs/2026-05-10-flux-substrate-design.md` — read §3 (binding formula + conservation), §5.4 (binding & structures, F1a portion only — bridges and structure-flux are F1b), §7 T3 (acceptance contract).

**Estimated wallclock:** 1–2 weeks solo.

**Acceptance contract:**
- `uv run pytest tests/flux/test_crystallization.py -v` passes (T3)
- `uv run pytest tests/flux/test_conservation.py -v` still passes (T1, with binding active and η heat export accounted for)
- All 33 F0 flux tests still pass
- All 382 legacy tests still pass

---

## What F1a deliberately defers to F1b

| Concept | Status in F1a | Where it lands |
|---|---|---|
| Bridges (node-to-node weighted edges) | NOT implemented | F1b |
| Structure-flux (free vibrations passing through nodes) | NOT implemented | F1b |
| Bridge plasticity (Hebbian strengthening / decay) | NOT implemented | F1b |
| Node dissociation when bridges fail | NOT implemented | F1b |
| `pred_coherence` as windowed cross-correlation | Simplified to frequency-match within ε in F1a | full version in F2 when cochlea brings multi-frequency input |
| T4 (decay) acceptance test | not in scope | F1b |
| T2 (Bénard) acceptance test | not in scope | F1c |

Single-frequency injection (T3's setup) makes the simplified coherence trivially 1.0 for all pairs. The rule reduces to pure temperature-gated binding for T3. This is the right scope for F1a.

---

## File structure (locked decisions)

New files:

| Path | Responsibility |
|---|---|
| `world/flux/structures.py` | `Nodes` SoA container — pre-allocated arrays for up to `MAX_NODES` bound nodes. F1a uses only the Node level; bridges added in F1b. |
| `world/flux/binding.py` | The single binding rule: pair search within `r`, coherence + temperature gate, binding event (consume quanta → create node + export heat). |
| `tests/flux/test_structures.py` | Nodes container unit tests. |
| `tests/flux/test_binding.py` | Pair-search, coherence, probability, binding event unit tests. |
| `tests/flux/test_crystallization.py` | T3 integration test (the acceptance test for F1a). |

Modified files:

| Path | What changes |
|---|---|
| `world/flux/audit.py` | `EnergyAuditor` learns about a `Nodes` reference; conservation now includes `E_in_nodes`. New helper `record_binding_heat`. |
| `world/flux/dynamics.py` | `tick` gets a new step between motion and absorption: attempt binding. New keyword arg `nodes: Nodes \| None` and `binding_cfg: BindingConfig \| None`. F0-style call (no nodes) still works. |
| `world/flux/__init__.py` | Re-export `Nodes`, `BindingConfig`, and new helpers. |
| `docs/flux/phase-log.md` | F1a start + close entries. |
| `README.md` | One-line status update on F1a in the "Two substrates" section. |

---

## Task 1: F1a start — phase-log entry

**Files:**
- Modify: `docs/flux/phase-log.md`

- [ ] **Step 1: Append F1a-start entry to `docs/flux/phase-log.md`**

Append at the end of the file:

```markdown

## 2026-05-11 — F1a start

- F0 closed: 33/33 flux tests + 382 legacy tests + T1 conservation green; commits `09f9488..4d6d1b0`.
- F1a target: T3 (crystallization at cold zones) passes.
  - Binding rule per spec §3: `p_bind = sigmoid(α * pred_coherence + β * (T_crit - T_local))`
  - `pred_coherence` simplified to frequency-equality within ε for F1a (full cross-correlation deferred to F2 when cochlea brings multi-frequency input).
  - Binding is exothermic: fraction `η` of binding energy exported as heat.
  - No bridges, no plasticity, no decay in F1a — those land in F1b.
- Plan: `docs/superpowers/plans/2026-05-11-flux-substrate-F1a.md`.
- Estimated 1–2 weeks solo.
```

- [ ] **Step 2: Commit**

```bash
git add docs/flux/phase-log.md
git commit -m "flux F1a start: phase-log entry

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: Nodes SoA container

**Files:**
- Create: `world/flux/structures.py`
- Create: `tests/flux/test_structures.py`

- [ ] **Step 1: Write failing test `tests/flux/test_structures.py`**

```python
"""Tests for Nodes SoA container — F1a level (no bridges yet)."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.structures import Nodes


def test_nodes_empty_on_init():
    n = Nodes(max_nodes=100)
    assert n.max_nodes == 100
    assert n.n_alive() == 0
    assert n.alive.shape == (100,)
    assert n.alive.dtype == np.bool_
    assert n.pos.shape == (100, 3)
    assert n.pos.dtype == np.float64
    assert n.energy.shape == (100,)
    assert n.energy.dtype == np.float64
    assert n.freq.shape == (100,)
    assert n.born_tick.shape == (100,)
    assert n.born_tick.dtype == np.int64


def test_nodes_add_returns_slot_and_writes_fields():
    n = Nodes(max_nodes=10)
    slot = n.add(pos=(1.5, 2.5, 3.5), energy=2.0, freq=440.0,
                 born_tick=42)
    assert 0 <= slot < 10
    assert n.alive[slot]
    assert n.pos[slot, 0] == 1.5
    assert n.pos[slot, 1] == 2.5
    assert n.pos[slot, 2] == 3.5
    assert n.energy[slot] == 2.0
    assert n.freq[slot] == 440.0
    assert n.born_tick[slot] == 42
    assert n.n_alive() == 1


def test_nodes_total_energy_sums_alive_only():
    n = Nodes(max_nodes=5)
    n.add(pos=(0, 0, 0), energy=1.0, freq=100.0, born_tick=0)
    n.add(pos=(0, 0, 0), energy=2.0, freq=100.0, born_tick=0)
    s = n.add(pos=(0, 0, 0), energy=99.0, freq=100.0, born_tick=0)
    n.remove(s)
    assert n.total_energy() == 3.0


def test_nodes_remove_marks_slot_free():
    n = Nodes(max_nodes=5)
    s0 = n.add(pos=(0, 0, 0), energy=1.5, freq=100.0, born_tick=0)
    released = n.remove(s0)
    assert released == 1.5
    assert not n.alive[s0]
    assert n.n_alive() == 0


def test_nodes_add_returns_minus_one_when_full():
    n = Nodes(max_nodes=2)
    n.add(pos=(0, 0, 0), energy=1.0, freq=100.0, born_tick=0)
    n.add(pos=(0, 0, 0), energy=1.0, freq=100.0, born_tick=0)
    full = n.add(pos=(0, 0, 0), energy=1.0, freq=100.0, born_tick=0)
    assert full == -1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/flux/test_structures.py -v`
Expected: `ModuleNotFoundError: No module named 'world.flux.structures'`

- [ ] **Step 3: Implement `world/flux/structures.py`**

```python
"""Nodes — SoA container for bound structures.

A Node is a bound configuration of one or more vibrations. It carries
the summed energy of its constituent vibrations (minus the η heat
exported during binding). Nodes persist while flux passes through them
(F1b mechanic; F1a nodes just accumulate).

Bridges (node-to-node weighted edges) are added in F1b. F1a stores
nodes only.
"""
from __future__ import annotations
from typing import Sequence
import numpy as np


class Nodes:
    """Pre-allocated SoA container for bound nodes.

    Slot reuse identical to `Quanta`: lowest-index free slot wins on
    `add`; `_next_search` cursor advances past the just-filled slot.

    Each node carries position, energy, dominant frequency, and the
    tick at which it was born (for F1b decay accounting).
    """

    def __init__(self, max_nodes: int):
        self.max_nodes = int(max_nodes)
        N = self.max_nodes
        self.pos = np.zeros((N, 3), dtype=np.float64)
        self.energy = np.zeros(N, dtype=np.float64)
        self.freq = np.zeros(N, dtype=np.float64)
        self.born_tick = np.zeros(N, dtype=np.int64)
        self.alive = np.zeros(N, dtype=np.bool_)
        self._next_search = 0

    def n_alive(self) -> int:
        return int(self.alive.sum())

    def total_energy(self) -> float:
        return float(self.energy[self.alive].sum())

    def add(self, pos: Sequence[float], energy: float, freq: float,
            born_tick: int) -> int:
        N = self.max_nodes
        for i in range(N):
            j = (self._next_search + i) % N
            if not self.alive[j]:
                self.pos[j] = pos
                self.energy[j] = float(energy)
                self.freq[j] = float(freq)
                self.born_tick[j] = int(born_tick)
                self.alive[j] = True
                self._next_search = (j + 1) % N
                return j
        return -1

    def remove(self, slot: int) -> float:
        if not self.alive[slot]:
            return 0.0
        e = float(self.energy[slot])
        self.alive[slot] = False
        self.energy[slot] = 0.0
        self._next_search = min(self._next_search, slot)
        return e
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/flux/test_structures.py -v`
Expected: all 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add world/flux/structures.py tests/flux/test_structures.py
git commit -m "flux F1a task 2: Nodes SoA container

Bound-structure storage paralleling Quanta. Same SoA + slot-reuse
pattern. F1a uses Node level only; bridges deferred to F1b.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: Predictive coherence (simplified F1a version)

**Files:**
- Create: `world/flux/binding.py`
- Create: `tests/flux/test_binding.py`

- [ ] **Step 1: Write failing test `tests/flux/test_binding.py`**

```python
"""Tests for binding rule — F1a level (no bridges, no plasticity)."""
from __future__ import annotations
import numpy as np
import pytest

from world.flux.binding import pred_coherence


def test_pred_coherence_returns_one_for_equal_frequencies():
    # F1a simplification: pred_coherence is 1.0 if |f_a - f_b| < eps,
    # else 0.0. Full cross-correlation deferred to F2.
    assert pred_coherence(200.0, 200.0, eps=1.0) == 1.0
    assert pred_coherence(200.5, 199.5, eps=1.0) == 1.0


def test_pred_coherence_returns_zero_for_different_frequencies():
    assert pred_coherence(200.0, 300.0, eps=1.0) == 0.0
    assert pred_coherence(100.0, 100.5, eps=0.1) == 0.0


def test_pred_coherence_at_boundary_is_zero():
    # Exactly at eps the difference is not strictly < eps → 0.0
    assert pred_coherence(200.0, 201.0, eps=1.0) == 0.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/flux/test_binding.py -v -k pred_coherence`
Expected: `ImportError: cannot import name 'pred_coherence' from 'world.flux.binding'`

- [ ] **Step 3: Create `world/flux/binding.py` with `pred_coherence`**

```python
"""Binding mechanism — the single rule that replaces 6 engineered levels.

Per spec §3, a bond forms between two or more vibrations within distance
`r` and time window `τ` with probability:

    p_bind = sigmoid(α * pred_coherence + β * (T_crit - T_local))

In F1a this is implemented in its scope-minimal form:
- `pred_coherence` is frequency-equality within `eps` (1.0 or 0.0), not
  the full windowed cross-correlation. T3 uses single-frequency
  injection, so this collapses trivially to 1.0 for all candidate pairs.
  The full cross-correlation version arrives in F2 when the cochlea
  brings multi-frequency input.
- Binding consumes quanta (frees their slots) and creates one Node.
- Binding is exothermic: a fraction `η` of total binding energy is
  exported as heat (added to the auditor).
- F1a binds in groups of exactly 2 per event. F1b will generalise.
"""
from __future__ import annotations
import numpy as np


def pred_coherence(freq_a: float, freq_b: float,
                   eps: float = 1.0) -> float:
    """Simplified F1a coherence: 1.0 iff |freq_a - freq_b| < eps.

    The spec defines pred_coherence as a windowed temporal
    cross-correlation of frequency-amplitude trajectories. F1a's
    single-frequency injection makes all pairs trivially coherent;
    the binary form here matches that regime exactly. Full version
    arrives in F2 with multi-frequency cochlea input.
    """
    return 1.0 if abs(freq_a - freq_b) < eps else 0.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/flux/test_binding.py -v -k pred_coherence`
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add world/flux/binding.py tests/flux/test_binding.py
git commit -m "flux F1a task 3: pred_coherence (simplified F1a form)

Frequency-equality within eps as F1a stand-in. Full windowed cross-
correlation deferred to F2 (cochlea + multi-frequency input).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: Pair search within distance r

**Files:**
- Modify: `world/flux/binding.py` (append `find_pairs_within`)
- Modify: `tests/flux/test_binding.py` (append tests)

- [ ] **Step 1: Append failing tests for `find_pairs_within` to `tests/flux/test_binding.py`**

```python
from world.flux.quantum import Quanta
from world.flux.binding import find_pairs_within


def test_find_pairs_within_returns_empty_for_zero_or_one_quanta():
    q = Quanta(max_quanta=10)
    pairs = find_pairs_within(q, r=2.0)
    assert pairs.shape == (0, 2)
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    pairs = find_pairs_within(q, r=2.0)
    assert pairs.shape == (0, 2)


def test_find_pairs_within_returns_close_pairs():
    q = Quanta(max_quanta=10)
    q.add(pos=(0.0, 0.0, 0.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=1.0)
    q.add(pos=(1.0, 0.0, 0.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=1.0)
    q.add(pos=(5.0, 0.0, 0.0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=1.0)
    pairs = find_pairs_within(q, r=2.0)
    # Only (0, 1) is within r=2.0 of each other; slot 2 is far away
    assert pairs.shape == (1, 2)
    assert {tuple(p) for p in pairs} == {(0, 1)}


def test_find_pairs_within_ignores_dead_slots():
    q = Quanta(max_quanta=10)
    s0 = q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    s1 = q.add(pos=(0.5, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    q.remove(s0)
    pairs = find_pairs_within(q, r=2.0)
    assert pairs.shape == (0, 2)


def test_find_pairs_within_returns_indices_ordered_low_high():
    q = Quanta(max_quanta=10)
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    q.add(pos=(0.5, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    pairs = find_pairs_within(q, r=2.0)
    # Should return (0, 1), not (1, 0)
    assert pairs[0, 0] < pairs[0, 1]


def test_find_pairs_within_no_pair_at_exact_r():
    """Distance exactly r → not within r (strict inequality)."""
    q = Quanta(max_quanta=10)
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    q.add(pos=(2.0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1, energy=1.0)
    pairs = find_pairs_within(q, r=2.0)
    assert pairs.shape == (0, 2)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/flux/test_binding.py -v -k find_pairs`
Expected: 5 tests FAIL with `ImportError: cannot import name 'find_pairs_within'`

- [ ] **Step 3: Append `find_pairs_within` to `world/flux/binding.py`**

```python
from world.flux.quantum import Quanta


def find_pairs_within(quanta: Quanta, r: float) -> np.ndarray:
    """Return shape (M, 2) int array of (i, j) pairs with i<j where the
    two alive quanta are within Euclidean distance r of each other.

    Naive O(N^2/2) algorithm — fine at F1a scale (≤ 1000 alive quanta).
    A KD-tree or cell-list optimisation is the F1b/F2 concern.
    """
    alive_idx = np.where(quanta.alive)[0]
    n = alive_idx.size
    if n < 2:
        return np.zeros((0, 2), dtype=np.int64)

    pos = quanta.pos[alive_idx]  # (n, 3)
    # Pairwise squared distances
    diff = pos[:, None, :] - pos[None, :, :]  # (n, n, 3)
    d2 = (diff * diff).sum(axis=-1)  # (n, n)
    r2 = r * r

    # Upper-triangle mask, strictly within r (d2 < r2)
    i_local, j_local = np.where(np.triu(d2 < r2, k=1))
    if i_local.size == 0:
        return np.zeros((0, 2), dtype=np.int64)
    pairs = np.stack([alive_idx[i_local], alive_idx[j_local]], axis=1)
    return pairs.astype(np.int64)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/flux/test_binding.py -v -k find_pairs`
Expected: 5 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add world/flux/binding.py tests/flux/test_binding.py
git commit -m "flux F1a task 4: find_pairs_within (naive O(N^2/2))

Pair search returning (i, j) with i<j for alive quanta within r.
Strict inequality on distance. Naive algorithm acceptable at F1a
scale; KD-tree/cell-list deferred to F1b/F2 if profiling shows it
matters.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: Binding probability function

**Files:**
- Modify: `world/flux/binding.py` (append `binding_probability`)
- Modify: `tests/flux/test_binding.py` (append tests)

- [ ] **Step 1: Append failing tests to `tests/flux/test_binding.py`**

```python
from world.flux.binding import binding_probability, BindingConfig


def test_binding_probability_is_high_in_cold_zones():
    cfg = BindingConfig(alpha=4.0, beta=4.0, T_crit=1.0)
    # Cold zone: T_local << T_crit → (T_crit - T_local) is large positive
    p = binding_probability(pred_coh=1.0, T_local=0.0, cfg=cfg)
    assert p > 0.9


def test_binding_probability_is_low_in_hot_zones():
    cfg = BindingConfig(alpha=4.0, beta=4.0, T_crit=1.0)
    # Hot zone: T_local >> T_crit
    p = binding_probability(pred_coh=1.0, T_local=10.0, cfg=cfg)
    assert p < 0.1


def test_binding_probability_is_low_when_coherence_is_zero():
    cfg = BindingConfig(alpha=4.0, beta=4.0, T_crit=1.0)
    # Cold zone but incoherent: alpha*0 + beta*1 = 4 → sigmoid(4)≈0.98
    # Wait — beta*(T_crit - T_local) = 4*(1-0) = 4. With coh=0 still
    # large positive. Let's test the OPPOSITE: very hot AND incoherent
    p = binding_probability(pred_coh=0.0, T_local=10.0, cfg=cfg)
    assert p < 0.001


def test_binding_probability_at_T_crit_with_coh_zero_is_one_half():
    """At T_local == T_crit and pred_coh == 0, sigmoid(0) = 0.5."""
    cfg = BindingConfig(alpha=1.0, beta=1.0, T_crit=2.0)
    p = binding_probability(pred_coh=0.0, T_local=2.0, cfg=cfg)
    np.testing.assert_allclose(p, 0.5, atol=1e-9)


def test_binding_config_defaults_are_sane():
    cfg = BindingConfig()
    assert cfg.alpha > 0
    assert cfg.beta > 0
    assert cfg.T_crit > 0
    assert 0.0 <= cfg.eta < 1.0
    assert cfg.r > 0
    assert 0.0 <= cfg.coherence_eps
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/flux/test_binding.py -v -k "binding_probability or binding_config"`
Expected: 5 tests FAIL with `ImportError: cannot import name 'binding_probability'`

- [ ] **Step 3: Append `BindingConfig` + `binding_probability` to `world/flux/binding.py`**

```python
from dataclasses import dataclass


@dataclass
class BindingConfig:
    """Tunable parameters of the single binding rule (spec §3).

    Defaults are F1a starting values — calibration sweeps live in the
    F1a task 9 phase-log notes once T3 results are in.
    """
    alpha: float = 4.0          # gain on coherence term
    beta: float = 4.0           # gain on temperature gap
    T_crit: float = 5.0         # critical temperature for binding
    eta: float = 0.1            # heat-export fraction (η ∈ [0, 1))
    r: float = 1.5              # binding radius (Euclidean)
    coherence_eps: float = 1.0  # frequency-equality tolerance (F1a)


def binding_probability(pred_coh: float, T_local: float,
                         cfg: BindingConfig) -> float:
    """Compute p_bind = sigmoid(α * pred_coh + β * (T_crit - T_local)).

    Returns a float in (0, 1).
    """
    x = cfg.alpha * pred_coh + cfg.beta * (cfg.T_crit - T_local)
    # Stable sigmoid
    if x >= 0:
        return 1.0 / (1.0 + np.exp(-x))
    else:
        ex = np.exp(x)
        return ex / (1.0 + ex)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/flux/test_binding.py -v -k "binding_probability or binding_config"`
Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add world/flux/binding.py tests/flux/test_binding.py
git commit -m "flux F1a task 5: BindingConfig + binding_probability

Sigmoid gate on alpha*coherence + beta*(T_crit - T_local) per
spec §3. Stable sigmoid in both branches.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: Binding event — consume quanta, create node, export heat

**Files:**
- Modify: `world/flux/binding.py` (append `attempt_binding`)
- Modify: `tests/flux/test_binding.py` (append tests)

- [ ] **Step 1: Append failing tests to `tests/flux/test_binding.py`**

```python
from world.flux.structures import Nodes
from world.flux.grid import Grid
from world.flux.binding import attempt_binding


def test_attempt_binding_creates_node_at_centroid_when_temperature_low():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=1.0)
    cfg = BindingConfig(alpha=10.0, beta=10.0, T_crit=1.0,
                         eta=0.1, r=2.0)
    # Two coherent quanta in a cold voxel
    q.add(pos=(5.0, 5.0, 5.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    q.add(pos=(5.5, 5.0, 5.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    # T_local around (5,5,5) is 0 (no smoothing of any density)
    rng = np.random.default_rng(0)
    heat = attempt_binding(quanta=q, nodes=n, grid=g,
                            cfg=cfg, tick_index=0, rng=rng)
    # Both quanta should have bound (high p) into one node
    assert n.n_alive() == 1
    # Centroid at (5.25, 5, 5)
    np.testing.assert_allclose(n.pos[0], [5.25, 5.0, 5.0])
    # Energy: total in = 2.0; heat = 0.1 * 2.0 = 0.2; node holds 1.8
    np.testing.assert_allclose(n.energy[0], 1.8, atol=1e-12)
    np.testing.assert_allclose(heat, 0.2, atol=1e-12)
    # Quanta slots freed
    assert q.n_alive() == 0


def test_attempt_binding_does_not_bind_in_hot_zones():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    cfg = BindingConfig(alpha=4.0, beta=10.0, T_crit=1.0,
                         eta=0.1, r=2.0)
    q.add(pos=(5.0, 5.0, 5.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    q.add(pos=(5.5, 5.0, 5.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    # Force a hot temperature at that voxel
    g.T[5, 5, 5] = 100.0
    rng = np.random.default_rng(0)
    heat = attempt_binding(quanta=q, nodes=n, grid=g,
                            cfg=cfg, tick_index=0, rng=rng)
    # Hot zone → p_bind ≈ 0 → no binding
    assert n.n_alive() == 0
    assert heat == 0.0
    assert q.n_alive() == 2


def test_attempt_binding_skips_frequency_mismatched_pairs():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    cfg = BindingConfig(alpha=10.0, beta=10.0, T_crit=1.0,
                         eta=0.1, r=2.0, coherence_eps=1.0)
    q.add(pos=(5.0, 5.0, 5.0), vel=(0, 0, 0), freq=100,
          polarity=1, energy=1.0)
    q.add(pos=(5.5, 5.0, 5.0), vel=(0, 0, 0), freq=500,
          polarity=1, energy=1.0)
    rng = np.random.default_rng(0)
    heat = attempt_binding(quanta=q, nodes=n, grid=g,
                            cfg=cfg, tick_index=0, rng=rng)
    # Frequencies differ by 400 >> eps=1 → coh=0; with alpha=10 and
    # beta=10, sigmoid(0 + 10*(1-0)) = sigmoid(10) ≈ 0.9999
    # — but the coherence-zero path should skip the pair entirely
    # before even computing p_bind. F1a optimisation.
    assert n.n_alive() == 0
    assert heat == 0.0
    assert q.n_alive() == 2


def test_attempt_binding_with_no_pairs_is_noop():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    cfg = BindingConfig()
    rng = np.random.default_rng(0)
    heat = attempt_binding(quanta=q, nodes=n, grid=g,
                            cfg=cfg, tick_index=0, rng=rng)
    assert heat == 0.0
    assert n.n_alive() == 0


def test_attempt_binding_sets_node_freq_to_pair_mean():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    cfg = BindingConfig(alpha=10.0, beta=10.0, T_crit=1.0,
                         eta=0.0, r=2.0, coherence_eps=2.0)
    q.add(pos=(5.0, 5.0, 5.0), vel=(0, 0, 0), freq=199,
          polarity=1, energy=1.0)
    q.add(pos=(5.5, 5.0, 5.0), vel=(0, 0, 0), freq=201,
          polarity=1, energy=1.0)
    rng = np.random.default_rng(0)
    attempt_binding(quanta=q, nodes=n, grid=g,
                    cfg=cfg, tick_index=7, rng=rng)
    assert n.n_alive() == 1
    np.testing.assert_allclose(n.freq[0], 200.0)
    assert n.born_tick[0] == 7
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/flux/test_binding.py -v -k attempt_binding`
Expected: 5 tests FAIL with `ImportError: cannot import name 'attempt_binding'`

- [ ] **Step 3: Append `attempt_binding` to `world/flux/binding.py`**

```python
from world.flux.grid import Grid
from world.flux.structures import Nodes


def attempt_binding(quanta: Quanta, nodes: Nodes, grid: Grid,
                    cfg: BindingConfig, tick_index: int,
                    rng: np.random.Generator) -> float:
    """Run one tick's binding pass.

    Finds all alive quanta pairs within distance r. For each pair:
      - skip if frequency mismatch (pred_coherence < 1.0)
      - read T_local at the pair's centroid voxel
      - compute p_bind; sample uniform → if < p_bind, BIND

    A binding event: consumes both quanta, creates one new node at the
    centroid with energy = (1 - η) * sum(quanta.energy), exports
    η * sum(quanta.energy) as heat (return value).

    Returns the total heat exported this tick (sum across all binding
    events). Caller is responsible for recording into the auditor.

    F1a only binds in PAIRS (2 quanta → 1 node). F1b will generalise.
    """
    pairs = find_pairs_within(quanta, cfg.r)
    if pairs.shape[0] == 0:
        return 0.0

    total_heat = 0.0
    # Iterate pairs; once a quantum is consumed in this tick it cannot
    # bind again, so track which slots have already participated.
    consumed = set()
    for p in pairs:
        i, j = int(p[0]), int(p[1])
        if i in consumed or j in consumed:
            continue

        # Coherence gate (F1a: frequency-equality)
        coh = pred_coherence(quanta.freq[i], quanta.freq[j],
                              eps=cfg.coherence_eps)
        if coh <= 0.0:
            continue

        # Temperature at pair centroid
        cx = 0.5 * (quanta.pos[i, 0] + quanta.pos[j, 0])
        cy = 0.5 * (quanta.pos[i, 1] + quanta.pos[j, 1])
        cz = 0.5 * (quanta.pos[i, 2] + quanta.pos[j, 2])
        ix, iy, iz = grid.pos_to_voxel((cx, cy, cz))
        T_local = float(grid.T[ix, iy, iz])

        # Binding probability
        p_bind = binding_probability(pred_coh=coh, T_local=T_local,
                                       cfg=cfg)
        # Sample
        if rng.random() >= p_bind:
            continue

        # BIND
        e_in = float(quanta.energy[i] + quanta.energy[j])
        heat = cfg.eta * e_in
        e_node = e_in - heat
        f_mean = 0.5 * (quanta.freq[i] + quanta.freq[j])
        slot = nodes.add(pos=(cx, cy, cz), energy=e_node,
                          freq=f_mean, born_tick=tick_index)
        if slot < 0:
            # Nodes buffer full; do not bind, leave quanta intact
            continue

        # Consume the two quanta
        quanta.remove(i)
        quanta.remove(j)
        consumed.add(i)
        consumed.add(j)
        total_heat += heat

    return total_heat
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/flux/test_binding.py -v`
Expected: all 18 binding tests PASS (3 coherence + 5 pair-search + 5 probability + 5 attempt_binding).

- [ ] **Step 5: Commit**

```bash
git add world/flux/binding.py tests/flux/test_binding.py
git commit -m "flux F1a task 6: attempt_binding (consume quanta -> node)

One binding pass per tick. Pair search + coherence gate + temperature
gate + probabilistic acceptance. Exothermic: eta fraction of input
energy exported as heat. F1a only binds pairs (2 quanta -> 1 node);
F1b will generalise.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: Wire binding into the tick

**Files:**
- Modify: `world/flux/dynamics.py`
- Modify: `tests/flux/test_dynamics.py` (append integration tests)

- [ ] **Step 1: Append failing test to `tests/flux/test_dynamics.py`**

```python
from world.flux.structures import Nodes
from world.flux.binding import BindingConfig


def test_tick_with_binding_creates_nodes_in_cold_zones():
    q = Quanta(max_quanta=50)
    n = Nodes(max_nodes=50)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=1.0)
    cfg = BindingConfig(alpha=10.0, beta=10.0, T_crit=1.0,
                         eta=0.1, r=2.0)
    # Place two coherent quanta near each other in a cold (empty) voxel
    q.add(pos=(5.0, 5.0, 8.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    q.add(pos=(5.5, 5.0, 8.0), vel=(0, 0, 0), freq=200,
          polarity=1, energy=1.0)
    rng = np.random.default_rng(0)
    # dt=0 so positions don't change; one binding pass
    heat = tick(q, g, dt=0.0, injector=None,
                 nodes=n, binding_cfg=cfg, rng=rng, tick_index=0)
    # heat returned from tick is now structured: cold-face export only;
    # binding heat is recorded via the rng-keyed binding return value.
    # See updated tick signature below.
    assert n.n_alive() == 1


def test_tick_without_binding_args_still_works():
    """F0-style call (no nodes, no binding) must still pass."""
    q = Quanta(max_quanta=10)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0)
    q.add(pos=(5.0, 5.0, 5.0), vel=(1.0, 0.0, 0.5),
          freq=100, polarity=1, energy=1.0)
    exported = tick(q, g, dt=0.1, injector=None)
    np.testing.assert_allclose(q.pos[0], [5.1, 5.0, 5.05])
    assert exported == 0.0
```

NOTE: This test assumes `tick` now returns a two-tuple `(exported, binding_heat)` OR keeps `exported` as the return and surfaces binding heat through a different channel. The implementation in Step 3 returns a tuple `(exported, binding_heat)`. The F0 callers (test_conservation.py) will need a one-line update in Task 9. Update the F0 tests' expectations in this task to match the new signature.

Therefore, also update the existing F0 dynamics tests to consume the new return type:

In `tests/flux/test_dynamics.py`, find these F0 lines:
```python
exported = tick(q, g, dt=0.1, injector=None)
```
and update each to:
```python
result = tick(q, g, dt=0.1, injector=None)
exported = result[0] if isinstance(result, tuple) else result
```

Actually — to keep F0 callers byte-for-byte unchanged, the cleaner design is to return a small dataclass `TickResult` with attributes `exported` and `binding_heat`, default 0.0 for `binding_heat` when no binding is configured. Then F0 callers that did `exported = tick(...)` break unless we keep returning float. Two choices:

**Option A (chosen):** Keep `tick(...) -> float` (returns exported) AND add a SECOND return slot ONLY when binding is configured. Concretely: when `nodes` is None, return `exported` (float, F0-compatible). When `nodes` is provided, return `(exported, binding_heat)` tuple.

This means F0 callers (test_conservation.py) need NO changes. New F1a callers handle the tuple.

The relevant test update is therefore just to consume the tuple form in the NEW test:

```python
def test_tick_with_binding_creates_nodes_in_cold_zones():
    # ... setup ...
    rng = np.random.default_rng(0)
    exported, binding_heat = tick(
        q, g, dt=0.0, injector=None,
        nodes=n, binding_cfg=cfg, rng=rng, tick_index=0,
    )
    assert n.n_alive() == 1
```

The `test_tick_without_binding_args_still_works` test is the regression guard — `tick` with no `nodes` returns a float as in F0.

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/flux/test_dynamics.py -v`
Expected: the 4 F0 tests still pass (unchanged); the 2 new tests FAIL with `TypeError: tick() got an unexpected keyword argument 'nodes'`.

- [ ] **Step 3: Update `world/flux/dynamics.py` to support binding**

Replace the existing `tick` function with the following (keep `_compute_density` unchanged). The `Injector` type alias stays the same.

```python
"""Per-tick orchestration.

Order of operations in one tick (spec §6, F1a subset):
1. Inject at hot floor (if injector provided)
2. Move free vibrations: pos += vel * dt
3. Absorb at cold faces → returns E_exported
4. Attempt binding (if nodes + binding_cfg provided) → returns
   binding_heat
5. Update temperature field from new density

Return value:
- If nodes is None: returns E_exported as a float (F0-compatible).
- If nodes is provided: returns (E_exported, binding_heat) tuple.

The injector closure is responsible for recording E_injected into
the auditor directly — tick does not surface it.

F1 plasticity + structure-flux still deferred to F1b.
"""
from __future__ import annotations
from typing import Callable
import numpy as np

from world.flux.quantum import Quanta
from world.flux.grid import Grid
from world.flux.boundary import absorb_cold_faces


Injector = Callable[[Quanta, Grid], float]
"""Function (quanta, grid) -> energy_injected_this_tick."""


def _compute_density(quanta: Quanta, grid: Grid) -> np.ndarray:
    """Histogram alive quanta into voxel bins → counts per voxel."""
    Lx, Ly, Lz = grid.dims
    s = grid.voxel_size
    density = np.zeros(grid.dims, dtype=np.float64)
    if quanta.n_alive() == 0:
        return density
    alive = quanta.alive
    pos = quanta.pos[alive]
    ix = np.clip((pos[:, 0] / s).astype(int), 0, Lx - 1)
    iy = np.clip((pos[:, 1] / s).astype(int), 0, Ly - 1)
    iz = np.clip((pos[:, 2] / s).astype(int), 0, Lz - 1)
    np.add.at(density, (ix, iy, iz), 1.0)
    return density


def tick(quanta: Quanta, grid: Grid, dt: float,
         injector: Injector | None,
         cold_face_delta: float = 0.5,
         *,
         nodes=None,
         binding_cfg=None,
         rng: np.random.Generator | None = None,
         tick_index: int = 0):
    """Run one tick.

    F0 mode (nodes is None): returns E_exported as a float.
    F1a mode (nodes provided): returns (E_exported, binding_heat) tuple.
    """
    # 1. Inject
    if injector is not None:
        injector(quanta, grid)

    # 2. Move
    alive = quanta.alive
    if alive.any():
        quanta.pos[alive] += quanta.vel[alive] * dt

    # 3. Absorb
    exported = absorb_cold_faces(quanta, grid, delta=cold_face_delta)

    # 4. Attempt binding (F1a)
    binding_heat = 0.0
    if nodes is not None and binding_cfg is not None:
        # Lazy import to avoid circular dependency at module load
        from world.flux.binding import attempt_binding
        rng_use = rng if rng is not None else np.random.default_rng()
        binding_heat = attempt_binding(
            quanta=quanta, nodes=nodes, grid=grid,
            cfg=binding_cfg, tick_index=tick_index, rng=rng_use,
        )

    # 5. Temperature
    density = _compute_density(quanta, grid)
    grid.update_temperature(density)

    if nodes is None:
        return exported
    return exported, binding_heat
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/flux/test_dynamics.py -v`
Expected: all 6 dynamics tests PASS (4 F0 + 2 F1a).

Also run the full flux suite:
Run: `uv run pytest tests/flux/ -v`
Expected: 51 total tests PASS (33 F0 + 18 binding/structures = 51). All F0 conservation/boundary/grid/quantum/audit tests still green.

- [ ] **Step 5: Commit**

```bash
git add world/flux/dynamics.py tests/flux/test_dynamics.py
git commit -m "flux F1a task 7: wire binding into tick

tick now accepts optional nodes + binding_cfg + rng + tick_index.
F0 callers unchanged (no nodes -> float return). F1a callers get a
(exported, binding_heat) tuple. Order in tick: inject -> move ->
absorb -> bind -> update_temperature.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 8: Auditor tracks structure energy + binding heat

**Files:**
- Modify: `world/flux/audit.py`
- Modify: `tests/flux/test_audit.py` (append tests)

- [ ] **Step 1: Append failing tests to `tests/flux/test_audit.py`**

```python
from world.flux.structures import Nodes


def test_auditor_with_nodes_includes_structure_energy_in_balance():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    a = EnergyAuditor(quanta=q, nodes=n, tol=1e-9)
    a.record_initial()
    # Inject 5 into a node
    n.add(pos=(0, 0, 0), energy=5.0, freq=100.0, born_tick=0)
    a.record_injection(5.0)
    a.check()  # Should pass: 0 + 5 == 0 (free) + 5 (node) + 0 (heat)


def test_auditor_record_binding_heat_accumulates_into_exported():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    a = EnergyAuditor(quanta=q, nodes=n, tol=1e-9)
    a.record_initial()
    # Two quanta of energy 1.0 each are bound: 1.8 into node, 0.2 heat
    a.record_injection(2.0)
    n.add(pos=(0, 0, 0), energy=1.8, freq=100.0, born_tick=0)
    a.record_binding_heat(0.2)
    a.check()  # 0 + 2 == 0 (free) + 1.8 (node) + 0.2 (heat)


def test_auditor_balance_violated_when_binding_heat_unrecorded():
    q = Quanta(max_quanta=10)
    n = Nodes(max_nodes=10)
    a = EnergyAuditor(quanta=q, nodes=n, tol=1e-9)
    a.record_initial()
    a.record_injection(2.0)
    n.add(pos=(0, 0, 0), energy=1.8, freq=100.0, born_tick=0)
    # Forgot to record the 0.2 heat -> should detect imbalance
    with pytest.raises(ConservationViolation):
        a.check()


def test_auditor_without_nodes_still_works_F0_compat():
    """F0-style auditor (no nodes) must keep working."""
    q = Quanta(max_quanta=10)
    a = EnergyAuditor(quanta=q, tol=1e-9)
    a.record_initial()
    q.add(pos=(0, 0, 0), vel=(0, 0, 0), freq=100, polarity=1,
          energy=3.0)
    a.record_injection(3.0)
    a.check()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/flux/test_audit.py -v`
Expected: 4 new tests FAIL (existing 6 still pass — auditor doesn't accept `nodes=`).

- [ ] **Step 3: Update `world/flux/audit.py`**

Replace the entire file content:

```python
"""Energy conservation audit.

Conservation law (F1a):
    E_initial + E_injected_total
    == E_in_quanta + E_in_nodes + E_exported_total + E_binding_heat_total

within tolerance `tol` × max(|E_initial + E_injected_total|, 1.0).

A failed audit halts the run (raises ConservationViolation). This is
non-negotiable per spec §3: a failed audit means the code is broken,
not the physics. Production mode can disable the assertion via the
caller passing audit=None to tick(); default is enabled.
"""
from __future__ import annotations

from world.flux.quantum import Quanta


class ConservationViolation(AssertionError):
    """Raised when energy conservation is violated beyond tolerance."""


class EnergyAuditor:
    def __init__(self, quanta: Quanta, tol: float = 1e-9, nodes=None):
        self.quanta = quanta
        self.nodes = nodes  # Optional Nodes instance (F1a+)
        self.tol = float(tol)
        self.E_initial: float = 0.0
        self.E_injected_total: float = 0.0
        self.E_exported_total: float = 0.0
        self.E_binding_heat_total: float = 0.0
        self.tick_count: int = 0

    def record_initial(self) -> None:
        e = self.quanta.total_energy()
        if self.nodes is not None:
            e += self.nodes.total_energy()
        self.E_initial = e

    def record_injection(self, e: float) -> None:
        self.E_injected_total += float(e)

    def record_export(self, e: float) -> None:
        self.E_exported_total += float(e)

    def record_binding_heat(self, e: float) -> None:
        self.E_binding_heat_total += float(e)

    def step(self) -> None:
        """Advance the tick counter by one."""
        self.tick_count += 1

    def check(self) -> None:
        """Assert conservation. Raises ConservationViolation on
        imbalance."""
        E_in_q = self.quanta.total_energy()
        E_in_n = self.nodes.total_energy() if self.nodes is not None \
                  else 0.0
        lhs = self.E_initial + self.E_injected_total
        rhs = (E_in_q + E_in_n + self.E_exported_total
               + self.E_binding_heat_total)
        scale = max(abs(lhs), 1.0)
        err = abs(lhs - rhs)
        if err > self.tol * scale:
            raise ConservationViolation(
                f"Energy conservation violated at tick {self.tick_count}: "
                f"E_initial({self.E_initial}) + E_injected({self.E_injected_total}) "
                f"= {lhs}; E_in_quanta({E_in_q}) + E_in_nodes({E_in_n}) "
                f"+ E_exported({self.E_exported_total}) "
                f"+ E_binding_heat({self.E_binding_heat_total}) = {rhs}; "
                f"diff={err}, tol={self.tol * scale}"
            )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/flux/test_audit.py -v`
Expected: all 10 tests PASS (6 F0 + 4 F1a).

Also run the full flux suite to confirm no regressions:
Run: `uv run pytest tests/flux/ -v`
Expected: 55 total tests pass (51 from task 7 + 4 new audit tests).

- [ ] **Step 5: Commit**

```bash
git add world/flux/audit.py tests/flux/test_audit.py
git commit -m "flux F1a task 8: auditor tracks node energy + binding heat

EnergyAuditor optionally accepts a Nodes reference. Conservation
equation extended:
  E_initial + E_injected == E_quanta + E_nodes + E_exported + E_binding_heat
F0 callers (no nodes) work unchanged (E_nodes = 0, E_binding_heat = 0).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 9: T1 conservation still holds with binding active

**Files:**
- Modify: `tests/flux/test_conservation.py` (append a new test, keep existing two)

- [ ] **Step 1: Append the new test to `tests/flux/test_conservation.py`**

```python
from world.flux.structures import Nodes
from world.flux.binding import BindingConfig


def test_T1_conservation_with_binding_active():
    """1000 ticks with injection AND binding active.

    Conservation:
      E_initial + E_injected
      == E_in_quanta + E_in_nodes + E_exported + E_binding_heat
    within 1e-9 relative.
    """
    rng_inject = np.random.default_rng(42)
    rng_bind = np.random.default_rng(123)
    q = Quanta(max_quanta=20_000)
    n = Nodes(max_nodes=20_000)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, nodes=n, tol=1e-9)
    audit.record_initial()

    cfg = BindingConfig(alpha=4.0, beta=4.0, T_crit=2.0,
                         eta=0.1, r=1.5, coherence_eps=1.0)

    QUANTA_PER_TICK = 5
    ENERGY_PER = 1.0
    N_TICKS = 1000
    DT = 0.1

    def injector(quanta, grid):
        count = inject_hot_floor(
            quanta, grid,
            n=QUANTA_PER_TICK,
            energy_per=ENERGY_PER,
            freq_mean=200.0,
            vel_z_mean=2.0,
            rng=rng_inject,
        )
        audit.record_injection(count * ENERGY_PER)
        return count * ENERGY_PER

    for t in range(N_TICKS):
        exported, binding_heat = tick(
            q, g, dt=DT, injector=injector,
            nodes=n, binding_cfg=cfg, rng=rng_bind, tick_index=t,
        )
        audit.record_export(exported)
        audit.record_binding_heat(binding_heat)
        audit.check()
        audit.step()

    audit.check()

    # Sanity bounds
    E_q = q.total_energy()
    E_n = n.total_energy()
    assert audit.E_injected_total > 0
    assert E_q >= 0
    assert E_n >= 0
    assert audit.E_exported_total >= 0
    assert audit.E_binding_heat_total >= 0
    # The full accounting equation
    np.testing.assert_allclose(
        audit.E_initial + audit.E_injected_total,
        E_q + E_n + audit.E_exported_total + audit.E_binding_heat_total,
        rtol=0, atol=1e-9 * max(audit.E_injected_total, 1.0),
    )
```

Also add the necessary import at the top of the file (right after existing imports):

```python
from world.flux.structures import Nodes
from world.flux.binding import BindingConfig
```

- [ ] **Step 2: Run the new test**

Run: `uv run pytest tests/flux/test_conservation.py::test_T1_conservation_with_binding_active -v`
Expected: PASS.

Run all conservation tests to confirm F0 ones still pass:
Run: `uv run pytest tests/flux/test_conservation.py -v`
Expected: 3 PASS.

Run full flux suite:
Run: `uv run pytest tests/flux/ -v`
Expected: 56 total tests PASS (55 + 1 new).

- [ ] **Step 3: Commit**

```bash
git add tests/flux/test_conservation.py
git commit -m "flux F1a task 9: T1 conservation holds with binding active

1000 ticks with injection AND binding. Verifies extended equation
E_initial + E_injected == E_quanta + E_nodes + E_exported + E_heat
holds within 1e-9 relative tolerance per tick.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 10: T3 Crystallization integration test (F1a acceptance)

**Files:**
- Create: `tests/flux/test_crystallization.py`

This is the F1a acceptance test from spec §7 T3.

- [ ] **Step 1: Write the integration test `tests/flux/test_crystallization.py`**

```python
"""T3 — Crystallization preferentially in cold (upper) zones.

Spec §7 T3: uniform-frequency vibration injection at hot floor;
cold ceiling. Run 5000 ticks. Verify
  count_structures(top_half) / count_structures(bottom_half) > 5.0.

This is the F1a acceptance test. When this passes, F1a is done.
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
from world.flux.binding import BindingConfig


def test_T3_crystallization_in_cold_half():
    """5000 ticks, uniform-frequency injection at hot floor, cold
    ceiling + walls. Nodes should accumulate in the top half (cold)."""
    rng_inject = np.random.default_rng(42)
    rng_bind = np.random.default_rng(123)
    q = Quanta(max_quanta=50_000)
    n = Nodes(max_nodes=50_000)
    g = Grid(dims=(10, 10, 10), voxel_size=1.0, T_smoothing=0.1)
    audit = EnergyAuditor(quanta=q, nodes=n, tol=1e-9)
    audit.record_initial()

    cfg = BindingConfig(
        alpha=4.0, beta=4.0, T_crit=2.0,
        eta=0.1, r=1.5, coherence_eps=1.0,
    )

    QUANTA_PER_TICK = 5
    ENERGY_PER = 1.0
    N_TICKS = 5000
    DT = 0.1
    FREQ_MEAN = 200.0

    def injector(quanta, grid):
        count = inject_hot_floor(
            quanta, grid,
            n=QUANTA_PER_TICK,
            energy_per=ENERGY_PER,
            freq_mean=FREQ_MEAN,
            vel_z_mean=2.0,
            rng=rng_inject,
        )
        audit.record_injection(count * ENERGY_PER)
        return count * ENERGY_PER

    for t in range(N_TICKS):
        exported, binding_heat = tick(
            q, g, dt=DT, injector=injector,
            nodes=n, binding_cfg=cfg, rng=rng_bind, tick_index=t,
        )
        audit.record_export(exported)
        audit.record_binding_heat(binding_heat)
        audit.check()
        audit.step()

    audit.check()  # Conservation must still hold

    # Spatial distribution of nodes
    alive_mask = n.alive
    assert alive_mask.sum() > 0, (
        "No nodes formed — binding never fired. Tune cfg or check "
        "injection / temperature plumbing."
    )

    node_z = n.pos[alive_mask, 2]
    Lz_half = g.dims[2] * g.voxel_size / 2.0  # 5.0 for 10×10×10
    n_top = int((node_z >= Lz_half).sum())
    n_bot = int((node_z < Lz_half).sum())

    # Pre-registered T3 threshold from spec §7
    if n_bot == 0:
        assert n_top > 0  # All in top half — trivially > 5x
    else:
        ratio = n_top / n_bot
        assert ratio > 5.0, (
            f"T3 ratio {ratio:.2f} below threshold 5.0. "
            f"top={n_top}, bot={n_bot}. Adjust BindingConfig in "
            f"docs/flux/phase-log.md."
        )
```

- [ ] **Step 2: Run the test**

Run: `uv run pytest tests/flux/test_crystallization.py -v`
Expected: PASS on first calibration with the BindingConfig defaults above. If it FAILS:
  - Inspect `n_top` / `n_bot` from the assertion message
  - Likely causes: `T_crit` too low (binding everywhere), `alpha` too small (frequency match doesn't push), `r` too large (binds far apart), `vel_z_mean` too small (quanta don't reach top)
  - Tune ONE parameter at a time. Document each attempt + result in `docs/flux/phase-log.md`. Do NOT lower the 5.0 threshold — that is pre-registered.

If after 5 parameter sweeps you cannot get the ratio above 5.0, BLOCK and report — the design may need rethinking, not retuning.

- [ ] **Step 3: Run full flux suite to confirm no regressions**

Run: `uv run pytest tests/flux/ -v`
Expected: 57 total tests pass (56 from task 9 + T3 = 57).

- [ ] **Step 4: Commit (after parameter calibration if needed)**

If you tuned `BindingConfig` to make T3 pass, include those values in the commit message body so the F1b plan can reuse them:

```bash
git add tests/flux/test_crystallization.py
# If you also modified the BindingConfig defaults in world/flux/binding.py:
# git add world/flux/binding.py
git commit -m "flux F1a task 10: T3 crystallization integration test

5000 ticks under uniform-frequency injection on a 10x10x10 cube;
nodes preferentially form in the cold upper half. F1a acceptance
test passes with BindingConfig(alpha=X, beta=Y, T_crit=Z, eta=W,
r=V, coherence_eps=U) — see docs/flux/phase-log.md for the sweep.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

Replace X, Y, Z, W, V, U with the actual values used. If defaults worked, say so explicitly.

---

## Task 11: __init__ re-exports + README + F1a close

**Files:**
- Modify: `world/flux/__init__.py`
- Modify: `README.md`
- Modify: `docs/flux/phase-log.md`

- [ ] **Step 1: Update `world/flux/__init__.py` to re-export F1a additions**

Replace the file:

```python
"""Flux Substrate — thermodynamically grounded learning substrate.

See docs/superpowers/specs/2026-05-10-flux-substrate-design.md for the
design rationale and falsifier contract.

This module is under active development. Public API stabilises after F1.
"""
from __future__ import annotations

from world.flux.audit import ConservationViolation, EnergyAuditor
from world.flux.binding import (
    BindingConfig,
    attempt_binding,
    binding_probability,
    find_pairs_within,
    pred_coherence,
)
from world.flux.boundary import absorb_cold_faces, inject_hot_floor
from world.flux.dynamics import Injector, tick
from world.flux.grid import Grid
from world.flux.quantum import Quanta
from world.flux.structures import Nodes

__all__ = [
    "BindingConfig",
    "ConservationViolation",
    "EnergyAuditor",
    "Grid",
    "Injector",
    "Nodes",
    "Quanta",
    "absorb_cold_faces",
    "attempt_binding",
    "binding_probability",
    "find_pairs_within",
    "inject_hot_floor",
    "pred_coherence",
    "tick",
]
```

- [ ] **Step 2: Update README.md "Two substrates" section**

Find the line in the existing README:

```
- **Flux** (`world/flux/`, `agent/flux/`) — the project's actual scientific bet. ... Status as of 2026-05-10: F0 in progress (skeleton + energy-conservation audit); F1–F6 roadmap pre-registered with Tier 2 falsifier as obligation and Tier 3 as stretch.
```

Replace the trailing status sentence with:

```
Status as of 2026-05-11: F0 complete (skeleton + energy-conservation audit, 33/33 flux tests + T1 acceptance); F1a complete (binding mechanism + T3 crystallization passes); F1b/F1c on the work list.
```

- [ ] **Step 3: Append F1a-close entry to `docs/flux/phase-log.md`**

Append:

```markdown

## 2026-05-11 — F1a complete

- 11 plan tasks landed.
- 57/57 flux tests pass (was 33 in F0; added 18 binding + 5 structures + 4 audit + 1 conservation + 1 T3).
- 382 legacy tests still pass.
- T3 acceptance test green: nodes form preferentially in the cold (upper) half of the cube under uniform-frequency floor injection. Ratio threshold > 5.0 holds.
- BindingConfig values that produced the pass: (record from task-10 commit message)

Known carry-overs into F1b:
- pred_coherence is the F1a stub (frequency-equality within eps). Full windowed cross-correlation is F2's job.
- Binding consumes pairs only (2 quanta -> 1 node). F1b will add multi-way binding and node-to-node binding via bridges.
- No bridges, no plasticity, no decay. F1b implements all three.
- BindingConfig defaults may need re-tuning when F1b adds structure-flux dynamics (flux through nodes will affect both node persistence and T_local in their voxels).

F1b plan to be written next.
```

- [ ] **Step 4: Run full flux suite one last time + run legacy suite**

Run: `uv run pytest tests/flux/ -v`
Expected: 57 passing.

Run: `uv run pytest tests/ -q -x --ignore=tests/flux/ -k "not slow"`
Expected: 382 passing (legacy untouched).

- [ ] **Step 5: Commit**

```bash
git add world/flux/__init__.py README.md docs/flux/phase-log.md
git commit -m "flux F1a complete: re-exports + README status + phase-log

Adds Nodes, BindingConfig, and all binding helpers to the package
public API. README "Two substrates" status updated for F1a complete.
Phase-log records the close: 57/57 flux tests + 382 legacy still
green, T3 acceptance achieved with the BindingConfig recorded in
task 10. F1b is the next plan.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## F1a Done-criterion

F1a is closed when **all** of the following hold:

- `uv run pytest tests/flux/ -v` passes with zero failures (≥ 57 tests)
- `uv run pytest tests/flux/test_crystallization.py -v` (T3 acceptance) passes
- `uv run pytest tests/flux/test_conservation.py -v` (T1 still holds, now with binding active) passes
- `uv run pytest tests/ -q --ignore=tests/flux/ -k "not slow"` shows 382 legacy tests passing (no regressions)
- README mentions F1a complete
- `docs/flux/phase-log.md` records F1a close + the BindingConfig values that made T3 pass
- 11 commits with `flux F1a task N:` (or `flux F1a complete:`) prefix on `main`

Next plan: `docs/superpowers/plans/2026-MM-DD-flux-substrate-F1b.md` — bridges, structure-flux, plasticity, decay → T4.

---

## Notes for the engineer implementing this

- **No Numba in F1a.** Naive O(N²/2) pair search is fine at ≤ 1000 alive quanta. If `attempt_binding` becomes the per-tick bottleneck in profiling, add cell-list bucketing in F1b — but don't pre-optimise.
- **Single-frequency injection is the F1a regime.** All pairs trivially coherent. The binding rule reduces to pure temperature gating, which is exactly what T3 tests.
- **Conservation is still mandatory.** The auditor now tracks `E_in_nodes` and `E_binding_heat_total`. The check formula is:
  `E_initial + E_injected == E_quanta + E_nodes + E_exported + E_binding_heat`
  If T1 fails, the bug is in `attempt_binding` (forgot to record heat?) or `Quanta.remove` (slot not zeroed?) or `Nodes.add` (energy mis-tracked?). Don't loosen tolerance.
- **Style continues to match legacy + F0.** Struct-of-arrays, `float64` for energy/position/velocity, `bool_` for alive flags, `_next_search` cursor for slot reuse.
- **No new dependencies.** numpy + pytest only.
- **Commit after every task.** Eleven commits total for F1a, one per task. Bug-fix commits are extra and clearly named (`flux F1a task N fix: ...`).
- **The T3 threshold is pre-registered.** Don't lower 5.0 if calibration doesn't immediately get there — tune the BindingConfig instead. If the design genuinely cannot meet the threshold after a documented sweep, that is a legitimate research finding; report it honestly and we revise the spec.

# Sub-project A.5 — Substrate performance (slot recycling + Numba JIT)

**Date:** 2026-05-06
**Status:** draft (awaiting user approval; ready to convert to a writing-plans plan once approved)
**Discovered scope:** not in the original foundation spec. Surfaced during Plan A's Task 9 (F1 sustained-run integration test) when wall-clock projected at multi-hour for the spec's 60-sim-minute target.
**Prerequisite:** Plan A merged. Plan A.5 is a pure performance / refactoring pass; it must not change observable substrate behaviour.

---

## 1. What this sub-project addresses

Plan A's Task 9 revealed a real architectural blocker:

- **Monotonic node allocator**: `World.allocate_node()` only ever increments `k_count`. Dead slots (where `k_alive[i] = False` after decay) are never reclaimed.
- **O(k_count) Python loops in hot paths**: `bind_nodes_upward`, `decay_unstable_nodes`, `move_nodes`, `apply_scale_repulsion`, and the decay branch of `ambient_regeneration` all iterate `for i in range(world.k_count)` in pure Python, with alive checks inside the loop.
- **Combined effect**: per-tick cost grows linearly with `k_count`, and `k_count` grows linearly with simulated time, so total wall-clock is quadratic in simulated time. Empirically: at `k_count=21` the per-tick cost is ~3 ms; at `k_count=92` it's ~20 ms (linear fit ~3 ms baseline + 0.245 ms per node). Extrapolating to a 60-sim-minute run with the spec's growth-amendment config gives 5–100+ hours wall-clock.

The 5-sim-minute reduction in Plan A's F1 unblocks the immediate test, but Plans B–G's longer integration tests (P1's 100 paired pulses, I3's 5-min closed loop, M4's 10-min glass-of-water training) will all hit the same wall as `k_count` accumulates.

This sub-project lands two performance fixes that together break the quadratic dependence:

1. **Slot recycling.** Track which slots are dead and unreferenced; `allocate_node` reuses them before extending `k_count`. Result: `k_count` plateaus at the steady-state population rather than growing forever.

2. **Numba JIT for the hot per-tick loops.** Convert the five identified hot paths to `@njit`-decorated functions. Result: per-iteration cost drops from ~50 µs Python loop overhead to ~0.5 µs JIT'd, a ~100× speedup on the inner loops.

Both are pure performance changes. Observable behaviour (counts, positions, firings, firing log, snapshot contents, test outcomes) must be identical to pre-A.5.

## 2. Architecture overview

### 2.1 Slot recycling

A new per-slot reference count `k_ref_count: np.ndarray (K,) int32` tracks how many alive higher-level nodes currently include this slot in their composition span. Reference counts are maintained by:

- `allocate_node`: when creating node N with constituents `[c1, c2]`, increment `k_ref_count[c1]` and `k_ref_count[c2]`.
- `decay_unstable_nodes` / `decay_high_level_nodes` / any other slot-killing path: when killing node N, decrement `k_ref_count[c]` for every `c` in N's composition span.

A slot `i` is recyclable iff `k_alive[i] == False AND k_ref_count[i] == 0`.

A new `World._free_slots: list[int]` maintains the recyclable-slot stack. It is populated when a slot becomes recyclable (the decay path checks ref-count and pushes the index if it just hit zero). `allocate_node` pops from `_free_slots` first; only extends `k_count` if the free list is empty.

When a slot is recycled (popped + reused), all per-slot state must be reset to a fresh-init value: `k_pos`, `k_vel`, `k_freq`, `k_pol`, `k_level`, `k_birth`, `k_alive`, `k_charge`, `k_refractory_until`, `k_strength` (back to 1.0), `k_orientation` (back to zero), `k_locked_this_tick`, `k_comp_kind`, `k_ref_count` (already 0).

### 2.2 Numba JIT migration

Five hot functions move from Python to Numba. Each is split into a thin Python entry point that does the marshalling and a Numba `@njit` core that does the work:

| Function | What it does | Inner-loop cost |
|---|---|---|
| `bind_nodes_upward` | scans alive nodes pairwise via spatial hash, attempts upgrade-target binding | dominant cost — O(k_count) outer + O(neighbours) inner |
| `decay_unstable_nodes` | per-tick exponential decay of pair/triad nodes | O(k_count) |
| `decay_high_level_nodes` | per-tick strength-modulated decay of level-5+ nodes (Plan A) | O(k_count) |
| `move_nodes` | applies k_vel to k_pos with periodic wrap | O(k_count) |
| `apply_scale_repulsion` | scale-separation repulsion between alive nodes | O(k_count²) worst case |

The `@njit` core takes pure NumPy arrays as inputs and returns plain Python ints (counts, etc) — no Python objects, no `World` instance reference. The Python entry point unpacks `world.*` arrays into the JIT call.

The substrate's RNG is the tricky part: Numba doesn't share state with `numpy.random.Generator`. For functions that need randomness, we either (a) pre-generate the random rolls in Python before calling the JIT core, or (b) use Numba's `np.random` inside the JIT function (which uses Numba's own seed). (a) is safer for reproducibility — Plan A's tests assert specific RNG-seeded outcomes, and (b) would change the RNG stream.

Approach (a) is what Plan A.5 uses. The decay functions, for instance, become:

```python
@njit
def _decay_high_level_njit(k_alive, k_level, k_strength, rolls, threshold,
                            decay_factor, K):
    n_decayed = 0
    for i in range(K):
        if not k_alive[i]:
            continue
        if k_level[i] < 5:
            continue
        s = k_strength[i] if k_strength[i] > 1.0 else 1.0
        p = decay_factor / s
        if rolls[i] < p:
            k_alive[i] = False
            k_strength[i] = 1.0
            n_decayed += 1
    return n_decayed


def decay_high_level_nodes(world, dt):
    cfg = world.config
    if cfg.lambda_dec_mol <= 0.0 or world.k_count == 0:
        return 0
    K = world.k_count
    rolls = world.rng.random(K)  # generate in Python, pass to JIT
    n_decayed = _decay_high_level_njit(
        world.k_alive[:K], world.k_level[:K], world.k_strength[:K],
        rolls, cfg.lambda_dec_mol * dt, ..., K,
    )
    # Push newly-dead slots onto the free list (in Python, since this is
    # rare and slot recycling logic stays in one place)
    if n_decayed > 0:
        for i in range(K):
            if not world.k_alive[i] and world.k_ref_count[i] == 0:
                if i not in world._free_slots_set:
                    world._free_slots.append(i)
                    world._free_slots_set.add(i)
    return n_decayed
```

(Skeleton; details may need tuning.)

## 3. New per-slot field + free list

Added to `World.__init__`:

```python
# Plan A.5 — slot recycling reference count
self.k_ref_count = np.zeros(K, dtype=np.int32)
# Free list of recyclable slots (k_alive=False, k_ref_count=0)
self._free_slots = []
self._free_slots_set = set()  # O(1) "already on free list?" check
```

The `_free_slots_set` lives alongside `_free_slots` to avoid O(n) "is index already on the free list" scans. Both are kept in sync.

The reference count starts at zero and is maintained as nodes are created and destroyed.

## 4. Modified `allocate_node`

```python
def allocate_node(self, pos, freq, pol, level, constituents, comp_kind):
    # Try to recycle first
    if self._free_slots:
        i = self._free_slots.pop()
        self._free_slots_set.discard(i)
        # Reset all per-slot state
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
        self.k_orientation[i] = 0
        # k_ref_count[i] is already 0 (free-list invariant)
        # k_comp_indices and k_comp_offset are NOT reset — they're still
        # valid until overwritten below
    else:
        i = self.k_count
        if i >= self.config.n_nodes_max:
            raise RuntimeError("Node capacity exhausted")
        self.k_count += 1

    # Now populate the slot with the new node's data
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

    # Increment ref count of constituents
    for c in constituents:
        self.k_ref_count[int(c)] += 1

    return i
```

**Critical detail: `k_comp_indices` is append-only.** When a slot is recycled, its old composition span (e.g. indices 5–7) is no longer used by anyone — but we still appended new compositions at the high-water mark `k_comp_used`. The `k_comp_indices` buffer therefore has "holes" of obsolete data. This is correct because nothing reads obsolete spans (the recycled slot's `k_comp_offset[i]` and `k_comp_offset[i+1]` are overwritten with the new span pointers). Memory-wise, `k_comp_indices` continues to grow with allocation count; if it fills the cap, we raise `RuntimeError`.

A future v2 could compact `k_comp_indices` periodically. For Plan A.5 we set `comp_caps = K * 16` (instead of `K * 4`) to give room for typical agent runs without a compaction pass.

## 5. Decay path: maintaining ref count + free list

Every code path that sets `k_alive[i] = False` for a node `i` must also:

1. Decrement `k_ref_count` for every `c` in node `i`'s composition span.
2. If the constituent `c` is now recyclable (`not k_alive[c] and k_ref_count[c] == 0`), push `c` onto the free list.
3. If node `i` itself is now recyclable (its ref count is 0), push `i` onto the free list.

The plan is to centralise this in a single helper:

```python
def _kill_node(world, i: int) -> None:
    """Mark node i dead AND decrement ref counts of its constituents AND
    push newly-recyclable slots onto the free list. Single source of
    truth for slot bookkeeping."""
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
            if not world.k_alive[c] and world.k_ref_count[c] == 0:
                if c not in world._free_slots_set:
                    world._free_slots.append(c)
                    world._free_slots_set.add(c)
    # Maybe i itself is now recyclable
    if world.k_ref_count[i] == 0:
        if i not in world._free_slots_set:
            world._free_slots.append(i)
            world._free_slots_set.add(i)
```

Existing decay functions (`decay_unstable_nodes`, `decay_high_level_nodes`) are refactored to call `_kill_node` for each decayed slot rather than just setting `k_alive[i] = False`. Same for any other code path that kills nodes — e.g. `bind_nodes_upward` deactivates the two parents when an upgrade fires; those `world.k_alive[i_a] = False` lines become `_kill_node(world, i_a)`.

## 6. Numba JIT migration plan

### 6.1 Functions to migrate

| Function | Migration approach | Notes |
|---|---|---|
| `decay_unstable_nodes` | full @njit core, Python wrapper for free-list bookkeeping | rolls pre-generated in Python |
| `decay_high_level_nodes` | full @njit core, Python wrapper | rolls pre-generated |
| `move_nodes` | full @njit | no RNG; pure numerical |
| `apply_scale_repulsion` | full @njit | the O(k_count²) worst case is the critical one for JIT speedup |
| `bind_nodes_upward` | partial — JIT the inner pair loop, keep outer + spatial-hash query in Python | the upgrade-target lookup is a Python dict; convert to a numpy array before JIT |
| `ambient_regeneration` (decay branch) | not migrated — only runs when buffer overflows, low frequency | leave as Python |

The non-hot paths (`bind_vibrations_to_electrons`, `move_vibrations`, `neuron_dynamics`, `apply_stdp`, `synaptic_transmission`) stay in Python. They are either already vectorised (vibration moves) or have complex control flow that's not a bottleneck (neuron dynamics with firing-event lists).

### 6.2 The `_UPGRADE_TARGET` migration

The current upgrade-target table is a Python dict keyed by `(li, lj)` tuples. Numba can't index a Python dict efficiently. Convert to a 2D numpy array indexed by `[li, lj]`:

```python
# Build at import time
_UPGRADE_TARGET_ARRAY = np.full((12, 12), -1, dtype=np.int8)
for (li, lj), target in _UPGRADE_TARGET.items():
    _UPGRADE_TARGET_ARRAY[li, lj] = target

_UPGRADE_TARGET_FUSION_ARRAY = np.full((12, 12), -1, dtype=np.int8)
for (li, lj), target in _UPGRADE_TARGET_FUSION.items():
    _UPGRADE_TARGET_FUSION_ARRAY[li, lj] = target
```

The JIT'd `bind_nodes_upward` looks up `_UPGRADE_TARGET_ARRAY[li, lj]`; if -1 and `mol_fusion_enabled`, falls back to `_UPGRADE_TARGET_FUSION_ARRAY[li, lj]`.

### 6.3 RNG handling

Numba can't share `np.random.Generator` state with the surrounding Python code. The approach:

- Decay functions: pre-generate `rolls = world.rng.random(K)` in Python, pass to JIT.
- `bind_nodes_upward`: the polarity choice for new nodes uses `world.rng.random()`. Pre-generate one roll per attempt (max k_count rolls per call). For typical k_count this is negligible.
- `apply_scale_repulsion`: deterministic — no RNG needed.
- `move_nodes`: deterministic.

This means the RNG sequence is identical to pre-A.5: every roll that Python made, Python still makes; only the loop body that *consumes* the rolls moved to JIT.

### 6.4 Numba startup overhead

First call to each `@njit` function compiles it (~1–3 seconds per function). Subsequent calls are ~100× faster than Python. Tests that measure performance must call the function once to warm it up before measuring.

The project already uses Numba for `bind_vibrations_to_electrons` and the spatial-hash helpers (per the original Phase 1 build), so the dependency is already there.

## 7. Configuration parameters

Two new flags, both default `True` because the changes are pure performance with no behavioural difference:

```python
# Plan A.5 — substrate performance
slot_recycling_enabled: bool = True   # use free list in allocate_node
numba_jit_enabled: bool = True        # use @njit cores for hot loops
```

For benchmark + regression diagnosis, both can be set to `False` to fall back to the old monotonic + Python paths. This is what the regression test suite uses to verify behavioural equivalence.

## 8. Acceptance tests

### 8.1 Necessary — behavioural equivalence

| ID | Test | Pass criterion |
|---|---|---|
| AP1 | Slot recycling preserves test outcomes | Run the entire existing pytest suite (Plan A's 173 tests) twice — once with `slot_recycling_enabled=True` (default) and once with `slot_recycling_enabled=False` (legacy path). Both must produce identical pass results. |
| AP2 | JIT preserves test outcomes | Same as AP1 but for `numba_jit_enabled`. |
| AP3 | Slot is reused after decay | Build a world with `n_nodes_max=4`. Allocate 4 atoms (k_count = 4). Decay one. Allocate one more — `k_count` must stay at 4 (the recycled slot was reused). Verify `_free_slots` is empty after the realloc. |
| AP4 | Reference count blocks premature recycling | Build a world. Allocate atom A (slot 0). Allocate molecule M (slot 1) with constituent A. Decay atom A: `k_alive[0]` becomes False but slot 0 must NOT be on `_free_slots` (because M references it). Decay M: now slot 0's ref count drops to 0 and slot 0 IS on `_free_slots`. Slot 1 (M) is also on `_free_slots`. |
| AP5 | k_count plateaus under sustained input | 1-minute simulated run with the growth-amendment config. Assert `world.k_count` does not exceed `2 × max_alive_node_count` at any point. (k_count can grow temporarily above peak alive count due to deallocation lag, but it should plateau, not grow linearly.) |
| AP6 | Snapshot round-trip preserves k_ref_count | Set `k_ref_count[3] = 7`. Save snapshot. Load. `k_ref_count[3]` reads back as 7. |

### 8.2 Necessary — JIT correctness

| ID | Test | Pass criterion |
|---|---|---|
| AP7 | JIT'd `decay_unstable_nodes` matches Python | Build a world with 100 alive level-2 and level-3 nodes. Pre-generate rolls. Run the Python and JIT versions independently with the same rolls. Assert identical k_alive arrays after one tick. |
| AP8 | JIT'd `decay_high_level_nodes` matches Python | Same shape as AP7 but for level-5+ nodes. |
| AP9 | JIT'd `move_nodes` matches Python | Build a world with k_count=100, random k_pos and k_vel. Run Python and JIT versions; assert k_pos arrays equal within 1e-12. |
| AP10 | JIT'd `apply_scale_repulsion` matches Python | Same shape as AP9. |
| AP11 | JIT'd `bind_nodes_upward` matches Python | Build a world with several level-1, -2, -3, -4 nodes. Run Python and JIT versions; assert identical post-state (k_alive, k_count, k_pos for new nodes). |

### 8.3 Headline — performance

| ID | Test | Pass criterion |
|---|---|---|
| **AP12** | **Per-tick wall-cost is bounded** | 5-min simulated run with the growth-amendment config. Measure wall-clock per simulated second over the run. Assert: max ≤ 5 × min (i.e. cost stays within 5× of its baseline; old code had >100× variation as k_count grew). |
| **AP13** | **F1 at full duration becomes feasible** | Re-run Plan A's F1 acceptance test at 60 sim-min (the original spec target). Wall-clock ≤ 30 min on developer hardware. (For comparison: current 5-min F1 takes ~30-90 min wall, so 60-min should take ~6× that, but with Plan A.5's quadratic→linear improvement, target is much lower.) |

### 8.4 Stretch

| ID | Test | Pass criterion |
|---|---|---|
| AP14 | k_comp_indices buffer doesn't fill on long run | 60-sim-min run; `world.k_comp_used` stays below `world.k_comp_indices.shape[0]`. (With `comp_caps = K * 16` this should be safe, but verify.) |
| AP15 | Slot recycling thread-safe | Multi-threaded test where two pseudo-threads alternate allocate / decay calls; verify no double-frees. (May not be needed if Python GIL serialises us; document the assumption.) |

## 9. Out of scope (explicitly)

- **k_comp_indices compaction.** When dead spans accumulate, the buffer can fill. v1 sizes the buffer 4× larger; compaction is a future fix.
- **Vectorising `apply_scale_repulsion`'s O(k²) outer loop into a spatial-hash variant.** The existing repulsion uses a brute-force pairwise scan. JIT'ing it is a constant-factor speedup; turning it into spatial-hash + cell-pair iteration would be algorithmic. That's its own future sub-project.
- **GPU acceleration.** CuPy / JAX / similar. Way out of scope for this perf pass.
- **Async or multi-threaded simulation.** The substrate is single-threaded; Plan A.5 keeps that invariant.

## 10. New module / test layout

```
world/
  state.py              # adds k_ref_count, _free_slots, _free_slots_set
  physics.py            # adds _kill_node helper; refactors decay paths to use it;
                         # @njit cores for the five hot functions
  snapshot.py           # extended with k_ref_count persistence (matches existing
                         # k_strength / k_orientation pattern)

tests/
  test_amendment_AP_slot_recycling_correctness.py    # AP3, AP4
  test_amendment_AP_slot_recycling_plateau.py        # AP5
  test_amendment_AP_jit_correctness.py               # AP7, AP8, AP9, AP10, AP11
  test_amendment_AP_behavioural_equivalence.py       # AP1, AP2 (parametrised)
  test_amendment_AP_snapshot.py                      # AP6
  test_amendment_AP_performance.py                   # AP12, AP13 (slow)
```

## 11. Decision log

- **Why reference counting (not garbage collection)** — refcount is deterministic, simple, single-step, and avoids GC pauses. With the small node populations involved (<10K alive at peak) and the strict tree structure of compositions (no cycles), refcount is the obvious choice. Cycles would require GC; the substrate has none.
- **Why a `set()` alongside the `list[]` for the free list** — the alternative is a flag array (`_is_on_free_list: np.ndarray bool`). The set is simpler for the small populations we expect; the array is faster for hot paths but only matters at very high k_counts. Start with set; switch to array if profiling shows it.
- **Why pre-generate RNG rolls in Python (not Numba RNG)** — preserves the RNG stream identity. Tests that assert specific seeded outcomes still pass after Plan A.5; we don't introduce a new RNG drift.
- **Why convert `_UPGRADE_TARGET` dict → 2D array** — Numba dict support is slow and brittle; small dense numpy arrays are the canonical Numba pattern. The 12×12 array adds 144 bytes; trivial.
- **Why both flags default `True`** — Plan A.5 is correctness-preserving (verified by AP1, AP2). Defaults should reflect the production path.
- **Why no migration of `bind_vibrations_to_electrons` / `apply_repulsion`** — those are already JIT'd from the original build. Re-migrating them is wasted work.

## 12. Risks

- **JIT correctness regressions.** A subtle Numba semantic difference (integer overflow handling, NaN propagation, float comparison) could cause a test to fail in the JIT version but pass in Python. AP7-AP11 catch this.
- **Slot recycling premature reuse.** If `_kill_node` is called from a code path I missed, ref counts go stale and a slot is recycled while still referenced. AP4 catches the basic case; deeper cases (spatial-hash references, snapshot mid-flight) need careful review.
- **Numba compile time.** First-test-run time goes up by ~5-10 seconds (one compile per JIT'd function). Subsequent runs are fast. CI should warm the cache once and keep it.
- **Snapshot backwards compatibility.** Old snapshots without `k_ref_count` need to load; the field defaults to 0, which is correct because nothing references slots in a freshly-loaded snapshot. (The decay-path bookkeeping is rebuilt during the next tick.)
- **`comp_caps` overflow on very long runs.** With recycling, allocations continue indefinitely while `k_comp_used` keeps growing. The buffer cap (4× → 16× n_nodes_max) should suffice for typical training durations but not infinite runs. AP14 verifies.

## 13. What this unblocks downstream

- **Plan A's F1 at full 60-sim-minute duration** (AP13) — demonstrates the foundation spec's intent.
- **Plan B's P3 plasticity-driven prediction test** — requires the substrate to evolve for ~30 simulated minutes during training. Pre-A.5 wall-clock makes that test infeasible; post-A.5 it should run in ~10–30 wall minutes.
- **Plan C's I3 closed-loop stability** — 5-sim-minute run with audio I/O + substrate. Same situation.
- **Plan G's M4 glass-of-water demo** — the headline acceptance test for the whole foundation, requiring ~10 sim-minutes of audio + video + reward training. Without A.5, this is multi-hour. With A.5, it should be tractable in a single session.

In short: Plan A.5 is what makes the foundation's headline tests demonstrable rather than theoretical.

---

## Approval gate

Before this becomes a writing-plans plan, the user should confirm:

1. **Slot recycling via reference counting + free list** is the right approach. Alternative was flag-array recycling; refcount is simpler and matches the structural-tree composition cleanly. Acceptable?

2. **Numba JIT migration scope** — five functions (`decay_unstable_nodes`, `decay_high_level_nodes`, `move_nodes`, `apply_scale_repulsion`, `bind_nodes_upward`). Two are *not* migrated (`ambient_regeneration` decay branch, `apply_stdp`). Acceptable, or should we migrate more / fewer?

3. **RNG handling: pre-generate rolls in Python, pass to JIT.** Preserves identical RNG stream so existing seeded tests still pass. Acceptable?

4. **Defaults: both flags `True`.** Pure performance change; old paths kept behind flags only for regression diagnosis. Acceptable?

5. **Headline test AP13: F1 at 60 sim-min ≤ 30 wall-min.** That's the target post-A.5 wall time. If we miss it (say, 60 wall-min instead), is that acceptable, or should we tighten the target? Hardware-dependent — confirm what hardware "developer hardware" means: my MacBook? CI runners? Both?

6. **Sequencing with Plan B.** Plan A.5 is independent of Plan B. Two options: (a) do A.5 first, then B (cleaner — B's tests have full perf headroom). (b) do B first, then A.5 (faster to user-visible features — STDP behaviour visible sooner). (a) is my recommendation since A.5 is small and self-contained, and B's longer integration tests will need the headroom anyway. Acceptable?

If approved, this becomes `docs/superpowers/plans/2026-05-06-baby-brain-foundation-plan-A5-substrate-performance.md` with TDD-bite-sized tasks.

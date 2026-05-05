# Phase 2 — Molecules and Structural Patterns Design Specification

**Status:** Draft for review
**Date:** 2026-05-06
**Source:** [`docs/CONCEPT.md`](../../CONCEPT.md) v2 §5 Phase 2
**Precondition:** Phase 1 v2 calibrated to produce atoms reproducibly (in progress, see `LOGBOOK.md` session 3)

**Scope:** Atoms (level-4 nodes) bind into molecules (level-5+). Implement the upgrade rules, the molecule-species classifier, observation tools, and tests. Per CONCEPT.md v2 §5 Phase 2, success means at least five distinct molecule species can be identified and reproduced.

---

## 1. Goal

Extend the substrate so that atoms combine into higher-order nodes — molecules — using the same general binding rules as the lower hierarchy levels. Identify recurring molecule species. Produce reliable observations of small mobile molecules (candidate neurotransmitter analogues for Phase 5) and larger structural molecules (candidate membrane components for Phase 3).

The substrate's natural laws are not changed. Phase 2 only extends the upgrade table and adds observation tooling.

## 2. Architectural decisions

| Decision | Choice | Why |
|---|---|---|
| Levels for molecules | 5 = di-atomic, 6 = tri-atomic, 7 = tetra-atomic, 8 = penta-atomic, …; capped at level 12 (octa-atomic) | Each upgrade adds exactly one atom, mirroring the Phase 1 `(N) + (1) → (N+1)` rhythm. Cap prevents runaway memory growth from very large structures (which Phase 3 will revisit). |
| Atom-only addition | Only `level-4 + level-4 → 5`, then `level-N + level-4 → level-(N+1)` for N ≥ 5 | A molecule is a "structure of atoms"; molecule-molecule binding would not match the source spec's framing. |
| Mobility | Molecules inherit `k_vel` and participate in scale repulsion, the same as atoms | Membrane formation in Phase 3 needs molecules that can drift and arrange spatially. |
| Decade rule | Atom + atom must share frequency decade (same as Phase 1); molecule (N≥5) + atom (4) must also share decade with the molecule's `k_freq` | Keeps the hierarchy frequency-coherent. |
| Polarity | Sampled fresh at formation (uniform 50/50), per CONCEPT.md v2 §2.2 | Same rule as every previous level — the keystone of the design. |
| Species identification | Hash of sorted (frequency-decade, count) pairs of constituent atoms | Cheap, deterministic, ignores noise inside a decade, matches the source spec's "different molecule species" framing. |

## 3. Binding rules (extension of Phase 1 v2)

The general binding conditions remain:

1. **Spatial proximity:** 3D periodic distance < `r_2`.
2. **Polarity difference:** opposite parity at the node level.
3. **Frequency 8% rule:** `|f1 − f2| / min(f1, f2)` within `[freq_ratio − freq_tolerance, freq_ratio + freq_tolerance]`.
4. **Same frequency decade:** `floor(log10(f1)) == floor(log10(f2))`.

The new upgrades are the rows added to `_UPGRADE_TARGET`:

| Trigger | Required levels | Resulting level | Composition stored |
|---|---|---|---|
| Di-atomic molecule | 4 + 4 | 5 | `[atom_idx_a, atom_idx_b]` (kind=1) |
| Tri-atomic | 5 + 4 (or 4 + 5) | 6 | `[molecule_idx, atom_idx]` (kind=1) |
| Tetra-atomic | 6 + 4 (or 4 + 6) | 7 | `[molecule_idx, atom_idx]` (kind=1) |
| Penta-atomic | 7 + 4 | 8 | … |
| Hexa-atomic | 8 + 4 | 9 | … |
| Hepta-atomic | 9 + 4 | 10 | … |
| Octa-atomic | 10 + 4 | 11 | … |
| Cap | 11 + 4 → no further upgrade | (no entry in `_UPGRADE_TARGET` for L≥12) | — |

Implementation: extend the existing `_UPGRADE_TARGET` dict in `world/physics.py`. The cap is implemented by simply not adding entries past level 11 + 4.

## 4. Code changes

### 4.1 `world/physics.py`

Extend `_UPGRADE_TARGET`:

```python
_UPGRADE_TARGET = {
    # Phase 1 (existing)
    (1, 1): 2,
    (1, 2): 3, (2, 1): 3,
    (1, 3): 4, (3, 1): 4,
    # Phase 2 (new)
    (4, 4): 5,
    (4, 5): 6, (5, 4): 6,
    (4, 6): 7, (6, 4): 7,
    (4, 7): 8, (7, 4): 8,
    (4, 8): 9, (8, 4): 9,
    (4, 9): 10, (9, 4): 10,
    (4, 10): 11, (10, 4): 11,
    # Cap at level 11 (deca-atomic-ish; further upgrades require Phase 3 rules).
}
```

`bind_nodes_upward` already handles arbitrary entries in `_UPGRADE_TARGET`; no other code changes needed there. Atoms (level 4) participating in bindings now consume the atom into a molecule (`k_alive[atom] = False`), the same way an electron is consumed into a pair.

### 4.2 `world/state.py`

Update `LEVEL_TO_VIBRATIONS` so `total_vibrations()` accounts for molecules:

```python
LEVEL_TO_VIBRATIONS = {
    1: 2, 2: 4, 3: 6, 4: 8,           # Phase 1
    5: 16, 6: 24, 7: 32, 8: 40,       # Phase 2 (each atom contributes 8 vibrations)
    9: 48, 10: 56, 11: 64,
}
```

### 4.3 `world/config.py`

No new fields. Phase 2 reuses Phase 1's binding parameters (`r_2`, `freq_ratio`, `freq_tolerance`, plus optional decay-rate fields).

Optional addition for later iteration:

```python
# Decay (mean exponential lifetimes, seconds) — Phase 2 levels are stable by default
# (no entry → no decay). Future calibration may add molecule_decay_time entries.
```

Molecule decay is **off by default** in Phase 2. The source spec describes molecules as functional carriers of biological processes (water, lipids, proteins, neurotransmitters); biological molecules are stable on the timescales of synaptic transmission. Decay can be added later as a calibration knob.

### 4.4 `tools/classify_molecules.py` (new)

A standalone observation tool that reads a snapshot and reports molecule-species counts.

```python
"""Classify and count molecule species in a snapshot.

A species is identified by a fingerprint built from the molecule's
constituent atoms' frequency decades. Two molecules with atoms at
decades (3, 3) are the same species (call it A33); a molecule at
(3, 4) is species A34; one at (3, 3, 3) is A333.

Usage:
    python tools/classify_molecules.py snapshot.npz [--format text|json]
"""
```

Algorithm:
1. For each alive node at level ≥ 5, walk its CSR composition recursively to find all level-4 (atom) constituents.
2. For each constituent atom, compute its frequency decade.
3. Sort the decades and form a fingerprint string `"A" + "".join(sorted(decades))`.
4. Bucket molecules by fingerprint; count each.
5. Output: a sorted table of fingerprint → count.

### 4.5 `world/render.py` and `world/preview.py` (extended)

Render molecules with size and colour scaled by level:

| Level | Radius (fraction of box diagonal) | Colour | Emission |
|---|---:|---|---:|
| 5 (di-atomic) | 0.06 | pale blue-white `#D8E0F0` | 2.0 |
| 6 (tri-atomic) | 0.07 | warm white `#F0EAD8` | 2.5 |
| 7 (tetra-atomic) | 0.08 | yellow-white `#FFF4D8` | 3.0 |
| 8+ (penta+) | 0.09 + 0.005·(level − 8) | pinkish white `#FFE0E0` | 3.5+ |

Plus a thin connecting tube between constituent atoms when rendering high-quality keyframes.

## 5. Tests

### 5.1 `tests/test_phase2_binding.py` (new)

| Test | Asserts |
|---|---|
| `test_atom_atom_forms_molecule_l5` | Two atoms within `r_2`, opposite parity, 8% freq diff, same decade → molecule at level 5 |
| `test_atom_polarity_same_no_bind` | Two atoms with same parity → no molecule |
| `test_atom_freq_off_no_bind` | Two atoms with freq diff ≠ 8% → no molecule |
| `test_atom_decade_off_no_bind` | Two atoms in different decades → no molecule |
| `test_l5_plus_atom_forms_l6` | A di-atomic molecule + atom (right rules) → tri-atomic molecule |
| `test_l6_plus_atom_forms_l7` | Tri-atomic + atom → tetra-atomic |
| `test_cap_at_level_11` | Hex-atomic (level 9 — wait, 11) + atom does not upgrade further |
| `test_molecule_does_not_bind_to_molecule` | Two molecules at level 5 within `r_2` → no upgrade (no `(5, 5)` in `_UPGRADE_TARGET`) |
| `test_molecule_polarity_random` | 50 hand-seeded di-atomic formations show both polarities (no inheritance from constituents) |

### 5.2 `tests/test_classify_molecules.py` (new)

| Test | Asserts |
|---|---|
| `test_classify_empty_world` | A world with no molecules returns an empty dict |
| `test_classify_single_diatomic_a33` | One molecule with two decade-3 atoms → `{"A33": 1}` |
| `test_classify_mixed_decades` | Molecules at (3, 3), (3, 4), (4, 4) → three different fingerprints with the right counts |
| `test_classify_higher_orders` | A tri-atomic at decades (3, 3, 4) → `{"A334": 1}` |

## 6. Acceptance criteria

This spec is satisfied when:

1. The full pytest suite passes including the new `test_phase2_binding` and `test_classify_molecules` files.
2. `tools/classify_molecules.py` runs on any snapshot without error.
3. The renderer (Open3D-style preview and Blender keyframe pipeline) draws molecules at level 5 through 11 with their assigned colours.
4. **A calibrated long run produces at least five distinct molecule species fingerprints** in `tools/classify_molecules.py`'s output. The TOML for that run is committed under `renders/` for reproducibility.
5. The LOGBOOK has a session-3 entry recording the species fingerprints observed and the calibration TOML used.

Calibrating the parameters to produce *interesting* molecule diversity (small mobile vs. larger structural) is beyond the acceptance criterion — it's part of the next round of calibration work the LOGBOOK kicks off.

## 7. Out of scope

- Molecule decay (no `molecule_decay_time` parameter for now).
- Molecule + molecule binding (would require revisiting the upgrade table; Phase 3 may revisit if membrane-formation needs it).
- Spontaneous neurotransmitter behaviour (mobile molecules emitted from sources and bound to receivers — that's Phase 5 §6.2).
- Membrane-formation tests — that's Phase 3.

## 8. Implementation order

1. `world/physics.py` — extend `_UPGRADE_TARGET`. Tests in `test_phase2_binding.py` cover this.
2. `world/state.py` — extend `LEVEL_TO_VIBRATIONS`.
3. `tools/classify_molecules.py` — observation tool. Tests in `test_classify_molecules.py`.
4. `world/preview.py` — render molecules in the preview window.
5. `tools/render_blender.py` — render molecules in keyframes (extend `add_node_spheres` colour/radius tables).
6. Smoke run with the calibrated TOML — confirm at least 5 molecule species form.
7. LOGBOOK update.

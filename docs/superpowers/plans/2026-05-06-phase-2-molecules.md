# Phase 2 — Molecules Implementation Plan

> Plan written *retroactively* matching the implementation that landed on
> 2026-05-06 with commit `66222f2` (`feat(phase2,phase3): molecules + membrane scaffolding`).
> Documented here for traceability between spec and code.

**Goal:** Atoms (level 4) bind into molecules (levels 5–11) using the same general rules. Identify recurring molecule species via fingerprint hashing.

**Architecture:** Extend `_UPGRADE_TARGET` in `world/physics.py`. Extend `LEVEL_TO_VIBRATIONS` in `world/state.py`. Add `tools/classify_molecules.py` with deterministic decade-based fingerprints. Update both renderers (Open3D-style preview, Blender keyframes) for the new levels.

**Tech Stack:** Same as Phase 1 v2 — Python 3.13+, NumPy, Numba, PyVista, Blender for keyframes.

**Spec:** [`docs/superpowers/specs/2026-05-06-phase-2-molecules.md`](../specs/2026-05-06-phase-2-molecules.md).

---

## Files touched

| Path | Change | Responsibility |
|---|---|---|
| `world/physics.py` | extend | rows added to `_UPGRADE_TARGET` for atom→molecule progression |
| `world/state.py` | extend | `LEVEL_TO_VIBRATIONS` covers levels 5–11 |
| `world/preview.py` | extend | radius/colour tables include levels 5–11 |
| `tools/render_blender.py` | extend | `add_node_spheres` radius/colour/emission tables include 5–11 |
| `tools/classify_molecules.py` | new | snapshot → species fingerprint counts |
| `tests/test_phase2_binding.py` | new | 8 tests covering binding rules and parity randomisation |
| `tests/test_classify_molecules.py` | new | 5 tests covering fingerprint correctness |

---

## Task 1 — Extend `_UPGRADE_TARGET`

**Files:** `world/physics.py`

- [x] Append the eight new rows (atom+atom → 5; molecule+atom → next level, both orderings; up to level 11).
- [x] No code changes elsewhere — `bind_nodes_upward` already iterates `_UPGRADE_TARGET` generically.
- [x] Commit (folded into the larger Phase 2 + Phase 3 commit).

## Task 2 — Extend `LEVEL_TO_VIBRATIONS`

**Files:** `world/state.py`

- [x] Add levels 5–11 with vibration counts 16, 24, 32, 40, 48, 56, 64.
- [x] Verify `total_vibrations()` returns the right count when molecules exist.

## Task 3 — Phase 2 binding tests

**Files:** `tests/test_phase2_binding.py`

- [x] `test_atom_atom_forms_molecule_l5` — basic atom + atom case
- [x] `test_atom_polarity_same_no_molecule` — same-polarity rejection
- [x] `test_atom_freq_off_no_molecule` — outside 8% rule rejection
- [x] `test_atom_decade_off_no_molecule` — different decade rejection
- [x] `test_l5_plus_atom_forms_l6` — di-atomic + atom upgrade
- [x] `test_l11_plus_atom_does_not_upgrade` — cap enforcement
- [x] `test_molecule_does_not_bind_to_molecule` — no `(5,5)` rule
- [x] `test_molecule_polarity_random_at_formation` — 60-molecule statistical check

## Task 4 — Molecule species classifier

**Files:** `tools/classify_molecules.py`

- [x] `_ground_atom_decades(world, idx)` — recursively walk CSR composition to find all level-4 atom constituents
- [x] `species_fingerprint(decades)` — sorted `"A" + decade_string`
- [x] `classify(snapshot_path)` — count molecules per species fingerprint
- [x] `format_text` and `format_json` modes
- [x] CLI entry point

## Task 5 — Classifier tests

**Files:** `tests/test_classify_molecules.py`

- [x] `test_species_fingerprint_sorted`
- [x] `test_classify_empty_world`
- [x] `test_classify_single_diatomic_a33`
- [x] `test_classify_mixed_decades`
- [x] `test_classify_higher_orders`

## Task 6 — Renderer updates

**Files:** `world/preview.py`, `tools/render_blender.py`

- [x] `world/preview.py` — radius and colour tables for levels 1–11 (was 1–4 only)
- [x] `tools/render_blender.py::add_node_spheres` — radius_for_level, color_for_level, emission_for_level extended
- [x] Smoke test: render a snapshot containing molecules at level 5+ — visible distinct colours per level

## Task 7 — Calibration verification

**Files:** none (calibration result lives in `renders/calibration_session3.toml` and the LOGBOOK)

- [x] Run `python /tmp/phase2_demo.py` (or equivalent) — calibrated Phase 1 config × 240s simulated, observe whether molecules form
- [x] Run `tools/classify_molecules.py` over the final snapshot — confirm at least 5 distinct species (or document why fewer)
- [ ] If fewer than 5 species: bump `n_initial_vibrations`, widen `freq_min`/`freq_max`, or extend duration. Iterate until criterion met.

The last sub-item is open: the overnight Phase 2 demo run was in progress when this plan was finalised; results land in the LOGBOOK session-3 entry once the run completes.

---

## Acceptance criteria

This plan is satisfied when:

1. The full pytest suite is green — verified at 84 passing tests.
2. `tools/classify_molecules.py` runs on any snapshot without error — verified.
3. The renderers handle levels 5–11 — verified visually in the calibrated animation.
4. **A calibrated long run produces ≥5 distinct molecule species fingerprints.** — pending the Phase 2 demo run finishing; if not met after 240s, the calibration TOML needs another iteration.

When (4) lands, the spec's main acceptance criterion is met and Phase 2 is closed. Phase 3 calibration follows.

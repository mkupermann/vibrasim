# Phase 3 — Membrane-like Structures Design Specification

**Status:** Draft for review (scaffolding only; spontaneous formation is empirical)
**Date:** 2026-05-06
**Source:** [`docs/CONCEPT.md`](../../CONCEPT.md) v2 §5 Phase 3
**Precondition:** Phase 2 produces molecules reproducibly (in progress)

**Scope:** Define an operational notion of a membrane in this 3D substrate, build detection tools that can identify candidate membranes in any snapshot, build a deliberate-construction tool that can hand-place molecules in a spherical-shell arrangement for stability tests. **Whether membranes form spontaneously is an empirical open question** — this spec only delivers the tooling needed to find out.

---

## 1. Goal

Make Phase 3 testable. The CONCEPT.md success criterion ("closed structures separating inside from outside, with selective permeability") is observational rather than constructional, so the deliverable is:

1. An operational definition of a membrane in this substrate.
2. Detection tools (`tools/detect_membranes.py`) that can scan any snapshot and return candidate membrane structures with measured properties (centre, radius, density, gap fraction, etc.).
3. A construction tool (`tools/construct_membrane.py`) that hand-places molecules in a hollow-shell arrangement, then runs the simulation forward to test stability under our natural laws.
4. Tests for the detection geometry on synthetic data.

This iteration **does not** change the natural laws. No new binding rules, no new force terms. We are observing what the existing substrate produces, and we are testing whether shell arrangements are stable under it.

## 2. Operational definition

A **membrane** in this substrate is a set of molecules satisfying all of:

- **Connectivity:** the molecules are pairwise close (within `r_membrane = 2.0 · r_2`); the set forms one connected component under that adjacency graph.
- **Hollow shell:** the molecules' positions lie approximately on the surface of a 3D sphere. Operationally:
  - Fit a sphere to the molecule centres (least squares).
  - The radial standard deviation `σ_r` of molecule distances from the sphere centre is < 0.20 · R (within 20% of the radius).
  - The interior of the sphere (radius < 0.6 · R from centre) contains no alive nodes.
- **Surface coverage:** at least 12 molecules lie on the shell. Below this, the structure is more pebble than membrane.
- **Optional permeability points:** identified by gaps in surface-density. A gap is a 3D solid-angle wedge (a small spherical cap on the fitted sphere) containing no molecules. A membrane with 0–4 permeability points is considered "closed but selective"; a membrane with ≥ 5 gaps is "leaky" and probably not membrane-like.

These thresholds are first-cut. The detection tool exposes them as parameters so calibration can tune them.

## 3. Detection algorithm

```python
def detect_membranes(world, r_membrane, hollow_threshold=0.6, sigma_threshold=0.20):
    """Find candidate membrane structures in `world`.

    Returns a list of dicts, one per candidate, with:
      - 'molecule_indices': k_pos indices of constituent molecules
      - 'centre': fitted sphere centre (3-vector)
      - 'radius': fitted sphere radius
      - 'sigma_r': radial std-dev (lower = more shell-like)
      - 'interior_count': number of alive nodes inside hollow_threshold·R
      - 'n_gaps': number of detected permeability points
      - 'closed': True if interior is empty AND sigma_r < sigma_threshold
    """
    # 1. Build adjacency graph: molecules within r_membrane of each other are connected.
    # 2. Find connected components (BFS/DFS).
    # 3. For each component with ≥ 12 molecules:
    #    a. Fit a sphere by least squares: minimize ||(p_i − c)|² − R²||²
    #    b. Compute σ_r = std-dev of |p_i − c| − R for each molecule.
    #    c. Count interior nodes — alive nodes with |p − c| < hollow_threshold · R.
    #    d. Detect permeability gaps via spherical-bin density (16 azimuth × 8 polar bins
    #       on the unit sphere; bins with zero molecules are gaps; merge adjacent gaps).
    # 4. Return descriptors.
```

## 4. Sphere fitting

A standard linear least-squares formulation:

For points `p_i = (x_i, y_i, z_i)`, the sphere `(x − c_x)² + (y − c_y)² + (z − c_z)² = R²` expands to:

    x_i² + y_i² + z_i² = 2·c_x·x_i + 2·c_y·y_i + 2·c_z·z_i + (R² − c_x² − c_y² − c_z²)

Define `D = R² − c_x² − c_y² − c_z²`. Solving the linear system

    A = [[2·x_1, 2·y_1, 2·z_1, 1], …]
    b = [x_1² + y_1² + z_1², …]
    [c_x, c_y, c_z, D] = np.linalg.lstsq(A, b)

yields `c` and then `R = sqrt(D + c_x² + c_y² + c_z²)`.

## 5. Construction tool

```python
def construct_shell(world, centre, radius, n_molecules, atom_count_per_molecule=2):
    """Place n_molecules atoms-bonded into molecules on a sphere of radius R.

    Uses a Fibonacci sphere distribution for even surface coverage.
    Each molecule is constructed as a level-(4 + atom_count_per_molecule - 1) node
    with synthetic atom constituents whose frequencies satisfy the 8% rule.
    """
```

Once placed, run the simulation forward and watch:

1. **Decay:** does the shell hold together over the run, or do molecules drift apart?
2. **Repulsion impact:** if shell molecules span multiple frequency decades, the §4.6 repulsion will tear them apart. Test with single-decade and mixed-decade shells separately.
3. **Permeability:** drop "small molecules" (lower-level nodes near the sphere) and see if they pass through gaps.

## 6. Files

| Path | Status | Responsibility |
|---|---|---|
| `tools/detect_membranes.py` | new | scan a snapshot, return candidate membranes with descriptors |
| `tools/construct_membrane.py` | new | hand-build a synthetic shell snapshot |
| `tests/test_detect_membranes.py` | new | sphere-fit accuracy on synthetic data; gap detection; threshold logic |
| `tests/test_construct_membrane.py` | new | constructed shells pass detect_membranes' "closed" check |
| `LOGBOOK.md` | append | session 3 entry includes any membranes detected during the calibrated runs |

## 7. Tests

### 7.1 `tests/test_detect_membranes.py`

| Test | Asserts |
|---|---|
| `test_sphere_fit_recovers_synthetic` | 200 points sampled on a sphere of known radius/centre — fit recovers both within 1% |
| `test_sphere_fit_with_noise` | Same points with σ=0.1·R noise — radius within 5%, centre within 0.05·R |
| `test_detect_synthetic_shell_is_closed` | A constructed Fibonacci sphere of 30 molecules → detected as closed (interior_count=0, sigma_r small) |
| `test_detect_open_cluster_is_not_closed` | A solid ball of 30 molecules (filled, not a shell) → detected with interior_count > 0, NOT closed |
| `test_gap_detection` | A shell with one removed cap of 30° radius → 1 permeability gap detected |

### 7.2 `tests/test_construct_membrane.py`

| Test | Asserts |
|---|---|
| `test_construct_30_molecule_shell` | construct_shell(n=30) places 30 alive nodes on a sphere |
| `test_constructed_shell_passes_detector` | After construct_shell, detect_membranes returns the shell as a closed candidate |

## 8. What this spec doesn't promise

**Spontaneous membrane formation under our natural laws is not guaranteed.** The CONCEPT.md text is explicit: Phase 3 may transition to a Phase 4 in which neurons are modelled without explicit membranes if our substrate cannot produce them.

What the deliverable from this spec **does** guarantee:

1. The detection tool runs on any snapshot without false positives on dense-but-filled clusters.
2. The construction tool can produce synthetic shells for stability tests.
3. The test suite covers the geometry (sphere fitting, gap detection, threshold logic).

If, after Phase 2 calibration, no shells emerge spontaneously, we use the construction tool to test which parameter regime keeps a hand-built shell stable for 60+ simulated seconds. That experiment determines whether Phase 4 needs explicit membranes or can proceed without them.

## 9. Out of scope

- Active transport across the membrane (Phase 5).
- Membrane self-replication.
- Lipid-bilayer-faithful chemistry.
- Permeability gating by frequency (selectivity beyond "compatible-frequency molecules pass small gaps").

## 10. Implementation order

1. `tools/detect_membranes.py` — sphere fit + gap detection + connectivity. Tests in `test_detect_membranes.py`.
2. `tools/construct_membrane.py` — Fibonacci shell placement + molecule synthesis. Tests in `test_construct_membrane.py`.
3. Smoke run: build a 30-molecule shell with `construct_shell`, run forward 60s, observe whether it holds.
4. Run `detect_membranes` on the calibrated Phase 2 snapshots from session 3 — record any candidate shells.
5. LOGBOOK update.

This is scaffolding for the empirical work that follows; the question "do shells form spontaneously?" is answered in calibration sessions after this spec lands.

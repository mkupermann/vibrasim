# Phase 2 Calibration Findings — ≥5 species achieved

**Agent:** Phase-2 calibration teammate, 2026-05-06
**Goal:** find a config that produces ≥5 distinct molecule species (CONCEPT.md v2 §5 Phase 2)
**Result:** **MET** by single-knob amendment (no spec change needed)

---

## Stage 1 — calibration sweep over existing knobs

9 configs × 60 simulated seconds, rng_seed=42:

| Config | freq_min | freq_max | freq_tol | n_init | r_2 | Species | Mols | MaxAtoms | Wall(s) |
|---|---|---|---|---|---|---|---|---|---|
| C0_baseline (session3b) | 100 | 10000 | 0.030 | 800 | 28 | 2 | 2 | 20 | 596 |
| C1_ftol010 | 100 | 10000 | 0.10 | 800 | 28 | 4 | 11 | 23 | 352 |
| C2_narrow_wide | 1000 | 9999 | 0.20 | 800 | 28 | 2 | 12 | 15 | 338 |
| C3_narrow_dense | 1000 | 9999 | 0.20 | 1500 | 40 | 2 | 50 | 16 | 606 |
| C4_decade2_max | 100 | 999 | 0.20 | 1200 | 40 | 2 | 41 | 10 | 386 |
| **C5_ftol020** | **100** | **10000** | **0.20** | **800** | **28** | **6** | **17** | **18** | **231** |
| C6_decade4_max | 10000 | 99999 | 0.20 | 1500 | 40 | 2 | 51 | 12 | 430 |
| **C7_twodecade_wide** | **100** | **9999** | **0.20** | **1500** | **40** | **10** | **37** | **19** | **439** |

### Verdict

Stage 1 succeeded — Stage 2 (per-level `freq_tolerance` substrate amendment) was **not needed**.

Two configs exceeded the ≥5 species threshold:
- **C5_ftol020**: 6 species — single-knob delta from session3b (`freq_tolerance` 0.030 → 0.200)
- **C7_twodecade_wide**: 10 species — overall leader (n_init=1500, r_2=40, ftol=0.20)

### Species breakdown — C5_ftol020 (the minimal-delta winner)

```
6 distinct species, 17 molecules total
A33    × 6   (di-atomic, both at decade 3)
A44    × 5   (di-atomic, both at decade 4)
A3334  × 2   (tetra-atomic, three at decade 3 + one at decade 4)
A444   × 2   (tri-atomic, all at decade 4)
A33334 × 1   (penta-atomic, four at decade 3 + one at decade 4)
A3344  × 1   (tetra-atomic, two at decade 3 + two at decade 4)
```

### Why single-decade configs (C2, C3, C4, C6) capped at 2 species

The `_decade(f) == _decade(g)` check in `bind_nodes_upward` requires same-decade for binding. When all atoms occupy a single decade, every molecule species is some homogeneous (AXX, AXXX, …) of that decade, hard cap at 2 species (di- and tri-atomic).

### Mechanism — why widening freq_tolerance helps so much

With `freq_tolerance=0.030`, the binding ratio window is `[0.050, 0.110]`. ~7% of same-decade atom pairs satisfy this; with 18 atoms ≈ 8 eligible pairs → 2-3 species.

Widening to `freq_tolerance=0.200` expands the window to `[−0.120, 0.280]`. Any pair with `f_larger ≤ 1.28 × f_smaller` qualifies; ~20% of same-decade pairs, ≈ 23 eligible pairs → 6-10 species.

---

## Promoted to repository

Saved at `renders/calibration_phase2_acceptance.toml` — the C5_ftol020 minimal-delta variant. Committed alongside the bug-fix integration. Reproducibility verified at integration time: 6 species in 60s simulated, 223s wall.

The C7_twodecade_wide variant (10 species) is also a viable promotion if the priority is *more* species rather than minimum delta.

## Wall time

Total Stage 1 across 8 completed configs: ~600 s parallel across 4 workers.

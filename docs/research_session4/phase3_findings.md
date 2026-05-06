# Phase 3 Membrane Findings — sustains, doesn't produce

**Agent:** Phase-3 membrane teammate, 2026-05-06
**Goal:** test whether membrane-like structures form spontaneously OR whether constructed shells hold under the natural laws.

---

## Experiment A — spontaneous formation

Calibrated session3b config × 120 simulated seconds, snapshot every 10s, run `tools/detect_membranes.py` after each:

| sim_t (s) | n_atoms | n_molecules (≥L5) | n_candidates | n_closed |
|----------:|--------:|------------------:|-------------:|---------:|
| 10 | 8 | 1 | 0 | 0 |
| 20 | 15 | 1 | 0 | 0 |
| 30 | 17 | 2 | 0 | 0 |
| 40-90 | 18-20 | 2 | 0 | 0 |
| 100-120 | 21 | 2 | 0 | 0 |

**Total `closed: True` candidates ever observed: 0.**

Molecules plateau at 2 (the session-3b cap). Detector requires ≥12 molecules in a connected component; world never reaches it.

---

## Experiment B — constructed shell stability

4 cases × 60 simulated seconds. Synthetic Fibonacci shells, level=5, single decade (30-36 kHz), no ambient.

| radius | N_mol | init σ_norm | final σ_norm | drift | final closed | n_gaps |
|-------:|------:|------------:|-------------:|------:|:------------:|-------:|
| 30 | 30 | ~3.3e-14 | 2.7e-14 | 0.0 | **True** | 4 |
| 30 | 50 | ~2.8e-15 | 2.7e-14 | 0.0 | **True** | 2 |
| 50 | 42 | ~1.9e-14 | 1.3e-14 | 0.0 | **True** | 4 |
| 50 | 60 | ~1.3e-14 | 1.9e-14 | 0.0 | **True** | 0 |

All four shells stayed `closed: True` for 60 simulated seconds. Zero positional drift (k_pos identical at t=10s and t=60s). k_vel zero. Same-decade placement ⇒ scale repulsion silent (frequency ratio < repulsion_threshold).

---

## Verdict

The substrate **sustains** a hand-built membrane indefinitely but **does not produce** one spontaneously at current calibration:

- Spontaneous membranes need ≥12 molecules; current configs cap at 2 (session-3b) or 17 (Phase 2 acceptance).
- The Phase 2 acceptance config (which produces 17 molecules) is the *next obvious test*: re-run experiment A against it to see if the molecule pool reaches 12 in a connected component.

## Substrate amendments needed (in priority order)

1. **Allow molecule + molecule binding.** No `(5,5)` entry in `_UPGRADE_TARGET`; molecules can only grow by absorbing atoms. A condensation pathway between molecules would unlock larger structures from the existing molecule pool.
2. **Higher atom density.** ~10× more vibrations or smaller box to get reliably 50+ atoms.
3. **Per-level freq_tolerance** (already partially addressed by the Phase 2 finding — wider global `freq_tolerance` was enough for ≥5 species, may not be enough for shells).
4. **Explicit shell-formation potential.** New physics term — short-range attraction between molecules at scale r < R_shell. Substantial spec amendment.

## Wall time

~30 min total. Experiment A is the bottleneck (~29 min for 120 s simulated).

---

## Follow-up suggested

Re-run Experiment A with `renders/calibration_phase2_acceptance.toml` (which produces 17 molecules). Even if molecules don't spontaneously form a closed shell, this would establish whether the Phase 2 config gets *closer* to the membrane threshold than session-3b did.

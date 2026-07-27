# BP-B1 — Molecules carry information (Rung B, existence claim)

**Programme:** Belief path (`docs/BELIEF_PATH.md`)  
**Status:** PRE-REGISTERED (bars locked before any data)  
**Date locked:** 2026-07-19  
**ID:** BP-B1  

---

## Hypothesis

**H-B1.** Under current substrate primitives, two **real** level-5 molecules that differ only in **composition fingerprint** (constituent atom frequency decades), placed with **positions uninformative** for the label, remain **decodable by composition alone** after a hold of *T* ticks — while matched negative controls fail.

This is an **existence** claim for structure-as-content, not emergent encoding from free evolution (that would be BP-B2).

## Mechanism

- **Write (engineered, charter §4.8-honest):** plant real composition trees via `World.allocate_node`:
  - Species **α** → fingerprint `A33` (two level-4 atoms, both frequency decade 3)
  - Species **β** → fingerprint `A34` (one decade-3 atom + one decade-4 atom)
- **Hold:** run `physics.tick` for *T* ticks; quiet world (no ambient gen, no molecule decay, no thermal node motion); no label-dependent drive.
- **Read:** composition walk → `species_fingerprint` (same algorithm as `tools/classify_molecules.py`). **Position is not used** for the treatment decode.

## What is NOT claimed

- Emergent species formation from free chemistry
- Talent / light / sound specialization (Rung C)
- Activity-memory or position-memory (G114–G119 already cover position)
- Any advantage over VSA / classical stores

## Arms

| Arm | Description | Expected if H-B1 true |
|-----|-------------|------------------------|
| T | α vs β planted, random pos, hold *T*, decode by fingerprint | accuracy ≥ 0.90 |
| C1 | Empty composition level-5 shells; labels not stored in structure | accuracy ≤ 0.60 |
| C2 | Real plant then scramble composition so fingerprint ≠ write label | accuracy ≤ 0.60 |
| C3 | Same plants as T; decode by position heuristic only (ignore composition) | accuracy ≤ 0.60 |
| C4 | Diagnostic: fraction treatment carriers alive + non-empty composition | ≥ 0.80 (bar B5) |

## Locked acceptance bars

| ID | Criterion | Threshold |
|----|-----------|-----------|
| B1 | Treatment (T) decode accuracy over all trials × seeds | ≥ **0.90** |
| B2 | C1 accuracy | ≤ **0.60** |
| B3 | C2 accuracy | ≤ **0.60** |
| B4 | C3 accuracy | ≤ **0.60** |
| B5 | Treatment survival: alive molecule + non-empty composition walk | ≥ **0.80** |

Chance for binary α/β = 0.50.

### Verdict rule

- **PASS** — B1 and B5 met, and B2–B4 all met (controls fail as required).
- **NULL** — any required bar unmet but harness valid; diagnose binding constraint.
- **FAIL** — crash, budget overrun, or indefensible pattern (e.g. C1 “passes” content while claiming structure).

**No post-hoc threshold tuning.** New experiment number if bars must change.

## Protocol numbers (locked)

| Parameter | Value |
|-----------|--------|
| Trials per seed *N* | 20 (10 α + 10 β, shuffled) |
| Seeds *S* | 2 → `{42, 7}` |
| Hold *T* | **500** ticks |
| dt | `1/60` s (default) |
| Box | `(80, 80, 80)` |
| n_initial_vibrations | 0 |
| lambda_gen / lambda_dec / lambda_dec_mol | 0 |
| node_thermal_speed | 0 |
| mol_fusion_enabled | False |
| Fingerprint α | `A33` |
| Fingerprint β | `A34` |

## Time budget

| Phase | Estimate | Hard 2× ceiling |
|-------|----------|-----------------|
| Implement + smoke | ≤ 1 h | 2 h |
| Full run | ≤ 40 min | 80 min |

Overrun → FAILED post-mortem in `LOGBOOK.md`, no quiet extension.

## Prediction (pre-data)

Prior ≈ 0.55 PASS if composition CSR is preserved under quiet hold; most likely NULL mode = carrier death / composition wipe; false-PASS risk mitigated by C1–C3.

## Runner

`tools/run_bp_b1_molecule_information.py`  
Results: `~/.eqmod/bet/BP-B1/result.json`

## RESULT

**Verdict: PASS** (2026-07-19)  
Runner: `tools/run_bp_b1_molecule_information.py`  
Artifact: `~/.eqmod/bet/BP-B1/result.json`

| Bar | Value | Threshold | Pass? |
|-----|------:|-----------|:-----:|
| B1 treatment acc | **1.000** | ≥ 0.90 | yes |
| B2 C1 empty acc | **0.000** | ≤ 0.60 | yes |
| B3 C2 scramble acc | **0.000** | ≤ 0.60 | yes |
| B4 C3 position acc | **0.525** | ≤ 0.60 | yes |
| B5 survival | **1.000** | ≥ 0.80 | yes |

Protocol: N=20 trials/seed × seeds {42, 7}, T=500 hold ticks. Smoke (N=4, T=50, seed 42) also PASS (all bars).

### Scope (honest)

- **Existence of structure-as-content under engineered write:** composition fingerprint (`A33` vs `A34`) survives quiet physics and decodes the write label; empty shells and scrambled composition do not; position-only readout stays near chance.
- **Not shown:** emergent species formation from free evolution (BP-B2); talent of collections (Rung C); that composition is *dynamically* maintained under stress (only quiet hold tested).
- Composition is CSR state on real constituents — a low-bar existence proof that the medium *can* hold molecular structure as a content channel distinct from position (G114–G119).

### Prediction check

Pre-data prior ~0.55 PASS; outcome PASS. Main risk was carrier death — did not materialize under locked quiet config (`lambda_dec_mol=0`, no thermal motion).

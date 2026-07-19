# BP-B3 — Multi-bit molecule information (Rung B depth)

**Programme:** Belief path · lab headless  
**Status:** PRE-REGISTERED  
**Date locked:** 2026-07-19  
**ID:** BP-B3  
**Depends on:** BP-B1 PASS (2-way composition content)

---

## Hypothesis

**H-B3.** Three real level-5 molecule species with distinct composition fingerprints  
(`A33`, `A34`, `A44`) remain decodable by composition alone after hold *T*, with  
positions uninformative — so molecule structure carries **multi-bit** content  
(log2(3)≈1.58 bits potential), not only a binary distinction.

## Mechanism

Plant real diatomic molecules via `allocate_node` (same as B1):

| Label | Fingerprint | Atom decades |
|-------|-------------|--------------|
| 0 | A33 | 3,3 |
| 1 | A34 | 3,4 |
| 2 | A44 | 4,4 |

Random position; hold *T*; decode by fingerprint walk. No live 3D.

## Arms

| Arm | Setup | Expected |
|-----|--------|----------|
| T | plant 0/1/2, decode fingerprint | acc ≥ 0.90 |
| C1 | empty shells | acc ≤ 0.40 (chance 1/3) |
| C2 | scramble composition after plant | acc ≤ 0.40 |
| C3 | position-only heuristic | acc ≤ 0.45 |
| C4 | survival composition non-empty | ≥ 0.80 |

Chance = 1/3 ≈ 0.333.

## Bars (locked)

| ID | Criterion | Threshold |
|----|-----------|-----------|
| B1 | Treatment accuracy | ≥ **0.90** |
| B2 | C1 empty acc | ≤ **0.40** |
| B3 | C2 scramble acc | ≤ **0.40** |
| B4 | C3 position acc | ≤ **0.45** |
| B5 | Survival | ≥ **0.80** |

## Protocol

| Param | Value |
|-------|--------|
| N trials/seed | 24 (8 per label) |
| Seeds | **{71, 73}** |
| T hold | 500 |
| box | 80³ |
| Quiet world | lambda_gen=dec=0 |

## Time budget

Estimate ≤ 15 min · hard 2× = 30 min.

## Prediction

Prior ≈ 0.70 PASS (B1 mechanism generalises to 3 classes).

## Runner

`tools/run_bp_b3_multibit_molecule.py`  
`~/.eqmod/bet/BP-B3/result.json`

## RESULT

*(empty until after run)*

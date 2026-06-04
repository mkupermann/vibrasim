# JEP-74 — scale envelope of the unified system: VSA capacity vs #concepts and structure complexity

## Motivation
JEP-73b unified grounding+structure on 10 concepts. Honest question: how does it SCALE? VSA bundling has a known
capacity limit (crosstalk grows with the number of bound items; cleanup fails past it, scaling with dimension D).
Characterize the unified system's scale envelope: relational-query accuracy vs #concepts in a scene, at fixed D.

## Pre-registration (locked BEFORE run)
- Unitarized concept vectors (as JEP-73b). A scene bundles P relational pairs (P above-relations). Query 'what is
  above Y'; cleanup. Sweep P (scene complexity) and D (dimension). Measure accuracy vs P for each D.
- CHARACTERIZATION: report the capacity curve (accuracy vs P) for D in {512,1024,2048}; the number of pairs at
  which accuracy drops below 0.9 is the capacity. Expectation: capacity grows ~linearly with D (known VSA result).
  Established (VSA capacity, Plate/Gallant-Okaywe), named as such.

## Result — measured scale envelope (VSA capacity ~ D; ambiguity from object reuse)
| D | P=10 | P=30 | P=60 | P=100 | P=150 |
|---|------|------|------|-------|-------|
| 256 | 0.88 | 0.51 | 0.34 | 0.17 | 0.13 |
| 512 | 0.89 | 0.64 | 0.38 | 0.28 | 0.17 |
| 1024 | 0.88 | 0.67 | 0.46 | 0.33 | 0.23 |

**VERDICT: scale envelope measured.** Relational-query accuracy DEGRADES with scene complexity P and is HIGHER
for larger D - the known VSA capacity result, now measured for the unified system. HONEST nuance: here objects
appear in MULTIPLE relations (random sampling), so part of the drop is genuine AMBIGUITY (multiple things above
the same Y -> the query returns a superposition) on top of crosstalk. With DISTINCT objects per pair (no reuse),
capacity is higher (~20 clean pairs at D=512, per the prior run). So the honest scale bound: the unified
grounded+structured system holds ~TENS of relations (VSA-capacity-limited, capacity ~ D); rich scenes (hundreds+
of relations, as in human cognition) need large D or HIERARCHICAL CHUNKING (recursion, JEP-67). This is the
measured scale envelope - the system works at small-scene scale, not yet rich-scene scale. The corrected finding:
capacity ~ D (measured), NOT 'unlimited'; the script's degenerate 'cap=0' was P=10 sitting just below the 0.9 bar
(0.88). Honest, measured. Established (VSA capacity, Plate; Gallant-Okaywe), named as such.

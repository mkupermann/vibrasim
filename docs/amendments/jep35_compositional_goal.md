# JEP-35 — compositional abstract goals: set logic (AND/OR/NOT) + relatedness over IS-A, then plan

## Motivation
JEP-34 handled single-category goals. Richer, more understanding-relevant: COMPOSITIONAL goals combining IS-A
with logic ("a mammal that is NOT a carnivore"), disjunction ("carnivore OR bird"), negation ("NOT animal"), and
relatedness ("most related to cat"). Composes the geometric programme's symbolic operators (AND/OR/NOT set logic)
with the concept reasoner (IS-A + relatedness) and the world-model planner.

## Pre-registration (locked BEFORE run)
- Same grid world + 14 leaf entities + concept reasoner + SR planner. Goal types: AND_NOT, OR, NOT, RELATED.
- Ground each goal by set logic over is_a / nearest, navigate to the nearest grounded entity, success = the
  arrived entity TRULY satisfies the goal (ground-truth taxonomy descendants / set ops).
- Bars: reached-goal-satisfying >= 0.85 AND >> random (+0.3). PASS = the agent handles compositional conceptual
  goals. NULL otherwise. Established (set logic, SR/TD, Poincare embeddings), named as such.

## Result — PASS (1.00 across all four goal types)
| goal type | accuracy (n) |
|-----------|--------------|
| AND_NOT ("mammal AND NOT carnivore" -> primates) | 1.00 (35) |
| OR ("carnivore OR bird") | 1.00 (42) |
| NOT ("NOT animal" -> plants) | 1.00 (39) |
| RELATED ("most related to X") | 1.00 (44) |
| random baseline | 0.27 |

**VERDICT: PASS.** The agent handles COMPOSITIONAL conceptual goals perfectly (1.00 across all types, random
0.27): set logic (AND/OR/NOT) + relatedness over IS-A ground each goal, the world-model SR planner navigates.
This composes the geometric programme's symbolic operators + the concept reasoner + the world model - a richer
step toward understanding-informed behaviour than JEP-34's single-category goals. KEY honest connection: the
AND_NOT case ("mammal AND NOT carnivore") depends DIRECTLY on the JEP-32 cross-branch is_a fix - it requires
is_a(human,carnivore)=False, which the OLD generality-only is_a got WRONG (would have wrongly excluded primates
from "NOT carnivore"). So the correctness bug I found and fixed by stress-testing my own deliverable is exactly
what makes compositional reasoning work here. Clean because entity->category IS-A is the reliable regime (not
siblings). Established methods (set logic, SR/TD, Poincare), named. Honest scope: small curated world+taxonomy.

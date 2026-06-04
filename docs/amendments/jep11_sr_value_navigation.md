# JEP-11 — SR as a VALUE FUNCTION enables genuine maze navigation (fixes JEP-8/9 planner flaw)

## Motivation
JEP-9's nav metric was invalid: 1-step greedy on EMBEDDING DISTANCE can't traverse a maze (dead-ends). But the
Successor Representation has a correct use: M[s,g] = expected discounted future occupancy of goal g from s = a
VALUE FUNCTION for reaching g. Greedy ascent (pick neighbour maximizing M[s',g]) is soft-Dijkstra and should
navigate mazes. Tested at scale with the LOCALLY-LEARNED (TD) SR.

## Pre-registration (locked BEFORE run)
- Random maze (DFS spanning tree), M x M cells. SR learned by LOCAL TD (substrate-compatible).
- Planners: (1) SR-VALUE greedy: from c pick carved-neighbour argmax M_td[neighbour, goal]; (2) EUCLID greedy
  (pick neighbour nearest goal in coords) - control; (3) random walk. Budget = 6*S steps.
- Reference: BFS path always exists (connected tree) -> optimal reachable = 1.00.
- Bars: SR-VALUE reached >= 0.9 AND >= EUCLID + 0.3 AND >= random + 0.3. PASS = locally-learned SR enables
  genuine maze planning (closes JEP-8/9). NULL otherwise. SR/TD (Dayan 1993) established, named as such.

## Result — PASS
| planner | maze goals reached |
|---------|--------------------|
| SR-VALUE greedy (local TD) | 1.00 (optimal) |
| Euclidean-greedy (control) | 0.03 |
| random | 0.32 |
| BFS-optimal reference | 1.00 |

**VERDICT: PASS.** The locally-learned SR, used as a VALUE FUNCTION (greedy ascent on M[s',goal]), navigates
the maze PERFECTLY (1.00) vs Euclidean-greedy 0.03 (stuck at walls) and random 0.32. This CLOSES JEP-8/9: the
prior failure was the PLANNER (1-step greedy on embedding distance), NOT the representation. SR encodes geodesic
reachability; a LOCAL TD rule learns it (JEP-9 corr 1.00). Substrate connection: TD with eligibility traces IS
the substrate's BTSP primitive (CLAUDE.md), so SR-learning is WITHIN the substrate's own toolkit - not a
foreign method. The full substrate-native planning loop: local TD/BTSP -> SR (geodesic value) -> value-based
planning (dynamic-programming / MPC) -> optimal goal-reaching. All backprop-free, all local. SR/TD (Dayan 1993)
established, named as such.

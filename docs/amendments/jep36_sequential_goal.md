# JEP-36 — sequential abstract goals: temporal composition of grounded subgoals

## Motivation
JEP-34/35 handled single + logically-composed goals. The next level is TEMPORAL composition: 'visit a <A> THEN
a <B>'. The agent must ground each subgoal (IS-A), plan to the first, then plan to the second from there - a
multi-step conceptual task, closer to genuine task execution.

## Pre-registration (locked BEFORE run)
- Grid world + 14 leaf entities + concept reasoner + SR planner. Goal = ordered pair of categories (A THEN B).
- Agent: ground A, navigate to nearest A-entity; from there ground B, navigate to nearest B-entity.
- Success = the entity visited FIRST is truly an A and the entity visited SECOND is truly a B (in order).
- Bar: ordered-sequential accuracy >= 0.85 (>> random ~0.05). PASS = the agent executes sequential conceptual
  tasks. NULL otherwise. Established (SR/TD, Poincare, sequential planning), named as such.

## Result — PASS
| metric | value |
|--------|-------|
| visited A THEN B correctly (in order) | 1.000 |
| random 2-entity sequence baseline | ~0.046 |

**VERDICT: PASS.** The agent executes SEQUENTIAL conceptual tasks ('visit a <A> THEN a <B>') at 1.00 - grounding
each subgoal via IS-A and navigating in order. Temporal composition of grounded subgoals, beyond JEP-35's logical
composition. HONEST framing of the integration trio (JEP-34/35/36, all 1.00): these compose cleanly because the
toy regime is the RELIABLE one - entity->category IS-A (true ancestor relations, not the sibling residual of
JEP-33) + small reliable SR planning + exact set logic. The composition INHERITS the component limits (sibling
confusion, full-scale under-convergence of JEP-31, deep-hierarchy degradation) in harder regimes - it is not
magically more robust than its parts. So: the BUILDING BLOCKS COMPOSE into single/logical/temporal understanding-
informed behaviour in the regime where the parts are reliable - a genuine, honestly-bounded integration. Open
work: stress-test composition where components are weak (siblings, scale, ambiguous goals). Established methods
(SR/TD, Poincare, set logic, sequential planning), named as such.

## Integration thread (JEP-34/35/36) conclusion
The two EQMOD-4 threads (world-model planning + concept reasoning) compose into an agent that acts on conceptual
goals: single ("reach a carnivore"), logical ("mammal AND NOT carnivore"), and sequential ("a carnivore THEN a
plant"). Knowledge informs action. Honestly bounded to the reliable toy regime; inherits component limits at scale.

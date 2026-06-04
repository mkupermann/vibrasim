# JEP-122 — understanding-informed action: the engine grounds a conceptual goal, the agent acts (perceive->understand->plan->act)

## Why (the programme capstone: unify the two threads)
Unify the Understanding Engine (JEP-92..121) with the world-model/MPC action loop (JEP-11/16/34): an agent
PERCEIVES objects, UNDERSTANDS them via the engine's taxonomy, grounds a CONCEPTUAL goal ('reach a living thing')
through engine.is_a, and PLANS a path to the nearest correctly-grounded target. The complete perceive->understand
->plan->act loop with the full engine.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 PASS: the agent reaches a correct-category target (is_a(target, goal-concept)) ~1.00 vs random ~chance, across
  conceptual goals incl AND/NOT. MOST-LIKELY MISS: the integration interface (grounding -> target set -> planner).

## Acceptance
- PASS: grounded-goal reach >= 0.95 and >> random; wrong-category never chosen. Established (SR/value planning +
  taxonomic grounding; JEP-34 did this with the old reasoner), named; no novelty. The point is the UNIFICATION.

## Result — PASS (HIT), the programme capstone
Grounded-plan reach: 'living thing' 1.00 (vs 0.73 random), 'animal' 1.00 (0.50), 'vehicle' 1.00 (0.22),
compositional 'animal that can fly' 1.00 (0.28). The engine GROUNDS conceptual goals via is_a + has_property; the
agent PLANS (BFS/value) to the correctly-grounded target, never the wrong category. Prediction HIT; tally 21/36.
The two main EQMOD-4 threads are UNIFIED: the Understanding Engine (JEP-92..121) drives the world-model/MPC action
loop (JEP-11/16/34) — perceive -> understand -> plan -> act, with conceptual and COMPOSITIONAL goals grounded by
the full engine's reasoning. This is the programme capstone: understanding-informed behavior. Established (SR/value
planning + taxonomic/property grounding), named; no novelty. HONEST: toy gridworld, deterministic BFS planner,
objects pre-named (perception->name is JEP-116/117); the unification of understanding+action is the point.

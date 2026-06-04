# JEP-63 — complete grounded loop with FUNCTIONAL concepts (act-to-learn-function -> reason -> act)

## Motivation
Capstone of the grounding thread: combine affordance-learned FUNCTIONAL concepts (JEP-62) with the complete loop
(JEP-55). The subtlety: function is NOT VISIBLE, so the agent must ACT to learn each entity's function from
affordances, form functional categories, then RECALL which entities have which function to plan on FUNCTIONAL
goals ('reach a container'). The most understanding-relevant demo: action-grounded functional concepts driving
goal-directed behaviour.

## Pre-registration (locked BEFORE run)
- Entities with visual IDs (uninformative about function) + hidden functions. Phase 1: agent observes each
  entity's AFFORDANCE -> infers function -> clusters into functional categories. Phase 2: goal = a functional
  category; ground = entities whose LEARNED function is in it; SR-plan; navigate.
- Bars: functional-category purity >= 0.9 (concepts valid) AND grounded-planning success >= 0.85 (reach a
  correct-FUNCTION entity). PASS = the full act-to-learn-function -> reason -> act loop works. Established
  (clustering, SR/TD), named as such.

## Result — PASS (the complete functional loop: act-to-learn -> reason -> act)
| phase | result |
|-------|--------|
| Phase 1: act to learn function (affordances) | 4 functional categories, true-purity 1.00 |
| Phase 2: plan to a functional goal (recall learned function) | reached correct-function entity 1.00 |

**VERDICT: PASS.** The agent ACTS to learn each entity's function from affordances (function NOT visible), forms
functional categories (purity 1.00), and plans to a functional goal - reaching a correct-function entity 1.00 of
the time by RECALLING what interaction taught it. Action-grounded FUNCTIONAL concepts drive goal-directed
behaviour: function from DOING, not appearance. This is the grounding-thread capstone and the most understanding-
relevant demo of the session. COMPLETE grounding arc: visual concepts from appearance (JEP-58/59) -> functional
concepts from interaction (JEP-62) -> the full act-to-learn-function -> reason -> act loop (JEP-63). HONEST scope:
simulated affordances (function-determined outcomes), toy environment, low noise (degrades with affordance noise
per JEP-62); NOT human-level understanding. But the STRUCTURE of learning-by-doing -> concepts -> action is
demonstrated end-to-end. Established methods (clustering, SR/TD), named as such.

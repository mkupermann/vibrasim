# JEP-62 — affordance-based concept formation: functional categories from INTERACTION, not appearance

## Motivation
JEP-60/61 mapped the frontier: functions UNCORRELATED with appearance need NON-VISUAL signal. The most basic
non-visual signal is AFFORDANCE - what happens when the agent INTERACTS with an item (a container holds, a tool
breaks, food is consumed). Test: when appearance is uninformative about function, can concept formation from
AFFORDANCE OUTCOMES recover the functional categories that appearance-based formation cannot?

## Pre-registration (locked BEFORE run)
- N items, each with a hidden FUNCTION (one of F classes). VISUAL features = random (UNCORRELATED with function).
  AFFORDANCE outcome = function-prototype + noise (function-determined; what interacting reveals).
- Cluster (into F) on VISUAL vs AFFORDANCE features; measure purity vs true function. Sweep affordance noise.
- Bars: affordance-clustering purity >= 0.9 at low noise AND >> visual-clustering purity (~1/F chance). PASS =
  interaction/affordance grounding recovers functional categories appearance cannot. NULL otherwise. Established
  (clustering, affordance learning), named as such.

## Result — PASS (affordance/interaction recovers function appearance cannot)
| signal | functional cluster purity |
|--------|---------------------------|
| appearance (uninformative) | 0.433 (~chance 0.25) |
| affordance, noise 0.3 | 1.000 |
| affordance, noise 0.8 | 0.883 |
| affordance, noise 1.5 | 0.633 |
| affordance, noise 2.5 | 0.550 |

**VERDICT: PASS.** When function is UNCORRELATED with appearance, clustering on AFFORDANCE outcomes (what
interacting reveals) recovers functional categories perfectly (1.00) while appearance-clustering is at chance
(0.43). Degrades gracefully with affordance noise. The agent must ACT to discover function when it is not visible
- and affordances do recover it. This makes the JEP-60 frontier concrete: the non-visual signal that recovers
appearance-independent functions is INTERACTION/AFFORDANCE. Honest caveat: simulated affordances (function-
determined outcomes), toy. COMPLETE grounding account: functional concepts come from EITHER (a) the right visual
INVARIANCE when function correlates with appearance (JEP-60 shape->footwear) OR (b) INTERACTION/AFFORDANCES when
it does not (JEP-62). Established (clustering, affordance learning), named as such.

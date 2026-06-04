# JEP-15 — model-based MPC beats cached SR on TRANSITION changes (the explicit-world-model advantage)

## Motivation
JEP-14b: the cached SR is reward-general but TRANSITION-specific - a blocked passage leaves it stale (0.63)
until full relearning. The model-based answer (the user's MPC directive): keep an EXPLICIT, LOCALLY-EDITABLE
transition model; on a transition change, edit the ONE affected edge (O(1)) and REPLAN via MPC/DP - instant
recovery, no relearning. This rung demonstrates the explicit-world-model + MPC advantage over the cached SR for
transition revaluation. Honest framing: SR (cached) wins for reward changes (instant, JEP-14b); explicit model
+ MPC wins for transition changes - the classic model-free/model-based complementarity.

## Pre-registration (locked BEFORE run)
- Looped maze (as JEP-14b). Two agents: (1) cached SR (TD-learned, stale after change); (2) MODEL-BASED: explicit
  adjacency model + planning value = BFS/DP distance-to-goal on the CURRENT model.
- Block a cycle edge (real detour). Detoured goals. Measure reach for: stale SR; model-based AFTER a LOCAL model
  edit (remove the blocked edge) + replan, with ZERO value relearning.
- Bars: model-based reach >= 0.9 AND >= stale-SR + 0.2 (instant transition recovery via local edit + MPC). PASS
  = explicit world model + MPC gives instant transition-revaluation the cached SR cannot. Methods (model-based
  planning / value iteration / MPC) established - named as such.

## Result — PARTIAL (model-based perfect; single-edge variance left the gap short of the bar)
| agent | reach on detoured goals |
|-------|-------------------------|
| MODEL-BASED (local edit + MPC/DP) | 1.00 |
| cached SR (stale) | 0.89 |

**VERDICT: PARTIAL.** Model-based MPC achieved PERFECT instant transition-recovery (1.00, zero relearning) - the
core claim. But this single blocked edge degraded the stale SR only to 0.89 (vs 0.63 in JEP-14b), so the gap
(0.11) missed the pre-registered 0.2 margin. Single-edge variance is high: in a looped maze, many blocks barely
disrupt (alternative paths remain). Bars locked, not retuned. JEP-15b averages over many blocked edges for a
robust estimate of the model-based advantage.

# JEP-191 — functional vs visual grounding: the last grounding frontier, characterized

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 appearance-clustering recovers visual groups (NOT functional), affordance-clustering recovers functional groups;
  the developmental loop grounds functional concepts only with affordance features — functional grounding needs
  interaction perception, not appearance (JEP-58/61/62 within the loop).

## Result — PASS (HIT)
Built 4 kinds where APPEARANCE and FUNCTION cross-cut: stool (small-legs / SEAT), small_table (small-legs / SURFACE,
looks like stool), armchair (big-soft / SEAT, looks unlike stool), desk (big-flat / SURFACE). Clustered the same
items by appearance features vs affordance features, scored against FUNCTIONAL truth (seat vs surface):
- cluster by APPEARANCE -> functional purity 0.50 (CHANCE — it recovers VISUAL groups, visual purity 1.00, but those
  are NOT the functional categories).
- cluster by AFFORDANCE -> functional purity 1.00 (function recovered exactly).
So when appearance and function CROSS-CUT, ONLY affordance/interaction features recover FUNCTIONAL categories;
appearance recovers look-alikes. The developmental loop grounds FUNCTIONAL concepts only with affordance perception.
THE COMPLETE GROUNDING PICTURE (JEP-178..191): a concept's grounding draws on THREE complementary perceptual/
linguistic sources at different levels — APPEARANCE from vision (coarse categories, JEP-187/189), NAMES from language
(fine distinctions vision blurs, JEP-190), and FUNCTION from affordance/INTERACTION (categories that cross-cut
appearance, JEP-191). Pixel grounding gets appearance; FUNCTIONAL grounding is the genuine OPEN frontier because it
requires perceiving INTERACTIONS (how things are used), not static images — which needs interaction data the project
does not have. This precisely characterizes WHY functional grounding is blocked and WHAT would unblock it. Prediction
HIT; tally 80/107. Established (affordance grounding, JEP-62; feature-space determines recoverable categories); named; no novelty.

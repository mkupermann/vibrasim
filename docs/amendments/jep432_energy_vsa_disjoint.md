# JEP-432 — Non-linear affect over UNSEEN real VSA clouds (JEP-431 flaw fixed)

## Motivation
JEP-431 was NULL/partial because of a self-caught flaw: F=12, K=4 gives only C(12,4)=495 distinct
concepts, so train and test overlapped — the learners memorized rather than generalized, and the
raw-linear baseline scored 0.86–0.90 instead of failing. JEP-432 fixes the flaw and re-asks the
clean question: does the valence-reservoir energy model recover a NON-LINEAR affect rule over
**genuinely unseen** real VSA energy-clouds, where a linear readout cannot?

## Method (`tools/run_jep432_energy_vsa.py`)
Identical to JEP-431 except the concept space is enlarged so train/test are provably disjoint:
- F=64 features, K=6 per concept → C(64,6) ≈ 7.4×10⁷ distinct concepts.
- Generate UNIQUE concept feature-sets, then PARTITION into disjoint train (800) and test (400) —
  no test concept appears in train (asserted in code).
- Same XOR affect: dark(−1) iff `feat0 ∈ concept XOR feat1 ∈ concept`, else bright(+1).
- `ValenceReservoirLearner(n_inputs=D=4096, n_features=600)`; compare reservoir vs raw-linear
  least-squares vs shuffled-valence control. Seeds 0 and 7.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J432a (energy model generalizes to unseen clouds):** reservoir held-out ≥ 0.80, both seeds.
- **J432b (genuinely non-linear — now that memorization is impossible):** raw-linear ≤ 0.65 on the
  disjoint test set, both seeds.
- **J432c (negative control fails):** shuffled-valence reservoir ≤ 0.60, both seeds.

Predicted PASS (reservoir cracks the XOR-affect on unseen clouds; raw-linear at ~chance now that it
cannot memorize). NULL if J432a < 0.80 (the bundle noise destroys the rule across unseen clouds — no
transfer) or if J432b still fails (the cloud geometry linearizes XOR even without overlap — also a
real, reportable finding about VSA representations). Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): NULL/partial — disjoint fixed, but a SECOND flaw (imbalance + XOR collapse)

| seed | reservoir held-out | raw-linear | shuffled control | base rate |
|------|--------------------|------------|------------------|-----------|
| 0 | 0.990 | 0.993 | 0.650 | 0.802 |
| 7 | 0.978 | 0.988 | 0.700 | 0.825 |

J432a ✓ (reservoir generalizes to truly unseen clouds), **J432b ✗ (raw-linear 0.99), J432c ✗
(control 0.65–0.70 > 0.60) → NULL/partial.**

**The second flaw (honest).** The disjoint-split fix worked, but the affect rule degenerated. With
F=64, K=6 a feature is present with prob 6/64 ≈ 0.094, so "feat0 XOR feat1 present" is dominated by
the *neither-present* case; "both present" has prob ≈ 0.008 and is negligible. With "both" gone, XOR
collapses to "**exactly one** ≈ **OR** of two sparse features", which is **near-linearly separable**
(a linear readout `w ≈ v_feat0 + v_feat1` thresholded). Hence raw-linear nails it (0.99). The set is
also **83% imbalanced** (base rate 0.80–0.825), so the shuffled control rides the majority class
above 0.60. Both locked bars correctly flagged that this still does not isolate a non-linear
advantage.

**Accumulating substantive finding (across JEP-431/432).** It is genuinely HARD to construct a
low-order affect rule over real VSA clouds that a LINEAR readout cannot crack — because (1) each
feature's presence is linearly decodable from the bundle (`cloud · v_feat`), and (2) low-order
logic over sparse features collapses toward linear separability. That is itself informative about
Michael's energy-cloud model: **the distributed cloud representation makes low-order affect
linearly readable** — arguably a feature, not a bug, but it means the reservoir's extra non-linear
capacity is not exercised by these rules.

**Corrected follow-up (JEP-433):** force a BALANCED, genuinely non-linear rule — each concept
contains exactly one of {A0,A1} and exactly one of {B0,B1} (two independent 50/50 binary slots) plus
filler; valence = parity(which-A, which-B). This is 50/50 balanced AND true XOR with no degenerate
"both/neither" case, so a linear readout must drop to chance if the reservoir's non-linearity is
what carries it. Third attempt; if raw-linear STILL wins, the "VSA linearizes low-order logic"
finding is established and the sub-thread closes.

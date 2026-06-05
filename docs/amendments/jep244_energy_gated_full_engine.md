# JEP-244 — robust FULL engine on the substrate via the ENERGY-GATED chain stop (the right fix for JEP-242/243)

Pre-registered 2026-06-05 (BEFORE the run). JEP-243 (NULL) traced the JEP-242 seed-7 interaction failure to a
DIAGNOSED-LESSON RECURRENCE: the chain ROOT-stop used `SIM_STOP` (value-overlap), which cannot detect an untrained
(root) key — so is-a chains ran PAST their root into spurious nodes, breaking the leak guard. The correct detector
is the KEY→VALUE ENERGY (JEP-237). A probe confirmed the energy gate stops at every root (both seeds). This BET
applies the energy gate to the chain stop (and the part-of hop) and verifies the full engine runs robustly.

## Method (no transformer)
- Identical to JEP-242 (one typed EnergyNet, all relation types from prose), but the chain-stop and the part-of hop
  use the JEP-237 ENERGY GATE: at store time `e_med = median(stored-pattern energies)`; a hop CONTINUES only if its
  settled energy ≤ `0.7 × e_med` (a trained edge = deep minimum; a root/untrained key = shallow → stop). Single-shot
  (no aggregation — the fix is the gate, not redundancy). Same battery + interaction + leak guard. Seeds 42 & 7.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J244a | Battery 1.00 on BOTH seeds | energy-gated battery match vs symbolic = 1.00 (both seeds) — closes the 0.93 dip |
| J244b | Interaction + leak hold BOTH seeds | part-of × is-a UP True + leak guard False, both seeds (closes J242c/J243b) |
| J244c | Chains STOP at roots | no is-a chain from a stored leaf overruns its root (the chain's reached set ⊆ the symbolic ancestor set), both seeds |
| J244d | Above an untrained control | untrained net battery match ≤ 0.60 (both seeds) |

PASS = J244a–d → the energy-gated chain stop fixes the integration; the full multi-relation engine runs robustly on
the substrate from prose. NULL (honest): J244a/b fail → the energy gate doesn't separate roots at this seed/load
(then it's a capacity/code-separation issue, not the gate). No post-hoc threshold tuning.

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 PASS, high confidence — the JEP-243 root-stop probe already showed every root's `hop(root,isa)` energy
(−35…−60) is ABOVE the 0.7×median gate (−64/−65) for BOTH seeds, while every trained edge is well below it, so the
energy gate stops chains exactly at roots: no overrun, leak guard holds, battery 1.00 both seeds (J244a), interaction
holds (J244b), reached-sets ⊆ symbolic ancestors (J244c), control fails (J244d). RISK: the gate threshold 0.7×median
is locked from JEP-237; if a root edge ever sat near −64 it could misfire — the probe shows margin (≥4 on the tight
seed-42 animal case), so I expect clean separation. Established (Hopfield energy as a stored-vs-untrained-key
detector, JEP-237), named; no novelty — the value is closing the integration with the CORRECT (already-diagnosed)
fix, applied consistently to the chain stop.

## RESULT (2026-06-05): PASS — all 4 bars, BOTH seeds; the energy-gated chain stop closes the integration

| seed | battery match | control | interaction + leak | chains stop at roots | JEP-242 (SIM_STOP) |
|------|---------------|---------|--------------------|--------------------|--------------------|
| 42 | 1.00 | 0.33 | True | True | 1.00 |
| 7  | 1.00 | 0.33 | True | True | 0.93 |

- **J244a ✓** — battery across all relation types = **1.00 on BOTH seeds** (closes the seed-7 0.93 dip).
- **J244b ✓** — the part-of × is-a interaction + leak guard hold on both seeds (closes J242c/J243b).
- **J244c ✓** — every is-a chain's reached set ⊆ the symbolic ancestor set: chains STOP at roots, no overrun.
- **J244d ✓** — untrained control 0.33.

**FINDING — the integration capstone, fixed correctly:** the FULL multi-relation Understanding Engine (is-a, part-of,
causal, comparison, temporal — multi-hop in each, the part-of × is-a interaction with leak guard) runs ROBUSTLY on
one typed energy substrate from real prose, matching the symbolic engine at 1.00 on both seeds. The fix was the
already-diagnosed JEP-237 ENERGY GATE applied to the chain root-stop (not the wrong JEP-243 aggregation). The
242→243→244 arc is the discipline in action: PARTIAL (interaction brittle, mis-diagnosed as a flake) → NULL
(aggregation fails, but digging in exposes the systematic SIM_STOP root-stop bug = a diagnosed-lesson recurrence) →
PASS (the energy gate, applied consistently, closes it). Lesson banked: a detector found for "stored vs untrained
key" (energy, not value-overlap) must be used at EVERY such check — slot-detection AND chain-root-stop. Established
(Hopfield energy detector, JEP-237), named; no novelty. Verdict: **PASS** (predict-calibrate HIT — the high-confidence
PASS the JEP-243 probe set up). This completes the substrate-relational arc (JEP-232..244): the substrate is the
engine's robust, typed, multi-relation memory + inference engine, store/chain/type/DAG/interaction/online, from prose,
bounded by ~20 edges/module — with the cure hierarchy (energy-gate for untrained keys; aggregation for independent
noise; codes/capacity for systematic interference) mapped.

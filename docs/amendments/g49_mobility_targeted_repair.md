# G49 — Is the wound static because edges are RIGID? Mobility + targeting repair

Pre-registered: 2026-06-05 (BEFORE the run). G48 falsified the G47 valence-commitment trade-off
and corrected the diagnosis: the membrane fails to heal because of **positional rigidity**
(curvature_k + atom_repulsion_k freeze the shell's shape so wound edges cannot migrate to
re-close) **+ no wound-targeting** (ambient regeneration forms atoms elsewhere, not at the hole).
G49 tests that corrected diagnosis as a causal claim: if rigidity is the blocker, then making the
wound edges MOBILE while edge-closure pulls them together should close the wound — the first
genuine self-repair in this substrate. If it still does not heal, the negative is deeper than
rigidity.

## Method (`tools/run_g49_mobility_repair.py`)
G46/G47 protocol (form membrane block=2 → wound a polar cap + its bridges → repair window 250),
seeds 42 & 7. Three repair arms (config swapped at the start of the repair window only):
- **A mobility+targeting:** `edge_closure_k=1.5`, `curvature_k=0.5` (↓ from 2.0),
  `atom_repulsion_k=0.3` (↓ from 1.0) — edges can migrate AND are pulled to close.
- **B mobility only (control):** `edge_closure_k=0.0`, same softened rigidity — mobile, untargeted.
- **C targeting only = G47 repeat (control):** `edge_closure_k=1.5`, rigidity UNCHANGED (2.0 / 1.0).

Metrics over the repair window: `healed = (recovered − post)/(N0 − post)` (largest-bridged
component regrowth, G47's metric); plus a **no-collapse guard** `radius_keep = final_radius /
initial_radius` to distinguish a re-closed shell from a collapsed blob.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G49a | Membrane forms | N0 ≥ 50 (both seeds) |
| G49b | Wound lands | post ≤ 0.7 × N0 (both seeds) |
| G49c | Mobility+targeting heals, no collapse | arm A: healed ≥ 0.30 AND radius_keep ≥ 0.6 (both seeds) |
| G49d | Healing needs targeting (not mobility alone) | arm A healed ≥ arm B healed + 0.20 (both seeds) |
| G49e | Mobility is the unlock vs rigid G47 | arm A healed ≥ arm C healed + 0.20 (both seeds) |

PASS = G49a–e → **first genuine membrane self-repair**: softening rigidity + edge-closure
targeting re-closes the wound, confirming G48's corrected diagnosis (rigidity + no-targeting was
the blocker) and completing the structural ladder with a self-renewing shell. PARTIAL = G49c
holds but G49d/e fail → it heals but via mobility/re-merging alone, not targeting. NULL = G49c
fails → even mobile, targeted edges do not re-close (the negative is deeper than rigidity — e.g.
fragments diffuse apart faster than edge-closure pulls them, or the wound atoms are simply gone).
Honest whichever way. No post-hoc threshold tuning.

## RESULT (2026-06-05): NULL — the negative is deeper than rigidity (and deeper than commitment)

| seed | N0 | post | A mob+tgt healed (rkeep) | B mob healed | C rigid+tgt healed |
|------|----|------|--------------------------|--------------|--------------------|
| 42 | 112 | 24 | **0.00** (rkeep 0.89) | 0.00 | 0.00 |
| 7  | 110 | 33 | **0.00** (rkeep 1.00) | 0.00 | 0.00 |

G49c ✗, G49d ✗, G49e ✗ → **NULL.** Mobility + edge-closure targeting heals exactly as much as the
rigid G47 baseline and as mobility-alone: **nothing**. The largest bridged component stays frozen
at post-wound size in every arm; `radius_keep` ≈ 0.89–1.00 shows the remaining shell holds its
shape (no collapse) — it simply never regrows.

**Corrected diagnosis (the real blocker, now isolated by elimination).** Across G46–G49 the
membrane fails to self-repair, and we have now ruled out the three candidate causes in turn:
valence commitment (G48 — block 0 ≡ block 2), positional rigidity, and absence of edge-closure
targeting (G49 — softening rigidity and turning targeting on changes nothing). What remains is the
true mechanism: **the wounded component cannot recruit NEW atoms into its bridge network at the
wound.** Component growth requires new/existing atoms to form *bridges* (b_alive) that attach to
the surviving shell; ambient regeneration replenishes free vibrations, but they do not bond onto
the committed membrane atoms at the hole — the surviving shell's atoms are bond-saturated and the
fresh atoms nucleate their own small clusters elsewhere rather than extending the existing one. The
membrane is a **terminal stable structure**: it forms, persists, regulates (G43/G44), and houses a
reaction interior (G45), but it does not grow new membrane onto itself. Self-repair would need a
mechanism that lets the existing shell act as a *template* recruiting new atoms at its free edges —
which this substrate does not have.

**Sub-thread closed (honest negative).** G46→G49 is a clean, four-experiment bounded negative:
the proto-cell is persistent and homeostatic but **not self-renewing**, and the blocker is
template-directed recruitment, not rigidity or valence. No more knob-twiddling (that would be
post-hoc fishing); the finding stands. The structural ladder ends at: persistent ✓, selective ✓,
homeostatic ✓, recovering-to-set-point ✓, reaction-chamber ✓, self-repairing ✗ (mechanism named).

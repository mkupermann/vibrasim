# G41 — Sealed two-way compartments: modular independence, corrected

Pre-registered: 2026-06-02 (BEFORE the run). G40 showed the one-way containment wall makes
cross-talk WORSE — it traps foreign emissions that enter a compartment. Fix:
`compartment_mode='seal'` (two-way) reflects inbound-from-outside (foreign emissions bounce
off, cannot enter) AND outbound-from-inside (own emissions stay in). Re-test modular
independence with the corrected boundary; bars identical to G40.

## Method
Identical to G40 (BET-099 substrate, two compartments A x=7.5 / B x=22.5, radius 6, raised
at STIM start, firing tallied per core during STIM) with `compartment_mode='seal'`.
Arms: A-seal (stim A), B-seal (stim B), A-nowall (cross-talk control).

## Bars (locked pre-run — same as G40)
| ID | Criterion | Bar |
|----|-----------|-----|
| G41a | A isolated | A-seal: A_fire / B_fire ≥ 10× |
| G41b | B isolated | B-seal: B_fire / A_fire ≥ 10× |
| G41c | No-wall shows cross-talk | A-nowall: A_fire / B_fire < 3× |
| G41d | Structure survives | A-seal: both A-core and B-core retain ≥ 3 atoms through STIM |

PASS = G41a–d → two engineered compartments are modularly independent with a sealed
boundary; the seal is what creates the independence. A positive CONCEPT §4.8 modular-port
building block. NULL: if G41a/b still fail, sealing free-vibration transit is insufficient —
the cross-talk route is not vibration transit (e.g. bridge percolation between near
compartments), localizing the limit further. Honest either way. No post-hoc threshold tuning.

## RESULT (2026-06-02): NULL/partial — the seal works, but this geometry can't decide its value

| arm | A_fire | B_fire | ratio |
|-----|--------|--------|-------|
| A-seal | 174 | 22 | A/B = 7.9 |
| B-seal | 16 | 164 | B/A = **10.2** |
| A-nowall | 171 | 30 | A/B = 5.7 |

G41a ✗ (7.9 < 10), G41b ✓ (10.2), G41c ✗ (no-wall 5.7 ≥ 3), G41d ✓. **Verdict: NULL/partial.**

**Mechanistically the seal WORKS.** Vs the one-way wall (G40: A/B 3.3, B/A 2.4) the two-way
seal roughly doubled isolation (7.9, 10.2) — foreign-driven cross-talk fell sharply
(B_fire 62 → 22 when A is stimulated). The fix was correct.

**But the geometry can't decide the wall's value.** At 15-unit separation the no-wall
baseline already isolates 5.7× (emissions decay over distance), so the seal's marginal
benefit is modest, and the residual ~16–22 fires in the un-stimulated compartment look like
INTRINSIC baseline firing (each region self-fires a little), not cross-talk from the other.
A raw firing-ratio bar conflates intrinsic baseline with leakage, and the "no-wall must show
cross-talk" bar (G41c) can't be met when distance alone gives 5.7×.

**Correct test (G42):** put the compartments CLOSE (where distance does NOT isolate) and use
an INDEPENDENCE metric — compare each compartment's firing under {stim-other} vs {stim-none}.
Independence = a compartment's activity is unchanged by the OTHER's stimulus. Show the seal
restores independence where no-wall has heavy cross-talk. That isolates the seal's true
contribution. Then consolidate the modular-port thread regardless of outcome.

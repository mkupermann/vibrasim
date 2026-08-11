# G161 — content-addressable matter recall under PRIM14 (capability question)

**Status: SIGNED OFF 2026-08-11 — committed before any data generation (D2). Bars final per D3.**

## 1. The one question (D1)

> With per-bond rest lengths (PRIM14, D2-verified attractor), the write channel
> gated during recall (D1 lesson), and the D2 dynamics cell — does the matter
> register now do content-addressable recall AT ALL: store a k-bit pattern,
> cue half the 1-bits, and have the substrate's own tension dynamics restore
> the missing bits at ≥ 0.90 bit-accuracy, with the no-bond control at chance?

**Scope separation (declared):** G154 CLOSED the efficiency question (Hopfield
1.000 at 1/546th wall-clock; that verdict stands). G161 asks ONLY whether the
capability exists on the substrate under the new primitive. Hopfield is run and
REPORTED as context (accuracy + wall-clock), but is NOT a verdict gate. A
capability-PASS does not reopen the efficiency claim — any efficiency statement
would need its own new ID.

## 2. Changes vs G154 (all declared, none post-hoc)

| Aspect | G154 (frozen, closed) | G161 |
|---|---|---|
| Rest length | global r_eq = r_2·0.5 | `per_bond_rest_enabled=True` (PRIM14) |
| Write channel during recall | open (valence 2, free slots) | gated: `atom_valence=1`… see §3 note |
| Dynamics | k=0.5, damping 0.95 (hardcoded) | k=8.0, damping 0.95 (D1-stable cell, config) |
| Verdict gate | accuracy AND beat-Hopfield-at-matched-wallclock | accuracy + controls only (efficiency closed) |
| Protocol otherwise | 6 cells, spacing 6, displace 14, cue ⌈ones/2⌉, 8 patterns × seeds {42,7,13} | identical |

§3 note on the write gate: G154's chain register needs valence 2 for interior
carriers (two stored neighbours). Valence-1 would break storage. The gate is
therefore implemented as a RECALL-PHASE bridge-formation freeze: no new bridges
may form after consolidation ends (harness enforces it and the bond census
verifies it — any new bond post-consolidation = run INVALID). This is an
engineered probe condition, named as such; the storage physics is untouched.

## 3. Protocol

Exactly tools/g154_matter_recall.py with the §2 changes: K=6 cells at spacing 6,
carriers at "1" cells, 8 consolidation ticks (bonds form at stored geometry,
per-bond rest = formation distances), cue = ⌈ones/2⌉ pinned, recall carriers
displaced +14, 400 relax ticks under tension, occupancy readout (CELL_R 1.5).
8 random patterns (≥2 ones) × seeds {42, 7, 13}. Negative control: identical
runs with atom_valence=0 (no bonds) — must stay ≤ 0.5. Bond census pre/post
relax every run (write gate verified). Hopfield baseline measured and reported.

## 4. Pre-registered bars (fixed before any data; D3)

- **PASS:** substrate mean bit-accuracy ≥ 0.90 on ≥ 2/3 seeds AND neg-control
  mean ≤ 0.5 AND all bond censuses clean.
- **PARTIAL:** 0.75 ≤ mean < 0.90 on ≥ 2/3 seeds, controls clean.
- **NULL:** mean < 0.75 (capability still absent under PRIM14), controls clean.
- **FAIL:** neg-control > 0.5 (readout artifact), or bond census violated
  (write gate failed — engineering stop), or G154-regression check: a
  control arm with per_bond_rest OFF (same dynamics k=8) reaching ≥ 0.75
  would mean the gain is the dynamics, not the primitive — then the PRIM14
  attribution is unsupported and the verdict is NULL-ATTRIB (recorded as
  NULL with the attribution explicitly denied).

Additional arm for attribution (cheap, same harness): **ARM-OLDREST** —
identical to the main arm but per_bond_rest_enabled=False. Reported always;
gates only the attribution as described.

## 5. Predictions (calibration, before data)

- Bond censuses clean (freeze works): 90%.
- Main arm ≥ 0.90: 40%; 0.75–0.90: 25%; < 0.75: 35% — the displace-14 probe
  moves carriers far outside their bond neighbourhoods; whether tension alone
  funnels them back through 14 units is genuinely open.
- ARM-OLDREST ≥ 0.75 (attribution risk): 25% — k=8 alone may already fix
  much of G154's slowness at spacing 6 where rest≈r_eq anyway.
- Verdict distribution: PASS 35%, PARTIAL 20%, NULL 30%, NULL-ATTRIB 10%,
  FAIL 5%.
- Most-likely failure mode: displaced carriers (14 units out) sit beyond any
  restoring bond's useful basin and drift or stall → NULL.

## 6. Budget (hybrid, §5)

Harness adaptation (flags + census + freeze + OLDREST arm): 45 min. Runs:
minutes. Verdict + LOGBOOK + FRONTIER (D10): 30 min.
**Realistic 1.5 h → hard cap 3 h.**

## 7. Out of scope

Efficiency/Hopfield-competitive claims (closed, G154), capacity beyond
8×3 patterns, multi-register interference, adaptive rest lengths, flux port.

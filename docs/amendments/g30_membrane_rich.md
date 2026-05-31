# G30 — A large closed membrane forms on the rich substrate (broad, non-8% band)

Pre-registered: 2026-05-31 (BEFORE the run). After G27 (widen the rule → rich
substrate), G28 (element-count ceiling lifted), G29 (can't delete the rule), test
whether the NEXT structural level composes: does a closed, stable membrane form on the
dense atom lattice — using a BROAD frequency band NOT centred on 8% (freq_ratio 0.05,
tolerance 0.045 → pairs 0.5–9.5 % apart), honouring "the 8 % rule is gone"?

Config: broad band, node_freq_binding=True, atom_valence=3, fusion_bond_block=2,
curvature_k=2.0, atom_repulsion_k=1.0, longer intermediate lifetimes, cap 2000, 250
ticks, seeds 42 & 7. Largest bridged atom component → sphere fit → shell-likeness +
enclosed interior vibrations + persistence.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| G30a | Large bridged membrane | component ≥ 50 atoms |
| G30b | Shell-like | σ_r/R < 0.35 (atoms lie on a sphere) |
| G30c | Encloses interior | ≥ 10 vibrations within 0.6·R |
| G30d | Persists | final size ≥ 0.6 × peak |

## RESULT (2026-05-31): PASS

| seed | component | σ_r/R | radius | interior vibrations |
|------|-----------|-------|--------|---------------------|
| 42 | 112 atoms | 0.277 | 10.9 | 179 |
| 7 | 110 atoms | 0.246 | 11.1 | 213 |

G30a–d all ✓ → **PASS**. A single connected bridged structure of ~110 atoms forms a
shell (σ_r/R ≈ 0.25–0.28 — atoms on a sphere surface), encloses ~180–210 interior
vibrations, and persists. This is BET-086's cell precursor at ~5–6× the scale (110 vs
15–34 atoms) — and it forms under the honest broad-band rule (0.5–9.5 % apart), NOT the
narrow 8 %.

## Honest scope
This is STRUCTURE at scale (Phase 3), not yet FUNCTION (no memory / selective
permeability / cognition demonstrated here). The interior count is within-0.6R free
vibrations; combined with the shell geometry it is a genuine enclosing membrane, though
some interior vibrations are ambient transit (see G24/G25 — passage is not yet gated in
the engine). The chain so far: widen the frequency rule (G27) → rich substrate → lifts
the element ceiling (G28) → a large closed membrane composes (G30). Next: selective
permeability (integrate the G25 rule into the engine) and the bridge/memory function on
this large lattice.

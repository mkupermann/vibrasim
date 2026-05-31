# G28 — The membrane/bridge element-count ceiling is lifted

Pre-registered: 2026-05-31 (BEFORE the run). The memory programme (BET-089..099) was
bounded by element count (~10–25 atoms / few bridges). Test whether, with the rich
binding regime + persistence (fusion_bond_block) + adequate capacity, the largest
connected bridged structure (membrane / memory precursor) grows far past that ceiling.

## RESULT (2026-05-31): finding — ceiling lifted (but the test still used the 8% rule)

Config: membrane machinery (atom_valence=3, fusion_bond_block=2, curvature_k=2.0,
atom_repulsion_k=1.0), cap 2500, 200 ticks, seeds 42 & 7.

| regime | seed | peak atoms | bridges | max bridged chain |
|--------|------|-----------|---------|-------------------|
| baseline 8% | 42 | 128 | 191 | **128** |
| baseline 8% | 7 | 110 | 163 | 106 |
| wide window (0.08±0.02) | 42 | 332 | 497 | 148 |
| wide window | 7 | 313 | 467 | **313** |

G28a ✓ (max_chain ≥ 30), G28c ✓ (bridges ≥ 40), G28b ✗ (wide not ≥ 2× baseline:
230 vs 117 mean) → NULL/partial on the strict bar.

**The real finding:** BOTH regimes now produce a SINGLE connected bridged structure of
100–313 atoms — far past the old ~10–25 ceiling. The structural ceiling that bounded
the memory programme is lifted by PERSISTENCE (fusion_bond_block keeps atoms alive) +
adequate capacity, with the binding window scaling the raw atom count. The old ceiling
was a small-scale / non-persistent artifact, not a hard limit.

**Honest correction (Michael):** this test still anchored on the 8% rule — both a
"baseline_8pct" arm and freq_ratio=0.08 in the wide arm. The directive was to drop the
8% rule entirely. Redone in G29 with NO frequency gate (proximity + polarity binding
only) to see what the substrate does without the rule at all.

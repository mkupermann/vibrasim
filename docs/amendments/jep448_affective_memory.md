# JEP-448 — Strong-energy connections become stronger: affective memory enhancement

## Motivation
Michael's model, verbatim: "mit Erfahrung werden die Verbindungen mit starker Energie immer
deutlicher und stärker" (connections carrying strong energy grow ever clearer and stronger). This is
**affective memory enhancement** — emotionally-charged memories are encoded more robustly than
neutral ones (Cahill & McGaugh 1998, amygdala-modulated consolidation). JEP-448 tests it with the
substrate's own machinery: a fact whose entity carries strong valence is stored with a higher binding
weight (the existing `add_fact(weight=)` superposition lever), so it survives interference better than
a neutral fact. Established (weighted VSA superposition → higher cleanup SNR; emotional-memory
phenomenon named), no new science. No transformer.

## Method (`tools/run_jep448_affective_memory.py`)
Single-module store (module_cap forced large so everything superposes → heavy interference). Store 30
EMOTIONAL target facts (entity valence ±2, weight = 1 + k·|valence|, k=1) and 30 NEUTRAL target facts
(valence 0, weight 1), then 300 interfering facts (weight 1) into the same module. Recall each target
(`query` cleanup) and score whether the right value is returned.
- **boost arm:** emotional facts weighted by |valence|.
- **control arm:** identical facts/interference but ALL weight 1 (no affect boost).
Seeds 0 & 7.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **J448a (affect enhances memory):** boost arm — emotional recall ≥ neutral recall + 0.15, both seeds.
- **J448b (it is the affect boost, not the content):** control arm — |emotional − neutral| ≤ 0.05,
  both seeds (without the boost the two are equivalent).
- **J448c (no net cost):** boost arm overall recall (emotional+neutral) ≥ control arm overall − 0.05,
  both seeds (enhancing emotional facts does not wreck the rest).

Predicted PASS: strong-energy facts are recalled more robustly under interference, and only because
of the affect-derived weight — the substrate realization of Michael's "strong connections grow
stronger." NULL if J448a fails (weight boost insufficient at this load). Bars locked; no retuning.
No transformer.

## RESULT (2026-06-05): **PASS** (prediction HIT)

| seed | BOOST emo | BOOST neu | CONTROL emo | CONTROL neu |
|------|-----------|-----------|-------------|-------------|
| 0 | 1.000 | 0.167 | 0.400 | 0.367 |
| 7 | 1.000 | 0.167 | 0.400 | 0.367 |

J448a ✓ (emo ≫ neu+0.15 in boost), J448b ✓ (control symmetric, |Δ|=0.03), J448c ✓ (boost overall
0.58 ≥ control 0.38) → **PASS, both seeds.**

## Verdict: strong-energy connections grow stronger (affective memory enhancement)
Facts whose entity carries strong valence, stored with an affect-derived weight, are recalled at
1.000 under heavy interference where neutral facts collapse to 0.167 — and the asymmetry is ENTIRELY
the boost (the control arm, identical facts at weight 1, is symmetric at ~0.38). This is the
substrate realization of Michael's "mit Erfahrung werden die Verbindungen mit starker Energie immer
deutlicher und stärker" — and of the emotional-memory-enhancement phenomenon (Cahill & McGaugh 1998).

**Honest tradeoff (and why it is realistic).** Boosting emotional facts pushes NEUTRAL recall DOWN
(0.367 → 0.167) in the same module — the strong bindings dominate the shared superposition. This is
not a flaw but the actual signature of emotional memory: vivid emotional events are retained at the
expense of mundane detail. Overall recall still rises (0.38 → 0.58) because the emotional gain
outweighs the neutral loss. Established (weighted VSA superposition; emotional-memory phenomenon),
named — the contribution is wiring affect → encoding strength in the substrate. No transformer.

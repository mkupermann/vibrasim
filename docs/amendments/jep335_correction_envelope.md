# JEP-335 — Correction reliability envelope: when does gate-override leak, and does compaction always fix it?

## Motivation
JEP-334 surfaced that correction-by-negation (gate-detected `not_isa` override, JEP-305) can LEAK at higher load —
the wrong positive fact slips through — while compaction (physical removal) is reliable. Quantify it: sweep load,
measure how reliably `is_a` respects a `not_isa` correction with gate-override vs after compaction. Tells us WHEN
compaction is needed for a long-lived corrected brain. No transformer.

## Method
Build stores with an increasing number of (wrong fact + its negation) corrections amid filler. For each load,
measure: (a) override-correction reliability — fraction of corrected `is_a(x, wrong)` that correctly return False
via gate-override; (b) the same AFTER `compact()`.

## Pre-registered bars (BEFORE the run)
- **J335a (compaction is reliable everywhere):** post-compaction corrected-answer reliability = 1.0 at EVERY load,
  both seeds (0, 7).
- **J335b (characterize the leak):** report the load at which gate-override reliability first drops below 0.95
  (the leak threshold) — a finding; if override never leaks in range, report that too.

Predicted outcome: compaction 1.0 throughout (J335a PASS); gate-override degrades as load rises (per JEP-334's
0.944 at ~67 facts) — leak threshold somewhere in the swept range. If override stays ≥0.95 throughout, JEP-334's
leak was a near-threshold fluke; report honestly.

## Result (seeds 0, 7): **PASS**
Override vs compacted correction reliability by load:

| corrections | facts | modules | gate-override | after compaction |
|-------------|-------|---------|---------------|------------------|
| 5  | 15  | 1 | 1.00 | 1.00 |
| 10 | 30  | 1 | 1.00 | 1.00 |
| 20 | 60  | 2 | 0.95 | 1.00 |
| 40 | 120 | 3 | 0.95 | 1.00 |
| 80 | 240 | 6 | 0.96 | 1.00 |

- **J335a:** post-compaction reliability = **1.0 at every load**, both seeds. **PASS.**
- **J335b:** gate-override is perfect at 1 module (≤10 corrections) and slips to **~0.95–0.96 once the store spans
  multiple modules** — it never drops below 0.95 in range (leak threshold >80 corrections). The JEP-334 0.944 was a
  near-threshold fluke around this ~0.95 plateau.

## Verdict: **PASS**
Compaction (physical removal) makes corrections reliable at EVERY load (1.0); gate-detected negation override is
~95–96% reliable once facts span multiple modules — good but not guaranteed. Practical rule for a long-lived
incrementally-corrected brain: **compact periodically** (e.g. on save) so corrections are physically applied rather
than relying on per-query override. Closes the JEP-334 correction-leak thread with a quantified envelope.
Established log-compaction + a reliability sweep, named as such; no transformer.


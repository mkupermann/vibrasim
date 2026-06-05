# JEP-400 — Abduction over read prose: "why?" phrasings + transitive causal chains

## Motivation
Probing the deeper inference operators on read prose: direct causal abduction works ("what causes cancer?" → smoking),
but (1) natural "why does X happen?" phrasing isn't parsed, and (2) abduction is single-hop — "what causes death?"
returns only the immediate cause (cancer), not the causal CHAIN (smoking → cancer → death). Extend abduction to parse
"why" phrasings and to trace the transitive causal ancestry (immediate + distal causes). Established method (abduction
over a stored inverse-causal graph; transitive closure of caused_by). No transformer.

## Method
- `BrainQuery.why(effect)` → trace the `caused_by` chain transitively (BFS over caused_by edges) and return all causes
  (immediate first), deduplicated.
- Parser: "why does X happen?" / "why X?" → `why(X)`; "what causes X?" also returns the chain.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: "why" phrasings parse to abduction, and the causal chain is traced (root causes surfaced), without
regressing direct single-cause queries.

- **J400a (why phrasing):** after reading "Smoking causes cancer. Cancer causes death." → "why does cancer happen?"
  mentions smoking; "why does death happen?" mentions cancer (and smoking via the chain), both seeds (0, 7).
- **J400b (transitive abduction):** "what causes death?" returns BOTH cancer AND smoking (immediate + root); for a
  3-link chain "A virus causes infection. Infection causes fever." → "what causes fever?" returns infection AND virus,
  both seeds.
- **J400c (no regression):** direct "what causes cancer?" → smoking (immediate cause present); `pytest -m "not slow"
  tests/test_conversation.py` passes.

If transitive tracing pulls in spurious causes or loops, report it (guard against cycles). Predicted clean. Bars fixed;
no retuning. No transformer.

## Result (seeds 0, 7): **PASS** (prediction HIT)
- **J400a (why phrasing): PASS** — "why does cancer happen?" → smoking; "why does death happen?" → "cancer, smoking"
  (the chain). Both seeds.
- **J400b (transitive abduction): PASS** — "what causes death?" → **cancer, smoking** (immediate + root); "what causes
  fever?" → **infection, virus** (3-link chain traced). Both seeds.
- **J400c (no regression): PASS** — "what causes cancer?" → smoking (direct cause present, ordered first);
  `tests/test_conversation.py` **10 passed**. Both seeds.

## Verdict: **PASS — deeper inference (abduction) composes over read prose, now transitive**
Abduction over read prose now parses natural "why does X happen?" questions and traces the causal CHAIN transitively
(BFS over the stored `caused_by` graph, cycle-guarded), surfacing both the immediate cause and the root cause in order
("what causes death?" → cancer, then smoking). Direct single-cause queries are unaffected and the suite is green. This
extends the validated reasoning from is-a/property/part-of into multi-hop causal abduction over real text — the deeper
inference operators compose over read prose, not just hand-built facts. Established method (transitive closure of an
inverse-causal graph); no transformer.

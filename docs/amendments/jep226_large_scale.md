# JEP-226 — large-scale multi-domain validation (+ an alphanumeric-name limitation, honestly caught)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the engine handles a large multi-domain KB (hundreds of concepts across all domains) efficiently (fast queries)
  and correctly — the ultimate scale+breadth validation. RISK: a query-time scaling issue from the relation-
  interaction is-a calls in loops.

## Result — PASS (HIT) on scale; + a genuine limitation + a test-design self-catch
FIRST RUN FAILED (2/8) — but NOT from scale: my test used DIGIT-containing concept names (c0, c1, ...), and the
engine's FIXED-relation extractors use an [a-z]-only concept regex, so they REJECT alphanumeric names (is_a/part/
causal/numeric all 0). The open-relation extractor (read_open, different parse) DID handle them. GENUINE LIMITATION
surfaced: alphanumeric/code-like concept names ('covid19', 'mp3', 'b2b') are not handled by the fixed extractors -
the engine targets letter-based natural-kind concepts; alphanumeric names are out of scope (a separate fix). TEST-
DESIGN SELF-CATCH: re-ran with LETTER-only names (3-letter base-26 codes).
SECOND RUN (the real scale test): read 475 sentences in 27ms -> is_a 229, part 49, causal 49, numeric 50,
comparison 49, temporal 49, open 30. 8/8 correct: deep is-a 200-HOP, part-of/causal/comparison/temporal 50-hop chains,
numeric, open relation, and a cross-domain negative -- all correct, the 8 queries (incl the 200-hop closure) in 1ms.
KB = 259 is-a concepts. So the engine SCALES to large multi-domain knowledge bases correctly and FAST (linear read,
sub-ms queries even at 200-hop). Prediction HIT (the scale claim held with a proper test); the first-run miss was a
test-design flaw that usefully surfaced the alphanumeric-name limitation. 90/90 regression tests green. Tally 114/141.
Established (transitive-closure scaling); named; no novelty.

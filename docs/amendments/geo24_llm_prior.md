# GEO-24 — Is the LLM's geometry a useful PRIOR for data-efficient structure learning? (when does it help?)

## Motivation
Everything so far uses geometry to READ the LLM (retrieval) or trains structure from scratch (TransE). The
deeper question: does LLM-INIT make learning a NEW structured relation more DATA-EFFICIENT than random init,
and does that depend on whether the relation correlates with semantics? Honest hypothesis: LLM-init helps
when the target structure aligns with semantic geometry (e.g. a taxonomy over related words), and does NOT
help when the structure is arbitrary (random pairing) — mapping WHEN geometry-over-an-LLM aids learning.

## Pre-registration (locked BEFORE run)
- Entities: 16 real animal words MiniLM knows.
- Relation A (SEMANTIC-aligned): a size-ordering "bigger_than" consistent with real-world size (mouse <
  cat < dog < horse ...) — plausibly correlated with embedding geometry.
- Relation B (ARBITRARY): a random fixed permutation ordering over the SAME words (no semantic meaning).
- For each relation, learn a 1-D-ordering embedding via margin ranking with k training pairs (k swept:
  4,8,16,32), init = {random, LLM-projected}. Test held-out pair ordering accuracy.
- Metric: ordering accuracy vs k, random-init vs LLM-init, for A and B. 3 seeds, report mean.
- Bars (descriptive map): (i) for A, LLM-init >= random-init + 0.10 at small k (prior helps); (ii) for B,
  LLM-init ~ random-init (no help — arbitrary structure uncorrelated with semantics). Honest either way.

PASS-as-designed if LLM-prior helps for semantic-aligned A but NOT arbitrary B (maps the condition). Report
all curves; a null (no help even for A) is a valid finding.

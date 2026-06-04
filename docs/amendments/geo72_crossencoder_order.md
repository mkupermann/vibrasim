# GEO-72 — Does a cross-encoder fix the word-order/compositional weakness?

## Motivation
GEO-71: mean-pooled bi-encoders are weak at word order (0.62-0.75), and it doesn't scale with size. The
prescribed fix (GEO-71) is a CROSS-ENCODER (jointly encodes query+fact, so it SEES word order). GEO-72 tests
whether the cross-encoder re-ranker resolves the compositional weakness on the clean 2-way order items.

## Pre-registration (locked BEFORE run)
- GEO-70b clean 2-way identical-bag word-order items.
- For each: cross-encoder scores (query, factA) vs (query, factB), pick higher.
- Compare to the bi-encoder baseline (0.75 MiniLM).
- Bar: cross-encoder >= 0.85 AND > bi-encoder. PASS validates the design rule (cross-encoder for
  role/word-order matching). NULL if it doesn't help.

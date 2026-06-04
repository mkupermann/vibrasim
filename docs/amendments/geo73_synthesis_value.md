# GEO-73 — Does the engineering SYNTHESIS beat naive bi-encoder RAG? (quantify the contribution)

## Motivation
The honest claim is that the contribution is the engineering SYNTHESIS (rerank + entity-resolution + symbolic
operators + abstention) over established parts. GEO-73 quantifies it: full system vs NAIVE bi-encoder RAG
(retrieve top-1, return it) on a realistic MIXED workload with the conditions each piece addresses.

## Pre-registration (locked BEFORE run)
- Mixed workload (12 queries): factoid, multi-hop, aggregation (count), a NOISY/typo'd entity reference, and
  unanswerable (should abstain). Known answers.
- NAIVE RAG: bi-encoder retrieve top-1 fact, return its object; never abstains; no operators; no entity-res.
- FULL system: entity-resolution (typos) + multi-hop chain + symbolic count + grounded abstention.
- Metric: accuracy on the mixed workload (unanswerable counts correct only if abstained). Bar: full >= 0.8
  AND full >> naive (by >= 0.3). PASS quantifies the synthesis value. NULL if naive matches it.

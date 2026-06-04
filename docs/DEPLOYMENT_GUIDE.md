# Geometric reasoning toolkit — safe deployment guide

Distilled from the EQMOD-3 programme (GEO-1..80). What the system is good at, where it fails, and how to
deploy it so it is trustworthy rather than confidently wrong. Read alongside `GEOMETRIC_ANSWER.md` (the full
honest characterization) and `tools/README_geometric.md` (usage).

## What it is (in one line)
A grounded neuro-symbolic QA toolkit: **LLM semantic matching** (resolves a query to the right stored fact)
+ **symbolic operators** (count/compare/join/negate/temporal/contradiction over the structured store) +
**grounding** (abstain when unsupported) + an optional small generator. A synthesis of established methods;
its value is making a small model reliable on YOUR facts (3x naive RAG, GEO-73).

## Use it for
- Grounded factual Q&A over your own structured facts or documents (it won't hallucinate facts not in the store).
- Multi-hop lookups, counts, comparisons, temporal/versioned queries, contradiction & ambiguity detection.
- Reliable factual answers from a SMALL/cheap model (GEO-79: grounding lifts a 0.5B model 0.17 -> 1.00).

## Do NOT use it for
- Causal "why" reasoning, open-ended prediction, or counterfactuals needing world knowledge — it does lookup
  + computation, not inference (GEO-75). Use the question-type guard to abstain on these (GEO-76).
- Open-domain questions outside your store — it abstains (good) but cannot answer them.
- Anything where a confidently-wrong answer is dangerous WITHOUT the safeguards below.

## THE critical caveat — grounding is double-edged (GEO-79/80)
Grounding amplifies retrieval BOTH ways:
- retrieval RIGHT -> a weak model becomes reliable (0.17 -> 1.00).
- retrieval WRONG -> a correct model becomes confidently wrong (0.90 -> 0.00; it follows the bad context 100%).
**So retrieval quality IS the system's accuracy.** Mitigate:
0. **The GIGO risk is narrow (GEO-81):** abstention catches COVERAGE gaps (queried entity absent -> low
   similarity -> abstains, 1.00). The real residual GIGO is a WRONG fact for the RIGHT entity (a store data-
   quality error) -> validate store correctness (conflict detection GEO-41/62, provenance). Then:
1. **Abstain on low confidence** — calibrate `abstain_tau` on a labelled dev split (GEO-23/32); never ground a
   weak retrieval. This is the essential safety net.
2. **Re-rank** — `rerank_k=10` (cross-encoder) recovers multi-hop accuracy at scale (GEO-40b) and fixes
   word-order/role matching (GEO-72); use it for prose and large stores.
3. **Entity resolution** — `resolve_entity()` (GEO-44) fixes typo'd/near-duplicate names that otherwise
   retrieve the wrong entity (noisy store 0.53 -> 1.00, GEO-43/44/45).
4. **Prefer extractive** — return the supporting fact (and let the user verify) over a generated answer when
   correctness matters; generation can amplify a wrong retrieval.
5. **Verify answerability** — focus-existence check (GEO-33) + question-type guard (GEO-76) reject in-domain-
   but-unanswerable and inference questions that a similarity threshold alone misses.

## Operating envelope (measured)
- **Latency:** ~7ms/query (~150 q/s), ~24ms with re-ranking; interactive to ~200k facts on CPU (GEO-63/64).
  Speed is NOT the scale limiter — retrieval PRECISION is.
- **Model:** a 17M embedder already does semantic matching (GEO-67); use all-mpnet-base-v2 for accuracy,
  all-MiniLM-L6-v2 for speed, paraphrase-multilingual-MiniLM-L12-v2 for cross-lingual (GEO-46).
- **Structured data:** exact and reliable (1.00). **Prose/documents:** retrieval-limited (~0.7-0.8), use
  re-ranking + multi-passage context; abstention keeps it honest (GEO-56/60/61).
- **Noise:** character typos x near-duplicate entities are the main failure (GEO-43); fix with entity
  resolution. Paraphrase is handled fine; near-duplicates with clean text are fine.

## The irreducible residual risk (GEO-82)
Most GIGO is mitigable: coverage gaps -> abstention; conflicting facts -> conflict detection; wrong PUBLIC-
knowledge facts -> optional LLM-prior fact-check (`gen` the question, compare to stored answer; catches errors
1.00 but FALSE-FLAGS private/updated facts 0.80, so use ONLY for public-knowledge stores). The ONE irreducible
residual: a single wrong PRIVATE fact with no conflicting fact — no automatic check can catch it (the LLM has
no prior to check against). Mitigation = data provenance/curation. Keep your store clean.

## The honest bottom line
This makes a small model trustworthy on YOUR facts — IF you keep retrieval clean and abstain when unsure.
It is a deployable engineering synthesis, not human-level AI and not a new method. Its biggest strength
(grounding) is also its biggest risk; the safeguards above are what make it reliable rather than confidently
wrong. Deploy with retrieval quality + abstention as first-class concerns.

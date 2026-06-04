# GEO-15 — Does relational geometry lift from WORDS to SENTENCES? (toward text understanding)

## Motivation
GEO-5–9 showed analogy/relation geometry on WORD embeddings. Real understanding is at the SENTENCE level.
GEO-15 asks: when facts are full templated SENTENCES embedded by a real LLM (MiniLM), (a) does retrieval-
by-geometry answer questions (question sits near its answer-fact), and (b) does a relation still form a
consistent OFFSET across sentences enabling analogy? This is the words->sentences lift toward text
understanding.

## Pre-registration (locked BEFORE run)
- 12 facts "The capital of <country> is <city>." for 12 known countries; 12 questions "What is the capital
  of <country>?". Embed all with MiniLM (normalized).
- (a) RETRIEVAL: each question's nearest fact (cosine) is its own country's fact. Bar: hits@1 >= 0.75
  (chance 1/12=0.08).
- (b) SENTENCE ANALOGY: relation offset = mean(fact - question) over a train split; on held-out, does
  question + offset land nearest the correct fact? Bar: hits@1 >= 0.6.
- Control: shuffled pairing must score ~chance.
- Both deterministic (one model); report raw numbers.

PASS if (a)>=0.75 AND (b)>=0.6 — relational geometry lifts to sentences. PARTIAL/NULL otherwise (record which).

## Result
| metric | value |
|--------|-------|
| (a) retrieval question->fact hits@1 | **1.00** (chance 0.08) |
| shuffled control | 0.00 |
| (b) sentence analogy via offset hits@1 | **1.00** |

**VERDICT: PASS** — relational geometry lifts cleanly to the SENTENCE level on real LLM embeddings. Both
geometric retrieval (question lands nearest its answer fact) and the offset-analogy structure (relation is
a consistent translation across sentences) hold at 1.00, control at chance. The words->sentences lift works;
the geometric method operates on full natural-language sentences, not just words.

# GEO-16 — Multi-hop UNDERSTANDING by iterative geometric retrieval (generator-free)

## Motivation
GEO-15: single-fact retrieval/analogy works at sentence level. Real understanding answers questions NO
single fact answers, by CHAINING facts. GEO-16 tests multi-hop QA via iterative geometric retrieval (a
real RAG pattern, but with NO LLM generator — pure geometry over an LLM-embedded fact store): retrieve hop
1, extract the bridge entity, retrieve hop 2, read the answer.

## Pre-registration (locked BEFORE run)
- 10 people: "<Person> works at <Company>." and 10: "<Company> is headquartered in <City>." (20 facts).
- Question: "Which city does <Person> work in?" Answer = the city via Person->Company->City.
- Method: embed all facts + question (MiniLM). Hop1: retrieve nearest 'works at' fact -> bridge Company.
  Hop2: build probe "<Company> is headquartered in" , retrieve nearest 'HQ' fact -> City. Score = correct
  city.
- Bars: 2-hop accuracy >= 0.7 (chance 1/10). Single-hop control (answer directly from question, no chain)
  must be LOWER (the chain is necessary). Distractor companies present.

PASS if multi-hop >= 0.7 AND chain beats no-chain. NULL/PARTIAL otherwise.

## Result
| metric | value |
|--------|-------|
| multi-hop (chain) accuracy | **1.00** (chance 0.10) |
| no-chain direct control | 0.10 |

**VERDICT: PASS** — multi-hop understanding by iterative geometric retrieval works perfectly and the chain
is NECESSARY (no-chain control at chance). Generator-free reasoning: retrieve hop-1 fact -> symbolic bridge
entity -> probe hop-2 -> answer. A real RAG pattern with NO LLM generator, just geometry over an LLM-
embedded labeled fact store. Arc established: words (GEO-5–9) -> sentences (GEO-15) -> multi-hop reasoning.

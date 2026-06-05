# JEP-181 — the MATURED read() on the full Boole text: the genre gate, conclusively

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 matured read() extracts MORE raw facts than JEP-155's 326 (more handlers fire), but precision for genuine
  knowledge stays low — the genre gate holds even with the best extractor. RISK: most extractions are artifacts.

## Result — MISS on quantity (FEWER, not more); core genre-gate claim CONFIRMED
Ran the full matured read() (copula, has, located-in, relative-clause, negation, multi-relation, all guards) on the
entire Boole text (5446 lines): 24 is-a + 27 part-of + 1 causal = 52 facts — FEWER than JEP-155's 326 loose-Hearst
candidates. PREDICTION MISS (direction): I predicted MORE, forgetting the matured extractor's bare-NP + valid-concept
guards are STRICTER (precision-focused), so on wrong-genre text it extracts FEWER, not more (more handlers but
tighter guards net fewer). CORE CLAIM CONFIRMED: the 52 facts are almost entirely logic/philosophy ARTIFACTS, not
genuine natural-kind taxonomy — variable assignments ('x = matter IS-A necessary being', '3 IS-A definition', 'b
IS-A probability', 'hence c IS-A probability'), philosophical predications ('nature IS-A point', 'virtue IS-A
argument a fortiori'), clause fragments ('we may hence infer IS-A priori'), and trivial head-noun links ('perpetually
recurring phenomenon IS-A phenomenon', 'necessary being IS-A being' — the adjective-modified-NP -> head-noun rule
firing on philosophical phrases). GENUINE encyclopedic-knowledge yield: ~0. So the GENRE GATE is conclusive: even the
BEST no-transformer extractor gets near-zero genuine knowledge from Boole (logic/argument prose), and a stricter
extractor extracts FEWER candidates on wrong-genre text (a precision/recall tradeoff). The learn-from-sources path
requires encyclopedic-register text (real corpus = the open frontier needing authorization), NOT a better extractor
on Boole. Prediction MISS (quantity direction); tally 70/97. Lesson: a more PRECISE extractor extracts FEWER on
out-of-distribution text, not more. Established (lexico-syntactic extraction, precision/recall tradeoff); named; no novelty.

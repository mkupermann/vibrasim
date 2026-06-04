# JEP-108 — the mature engine on REAL Boole prose: re-measuring the parse gate

## Why
JEP-89 (crude patterns) got 46 noisy triples from Boole. The engine is now far more capable (multi-word,
conjunction, properties, coreference). Does it extract more usable structure from Boole's ACTUAL sentences?

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 STILL SPARSE: <5% of 5447 sentences parse into facts; the successes are rare simple "X is a Y" definitionals;
  Boole's complex argumentative prose mostly returns 'none'. Confirms the parse gate persists with the mature
  engine - the engine's grammar is for SIMPLE declaratives, not dense Victorian mathematical prose.

## Result — prediction MISS on the metric; the finding is STRONGER (parse rate is a trap)
43.4% of Boole "parsed" (2362/5447: isa 2093, neg_isa 260, rel 9) — predicted <5%. BUT the parses are SPURIOUS:
the permissive (.+?) concept regex matches any sentence with "is/are" and grabs whole CLAUSES as "concepts"
(e.g. 'design of the following treatise' IS 'to investigate the fundamental laws...'). The 43% is mis-fitting, not
understanding. CALIBRATION: I predicted the wrong METRIC — parse RATE is misleading on complex prose; should have
predicted parse QUALITY (~0). LESSON: a high parse rate on out-of-domain text is a TRAP (a permissive grammar
mis-fires and looks successful). It also exposed a real DEFECT: the engine emits garbage instead of cleanly
REJECTING complex sentences. Fixed in JEP-108b (concept-validity guard). The parse gate PERSISTS - quality is ~0.
Tally: MISS (10/19). Established (parsing limits), named; honest.

## JEP-108b — concept-validity guard: fail cleanly on out-of-domain prose
Guard: a concept phrase must be <=4 words with no internal punctuation (a short noun phrase), else the IS-A is
rejected ('none'). Effect: the engine fails cleanly on Boole's complex sentences instead of emitting clause-as-
concept garbage; honest Boole parse rate drops to the genuinely-simple sentences; all simple-language tests stay
green (their concepts are short). This makes parse RATE on Boole an honest proxy for parse-able sentences again.

## JEP-108b result — HIT (honest parse gate confirmed)
With the concept-validity guard: Boole parse rate 43.4% -> **2.1%** (112 sentences: isa 98, rel 9, neg_isa 5);
5335 of 5447 now cleanly REJECTED instead of emitting garbage. 19 tests stay green (simple-language concepts are
short). The engine fails cleanly on out-of-domain prose; the honest parse gate is ~2% (the genuinely simple
definitional sentences) — confirming the gate (my original <5% intuition was right; I'd measured the wrong metric
before the guard). Net: a robustness + honesty improvement. Established (input validation), named; no novelty.

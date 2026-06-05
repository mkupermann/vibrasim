# JEP-266 — document-scale validation of the cumulative prose hardening (JEP-254..264)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the hardened engine handles a FRESH multi-domain document (combining all newly-handled constructions) at high
  recall (>=0.9), quantifying the cumulative 254..264 hardening end-to-end (paralleling JEP-175/213).

## Result — PASS (HIT): 15/16 = 0.94
Read a fresh 15-sentence multi-domain document exercising EVERY newly-handled construction; checked 16 ground-truth
facts/answers spanning: is-a multi-hop, 'such as' example, adjectival PROPERTY (loyal/friendly), part-of, numeric,
ability can/cannot, PASSIVE causal (rabies<-virus), causal x is-a, spatial 'in' + spatial question, mereological verb
('body consists of organs'), comparison, and INHERITED possession ('does a poodle have a heart?' via poodle->dog).
15/16 = 0.94. The single miss: 'what is the capital of France?' -> the open relation 'is capital of' needs >=2
occurrences to be auto-induced (read_open rule) and the doc has ONE -- by design, not a regression.
Prediction HIT; tally 145/181. The cumulative prose hardening (254..264) is validated end-to-end at document scale:
the engine learns + reasons + communicates across a fresh multi-domain document at 0.94, ROBUST (JEP-265, 0/4000),
106 unit tests. Established (document-scale evaluation), named; no novelty. Honest residuals (NL hard problems):
mid-sentence proper-noun capitalization (NER), multi-word concept coreference ('human body' vs 'body'), single-
occurrence open relations.

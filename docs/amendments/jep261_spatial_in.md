# JEP-261 — spatial containment 'X is in Y' (extraction + question routing)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 geography QA showed 'France is in Europe' induced as a generic OPEN relation 'is in', and the questions 'is X in
  Y?' / 'is X located in Y?' mis-parsed as is-a -> unknown. Adding plain 'is in' to the spatial-containment extractor
  (-> part-of) + routing the spatial questions to part_of fixes both; exclude 'is in' from read_open (now fixed).

## Result — PASS (HIT)
The spatial extractor handled 'located/situated/found in' but NOT plain 'X is in Y', so 'France is in Europe' leaked
to open; and respond() had no spatial-question handler, so 'is France in Europe?' parsed as is_a(France,'in europe').
Three changes: (1) added '|in' to the spatial-containment alternation ('X is in Y' -> tell_part, part-of); (2) added
a spatial question handler 'is X (located/situated/found) in Y?' -> part_of; (3) excluded 'is in/on/at' from read_open
(spatial is fixed, not open).
- 'France is in Europe. Paris is located in France.' -> part-of france->europe, paris->france.
- 'is France in Europe?' -> 'Yes. France is in Europe.'; 'is Paris located in France?' -> 'Yes...'; TRANSITIVE
  'is Paris in Europe?' -> Yes (Paris->France->Europe). 'is Italy in Asia?' -> No.
- No redundant open 'is in'; genuine open 'is capital of' still induced + answered ('Paris.'). is-a unaffected.
102/102 -> 103/103 regression tests green (+1). Prediction HIT; tally 140/176. Established (spatial-containment
mereology, JEP-167/150), named; no novelty. Residue: 'a paris' (sentence-start proper noun) is the known NER wall.

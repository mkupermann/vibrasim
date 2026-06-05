# JEP-276 — 3+ item comma list of SUBJECTS ('Dogs, cats, and horses are mammals')

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 a list QA pass showed 'Dogs, cats, and horses are mammals' captured only 'horses' (the copula split subjects by
  ' and ' only, so 'dogs, cats,' -- with commas -- failed bare_np). OBJECT lists already split on comma+and and work.
  Splitting subjects by comma AND 'and' fixes it; 2-item 'X and Y' and single subjects unaffected.

## Result — PASS (HIT)
The copula subject split was `re.split(r"\s+and\s+", ...)` (' and ' only); a 3+ item list 'Dogs, cats, and horses'
left 'dogs, cats,' as one non-bare-NP subject -> dropped. Changed to split on comma AND 'and':
`re.split(r"\s*,\s*and\s+|\s*,\s*|\s+and\s+", ...)`.
- 'Dogs, cats, and horses are mammals.' -> dog, cat, horse all is-a mammal; 'is a cat an animal?' -> Yes (transitive).
- 'Iron, copper, and gold are metals.' -> iron, copper, gold all is-a metal.
- 2-item 'Robins and sparrows are birds' + single subjects unaffected (no regression).
113/113 -> 114/114 regression tests green (+1). Prediction HIT; tally 155/191. Established (coordinated-NP list
parsing), named; no novelty. Residue: 'an iron is metal'/'a copper' (mass-noun-as-list-item article -- the usage-
countability heuristic only marks bare SUBJECTS, not list items) -- answer correct, only the article.

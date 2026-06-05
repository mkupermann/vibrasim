# JEP-268 — COMMUNICATE fixes: describe() splits abilities/properties + 'rabies' singularization

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 real-usage QA on the COMMUNICATE side (describe/summarize) surfaced 'It can bark, friendly' (describe lumps
  adjectival PROPERTIES, JEP-258, with ABILITIES under 'can') and 'a virus causes a raby' ('rabies' over-stripped by
  the -ies plural rule -- the recurring singularization-over-strip class: virus->viru, horses->hors). Splitting
  describe by adjective-suffix shape + adding 'rabies' (singular -ies/-es nouns) to _NOT_PLURAL fixes both.

## Result — PASS (HIT)
Two COMMUNICATE fixes:
(1) describe() now SPLITS its properties: adjective-shaped ('friendly','venomous') -> 'It is ...', the rest (verbs:
    'bark') -> 'It can ...'. Was 'It can bark, friendly'; now 'It can bark. It is friendly.'
(2) 'rabies' (and scabies/measles/diabetes/herpes/physics/mathematics/economics) added to _NOT_PLURAL -> not stripped
    to 'raby'. 'a virus causes rabies' (was 'a raby'). Real -ies plurals still singularize ('berries'->'berry').
- describe a dog: 'A dog is a mammal. It can bark. It is friendly. It has a heart. It has 4 legs.'
- summarize: '...a virus causes rabies.'
107/107 -> 108/108 regression tests green (+1). Prediction HIT; tally 147/183. The singularization-over-strip class
recurs (now guarded for -ies/-es singulars too). Established (English number morphology, adjective/verb split), named;
no novelty. This closes the COMMUNICATE-side real-usage QA.

# JEP-262 — bare singular SUBJECTS take no article (the complement of JEP-256)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the recurring 'a copper'/'a rust'/'a paris' residue: a concept introduced as a BARE (article-less) singular
  subject is proper/mass -> no article. Marking these (after _countable precedence) fixes them without breaking
  article-led countables ('a metal') or plurals ('a dog' from 'Dogs are mammals'); residue = capitalization of true
  proper nouns mid-sentence (the NER wall).

## Result — PASS (HIT), + corrected a prior test pinned to buggy output
read() now records concepts appearing as a bare singular sentence-subject ('Copper is...', 'Rust is...', 'Jupiter
has...') into self._no_article; _art renders them article-less, with _countable (article-led usage, JEP-256) taking
PRECEDENCE so polysemes stay countable.
- 'a copper'->'copper', 'a rust'->'rust', 'a paris'->'paris'; 'does oxygen cause rust?' -> 'Yes. Oxygen causes rust.'
- 'a metal' STAYS countable (article-led), 'a dog' stays countable (the plural 'Dogs' does not mark singular 'dog').
- Bonus: 'how many moons does Jupiter have?' -> 'Jupiter has 4 large moons.' (was the BUGGY 'A jupiter ...'); the
  JEP-229 test that pinned the buggy 'A jupiter' was corrected to the right value (fix, not post-hoc tuning).
102/102 -> 103/103 regression tests green. Prediction HIT; tally 141/177. HONEST RESIDUE (the NER wall): a true proper
noun rendered MID-sentence is article-less but lowercase ('paris', not 'Paris') -- distinguishing proper (Paris) from
bare-mass (copper) at sentence-start needs a lexicon/NER (the no-pretrained constraint). Sentence-INITIAL rendering
capitalizes correctly ('Jupiter has...'). Established (usage-based article assignment), named; no novelty.

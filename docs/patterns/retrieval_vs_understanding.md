# Pattern: the retrieval -> understanding ladder (JEP-83..88), and where it actually breaks

A substrate (or any system) trained on text climbs a ladder; each rung is a different capability, and it is easy to
mistake a lower rung for a higher one. Measured on real text (Boole's "Laws of Thought") with substrate-legal,
no-transformer methods.

## The rungs
1. **Vocabulary geometry (PASS, JEP-83/86).** Distributional co-occurrence (HDC/Random Indexing) makes related
   words similar: NN(truth)=falsehood, NN(probability)=event. Real, learned from the corpus alone. This is NOT
   understanding — it is word geometry.
2. **Retrieval (PASS, JEP-83/86).** Bag-of-words similarity returns relevant passages (86% vs 34% random control).
   Useful, but it RE-RANKS the source's own sentences.
3. **The bag-of-words ceiling (NULL, JEP-87).** Asked to tell TRUE from FALSE statements built from the SAME words
   (binding swapped), bag-of-words scores them IDENTICALLY (5/5 exact ties). It encodes vocabulary, not meaning.
   This is the precise line where retrieval stops and understanding would begin.
4. **Structure breaks the ceiling (PASS, JEP-88).** VSA role-binding (cconv(SUBJ,s)+cconv(REL,r)+cconv(OBJ,o))
   makes who-plays-which-role matter, so it separates the same-bag true/false pairs 5/5 that bag-of-words tied.
   Binding is a substrate primitive (JEP-66). This is the MECHANISM that gets past the ceiling.
5. **Inference over structure (PASS, JEP-84).** Transitive closure over bound facts answers multi-hop questions
   never stated in the source (1.00) where bare retrieval is at chance (0.43).

## Where it ACTUALLY breaks (the honest gate)
Rungs 4-5 assume the text has been PARSED into (subject, relation, object) roles, and that the facts are curated/
correct. The parse is the bottleneck: classic non-ML extraction (Hearst patterns) hits F1 0.85 but multi-hop
inference collapses to 0.65 because ONE missing edge breaks every chain (JEP-85). And the structure itself is
hand-given, not LEARNED unsupervised (JEP-69/70 NULL). So: the mechanisms of understanding (binding + inference)
WORK given structure; turning real prose INTO reliable structure, and LEARNING that structure, is the open
frontier. Don't mistake rung 2 (retrieval) for rung 5 (understanding) — they look similar and are not.

## The discipline that caught it
JEP-87 first reported 0.90 separation (apparent comprehension). On inspection the false statements used rarer
vocabulary — a test-construction confound. A fair same-bag control gave 5/5 exact ties. The apparent PASS was
honestly flipped to NULL. Measure with matched controls, or you will read vocabulary as meaning.

## Learn-from-sources, end to end (JEP-155..157b) — where it works, and the universal insight's third home
The "learn from real prose and understand" goal, mapped to a concrete working pipeline + its precise limits.

### The parse gate is the GENRE, not the extractor (155/156)
- Dense logic/philosophy prose (Boole) yields almost NO genuine taxonomy even with classic Hearst patterns ('X is a
  kind of Y', 'Y such as X'): 326 raw candidates but ~0 genuine — they are clause fragments and property/identity/
  philosophical predications. Boole is the WRONG genre (it presupposes grounding; it argues, it doesn't describe).
- CONTROLLED MINIMAL PAIR (156): the SAME Hearst + bare-NP-subject extractor gets precision 0.87 / recall 0.93 on
  encyclopedic prose (Simple-Wikipedia register) vs ~0 genuine on Boole. GENRE is the causal variable, conclusively.
- The bare-NP subject guard (short NP: optional quant/article + <=2 adjectives + head noun; NO conjunctions, prepo-
  sitions, or clause markers) is what makes pattern extraction precise — it rejects the clause fragments that the
  bare _valid_concept guard (<=4 words) lets through. This is the JEP-108 'predict QUALITY not RATE' lesson: a high
  raw match count on complex prose is a precision trap.

### End-to-end learn-from-prose -> multi-hop UNDERSTANDING works (157)
Feed the extracted taxonomy into the engine; it answers CROSS-SENTENCE multi-hop is-a (e.g. 'a poodle is an
organism' — depth-4, stated in NO single sentence) at 1.00 via transitive closure, while bag-of-words retrieval gets
0.00 beyond co-occurring (depth-1) pairs. This is the retrieval-vs-understanding line, demonstrated END-TO-END from
real prose, NO transformer. The learn-from-sources recipe: encyclopedic register + Hearst + bare-NP guard + the
engine's parse->bind->infer.

### The universal compounding/aggregation insight, third manifestation (157b)
Under realistic extraction NOISE (~13-25% edge error), multi-hop is-a DEGRADES with hop-DEPTH (a depth-k fact needs
all k extracted edges correct ~ (1-p)^k: noise0.25 d1 0.79 -> d4 0.51), and REDUNDANCY (each link restated -> more
extraction chances) ERROR-CORRECTS (x3 -> 0.97). This is the SAME chaining-vs-aggregation insight that governs
structure LEARNING and multi-hop REASONING — now in the learn-from-PROSE pipeline. ONE principle across all three:
chained inference compounds errors; redundant aggregation cures it. CALIBRATION LESSON (157 MISS): a noise-dependent
effect cannot show in a noise-free experiment — match the TEST REGIME to the predicted MECHANISM.

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

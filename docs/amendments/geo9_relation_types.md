# GEO-9 — Relation-type boundary map (what the geometric method learns)

## Result (MiniLM, 5-shot offset, held-out, ranked among full union vocab)
| relation type | hits@1 |
|---------------|--------|
| capital (encyclopedic) | 1.00 |
| plural (morphological) | 1.00 |
| past tense (morphological) | 1.00 |
| comparative (morphological) | 1.00 |
| is_a / hypernym (taxonomic) | 0.92 |
| gender | 0.88 |
| **antonym** | **0.54** |

## Finding — the honest scope of geometric few-shot relation learning
The offset method learns morphological, encyclopedic, taxonomic, and gender relations strongly (0.88–1.00),
but ANTONYMY is the weak point (0.54) — a known limitation: antonyms occur in similar contexts so they sit
CLOSE in embedding space, making the relation a noisy direction rather than a clean translation. So the
method's scope: relations that are ~consistent translations in LLM space (most syntactic + many semantic);
it degrades for relations defined by opposition/negation. This is the honest boundary of the geometric+LLM
learning method. (Consistent with the word-embedding analogy literature.)

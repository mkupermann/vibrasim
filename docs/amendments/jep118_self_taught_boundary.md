# JEP-118 — where self-supervised learning BREAKS: the honest boundary of the self-taught pipeline

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 self-taught is-a accuracy DEGRADES as perceptual overlap rises (sigma up -> clusters mix -> wrong names ->
  wrong taxonomy) and as ambient super-class word frequency falls; below 0.8 in the hard regime. Maps the limit.

## Acceptance (characterization)
- Report the accuracy surface over (sigma, super-word-freq). The degradation IS the finding (the favorable regime
  of JEP-117 is not universal). Established (clustering + cross-situational learning under noise), named; no novelty.

## Result — calibration MISS; an HONEST correction to JEP-117
Sweep (self-taught is-a accuracy):
| sigma\freq | 0.6 | 0.2 |
|------------|-----|-----|
| 0.35 | 1.00 | 0.00 |
| 0.8  | 1.00 | 0.00 |
| 1.5  | 1.00 | 0.00 |

Prediction MISS: I predicted perceptual OVERLAP (sigma) would break it — it does NOT (1.00 even at sigma=1.5; the
superclass signal dominates, clustering is robust). The breaking factor looked like super-word FREQUENCY, but the
verified MECHANISM is deeper: **PMI SATURATES for any word EXCLUSIVELY associated with a cluster** — P(w,cl)=P(w)
=> PMI = log(1/P(cl)), IDENTICAL for the superordinate ('bird') and a basic-level word ('robin', also exclusive to
the bird branch). So co-occurrence-with-cluster CANNOT distinguish hierarchy LEVELS; the super-naming is an
arbitrary tie-break. **This corrects JEP-117 honestly: its super-naming 1.00 was partly LUCK (tie-breaking), not
robust learning.** This is a real, known issue (why child word-learning needs the taxonomic/basic-level
constraints, Rosch/Markman). PRINCIPLED FIX (JEP-118b): assign each word to the granularity where its PMI is
MAXIMAL — 'robin' peaks at the sub-cluster (log 4 = 1.39 > log 2 at super), 'bird' peaks at the super-cluster —
separating levels robustly. Tally MISS (19/30). Established (PMI properties, cross-situational learning limits),
named; no novelty.

## JEP-118b — fix: assign words to their best-fitting granularity (level separation)
My PMI-max granularity fix FAILED: 0.00 everywhere (WORSE than naive's 1.00 at freq=0.6). Diagnosis: superordinate
words ALSO tie — 'bird' has PMI ~0.69 at the super-cluster AND ~0.69 at each sub-cluster it spans (it's split, not
exclusive, at the sub level), so "assign to max-PMI granularity" sent 'bird' to a sub-cluster, leaving the
super-cluster UNNAMED -> 0.0. PMI saturation is more pervasive than I assumed. The CORRECT criterion (not
implemented here) is LCA-of-extension: a word names the SMALLEST cluster that contains (almost) all of its
referent-instances ('robin' -> robin-sub; 'bird' -> the super-cluster, the lowest cluster containing all birds).
HONEST OUTCOME: a SECOND calibration miss (my fix didn't work). The valuable, honest result stands: PMI-based
cross-situational naming UNDERDETERMINES hierarchy LEVELS; JEP-117's superordinate naming was fragile/lucky, while
the INSTANCE->basic-level naming (JEP-116) is robust (basic-level words ARE exclusive to their tight cluster, so
PMI works). Recorded as-is; no claim of a working fix. Tally 19/31. Established (cross-situational learning limits;
the taxonomic/basic-level constraints exist precisely because co-occurrence underdetermines level), named.

## JEP-118c — LCA-of-extension naming: PARTIAL (the correct criterion; genuine data limits remain)
LCA-of-extension (a word names the smallest cluster with coverage>=0.7 AND specificity>=0.7 over its instance
extension) — self-taught is-a accuracy:
| sigma\freq | 0.6 | 0.2 |
|------------|-----|-----|
| 0.35 | 1.00 | 0.00 |
| 0.8  | 1.00 | 0.00 |
| 1.5  | 0.74 | 0.00 |

PARTIAL. The LCA criterion is the CORRECT one and works at adequate super-word frequency (1.00 at freq 0.6, low/mid
sigma) — fixing JEP-118b's total failure. Two GENUINE limits remain: (1) freq=0.2 still 0.00 — the superordinate
word is heard too rarely, so its extension covers <70% of the super-cluster (coverage too sparse). This is a real
EXPOSURE limit, not a method flaw (you can't learn a word you barely hear). (2) sigma=1.5 drops to 0.74 — at extreme
perceptual overlap the clustering itself starts to fail (so overlap DOES matter at the extreme, partly vindicating
JEP-118's original instinct). HONEST ENVELOPE of self-taught hierarchical learning: it works given ADEQUATE
superordinate-word exposure AND sufficiently DISTINCT concepts; it fails on rare super-words or heavy concept
overlap. The basic/instance level (JEP-116) is robust; the superordinate level needs more data. Calibration: PARTIAL
(predicted >=0.9 everywhere). Established (extension-based naming, the taxonomic constraint), named; no novelty. This
4-rung arc (117 capstone -> 118 honest correction -> 118b failed fix -> 118c principled-but-bounded fix) is the
discipline characterizing a frontier honestly: a fragile success, corrected, a failed fix owned, then the real
criterion and its real limits.

# GEO-29 — Is the compositional zero-shot gap (GEO-28) fundamental or recoverable?

## Motivation
GEO-28: conjunction of two zero-shot attributes collapsed to chance. But that test was under-powered (8
unseen, rare positive class, no calibration). GEO-29 asks whether composition RECOVERS with (a) more
entities (denoise per-attribute scores) and (b) a BALANCED conjunction target. If it recovers, the gap is
practical (data/noise); if it stays at chance, it is a more fundamental limit of composing noisy zero-shot
scores.

## Pre-registration (locked BEFORE run)
- 40 synthetic-but-LLM-resolvable items: animals with size-rank + a second attribute that MiniLM encodes
  (aquatic vs land, a clean semantic split). 24 seen / 16 unseen.
- Target: "large AND aquatic" with a BALANCED design (size median split; aquatic ~half) so the positive
  class is ~25-35%, not rare.
- Learn size-score (ranking) + aquatic-score (mean-diff) on seen; compose on unseen. LLM vs random init, 5
  splits.
- Bars: composition recovers if LLM composite bal-acc on unseen >= 0.70 AND >= random + 0.20. If still
  < 0.65, the compositional limit is confirmed as more fundamental. Report per-attribute too.

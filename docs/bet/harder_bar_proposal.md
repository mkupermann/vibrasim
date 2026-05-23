# Harder-Bar Proposal — T6/T7/T8/T9

**Status:** DRAFT — not pre-registered, not queued, awaiting operator decision.
**Trigger:** BET-006 + BET-007 hostile-reader meta-finding (LOGBOOK
2026-05-23 ~20:50). The locked 5/5 bar (T0-T5) was met by two
architecturally orthogonal substrates trivially. The bar measured the
minimum demonstration, not the research goal.
**Pre-registration discipline:** these new tests apply to FUTURE
iterations only (BET-009+). They do not retroactively change BET-006/007/008
verdicts. Post-hoc threshold tuning of the locked bar is forbidden.

## What the locked bar measured (and didn't)

| Test | What it measures | Trivial-pass mechanism |
|------|------------------|------------------------|
| T0 | spatial std > 0.05 | bimodal visited/unvisited cells |
| T1 | KL init vs eng > 0.1 | any non-zero post-training state |
| T2 | KL eng vs wn > 0.1 | encoder discriminates EN/WN already |
| T3 | T1+T2 at half corpus | same as T1+T2 |
| T4 | held-out precision > 0.3 | SOM's BMU maximises cosine by construction |
| T5 | retention >= 50% | no decay rule means trivial 100% |

None of T0-T5 directly tests:
- predictive capability
- fine-grained acoustic structure
- catastrophic-forgetting resistance
- emergent organisation beyond the encoder

## Proposed harder tests

### T6 — Predictive bit-rate

The substrate must predict the next chunk's features from a sliding
window of recent chunks better than chance.

  - Protocol: train substrate on first 70% of corpus. For each chunk
    in the held-out 30%: from the substrate state, predict the next
    chunk's 10-D feature vector. Compute MSE.
  - Negative control: same protocol on a fresh (untrained) substrate.
    Compute MSE.
  - Bar: trained-MSE < 0.5 * untrained-MSE (50% reduction).
  - Why "harder": absorbing sensor distributions alone does not enable
    prediction. The substrate needs temporal structure or a query
    interface that produces prediction-relevant output. Neither
    cog_map nor SOM has this out of the box.

### T7 — Fine-grained acoustic discrimination

The substrate must discriminate sub-classes within EN audio (not just
EN-vs-WN macro-discrimination).

  - Protocol: split R-7 corpus into two acoustically-distinct
    sub-segments (e.g., first 50% vs second 50% — likely different
    speakers/topics). Train substrate on first sub-segment. Compute
    histogram-KL between sub-1-trained substrate and a fresh substrate
    that trained on sub-2 only.
  - Bar: KL(sub-1 vs sub-2) > 0.1 with a NULL of KL(sub-1 vs sub-1-shuffled-time)
    where the shuffled-time control should give KL ≈ 0 if substrate
    is purely distribution-absorbing.
  - Why "harder": both sub-segments are EN, same speaker family, same
    encoder. The only signal is fine acoustic structure within EN.

### T8 — Catastrophic-forgetting resistance

Train on class A, then on class B, then check whether the substrate
still discriminates A from a fresh-A class.

  - Protocol:
    1. Train substrate S on EN audio for N ticks. Save state_A.
    2. Continue training S on WN audio for N ticks. (no reset)
    3. Compare S to a fresh substrate trained on EN audio for N ticks
       — the fresh comparison.
    4. KL(S vs fresh_A) should be small if A-knowledge survived.
  - Bar: KL(S vs fresh_A) < KL(fresh_B vs fresh_A) (i.e. S is closer
    to its origin-class than to the interfering class).
  - Why "harder": tests whether learning is destructive or additive.
    cog_map at beta=0 stores running means per cell; new visits to a
    cell overwrite the old mean. Class B visits to cells previously
    visited by class A would destroy A-knowledge. So cog_map would
    FAIL this test — that is the discriminating power.

### T9 — Emergent organisation

The substrate's cell organisation must reflect acoustic categories the
encoder cannot directly see (i.e., emergent structure beyond
encoder-arithmetic).

  - Protocol: train substrate on R-7 corpus. Cluster the cells by their
    final mu/w values. Measure cluster-quality (silhouette score) on
    a 2D dimensionality reduction of the cell positions.
  - Negative control: same protocol with cells visited in random order
    (destroys any topology learning). Compute silhouette.
  - Bar: trained-silhouette > 2 * shuffled-silhouette.
  - Why "harder": tests whether the substrate produces a USEFUL
    organization, not just any organization.

## Operator-decision questions

The operator returns ~2026-05-25 20:30 and should decide:

1. **Accept the locked-bar WIN as the wager outcome?**
   - The contract said 5/5 PASS. Two substrates passed 5/5. Per the
     contract, this is WIN. Confirming this consumes the wager.
   - Alternative: declare WIN at locked bar AND propose harder bar.

2. **Apply the harder bar (T6-T9) to follow-up iterations?**
   - YES → queue BET-009 implementing T6-T9, run cog_map beta=0 and
     SOM through it. If either passes, that is a much stronger
     scientific claim. If neither passes, the cog_map / SOM bar-passes
     were narrow technical wins, and the substrate-design space needs
     genuinely new ideas.
   - NO → close the bet at the locked-bar WIN. Move to applications
     of the substrate (e.g., audio classification benchmark).

3. **Reframe the wager?**
   - The original wager said "5/5 binary bar". The operator now has
     evidence the bar was too easy. Tightening the bar retroactively
     would violate pre-registration. But declaring the wager-as-written
     a "minimum technical demonstration" rather than a "research-goal
     achievement" is consistent with both contracts and rigor.

4. **What about the 12-month deadline?**
   - The bet has 364 days remaining (deadline 2027-05-22). Continuing
     research within the original window with a harder bar is consistent
     with the original spirit. Stopping research now after a locked-bar
     WIN is consistent with the original contract.

The operator decides. This document is the briefing.

## Specific BET-009 sketch (if approved)

If operator approves T6-T9, BET-009 implementation outline:

  - File: `tests/bet/test_bet_009_harder_bar.py`
  - Subject: beta=0 cog_map AND SOM, both substrates tested under
    the new bar (since both passed the old one — let them compete on
    the new one).
  - Per-substrate, run T0-T5 (locked) + T6-T9 (new). Report all 10.
  - Verdict: substrate "passes" if T0-T9 all pass. (10/10 is the new
    bar.) Either substrate independently can pass; or both pass; or
    neither passes — all three outcomes are findings.
  - Compute budget: T6 + T7 + T8 + T9 each cost roughly the same as
    one BET-002 run. Total ~5× BET-006 cost. Fits in 1h cap.

Implementation NOT done yet. Awaiting operator approval.

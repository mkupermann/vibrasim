# BET-144 — Deep TEMPORAL credit assignment without BPTT: can eligibility (e-prop) learn delayed selective recall a reservoir can't?

Pre-registered: 2026-06-05 (BEFORE the run). The cognition thread's stated open frontier (memory
`cognition-programme-state`; BET-140 capstone) is *deep credit assignment without BPTT* — "the e-prop /
equilibrium-prop frontier." BET-136→140 showed substrate-native recurrent composition trainable by a LOCAL
one-step rule, but only on tasks where the one-step rule is exact (parity step = XOR). Tasks needing **temporal
credit** — where the readout error at time T must be assigned to a STORE decision many steps earlier — are
untested. e-prop (Bellec et al., *Nat Commun* 2020) does exactly this with **eligibility traces**, which are a
core substrate primitive (BTSP). Established method, named as such; the contribution is a substrate-native
demonstration + a clean component map, not new mathematics.

## Task — delayed SELECTIVE recall with distractors (requires temporal credit)
Vocabulary of K=4 symbols. A sequence of length D+2:
- t=0: a **cue** = one-hot symbol with a `cue-bit=1`.
- t=1..D: **distractors** = random one-hot symbols with `cue-bit=0` (must be ignored).
- t=D+1: a `go-bit=1`, zero symbol.
- Target (at the final step only): the class of the t=0 cue.
The net must (a) store the gated cue, (b) ignore D distractors, (c) recall after delay. A readout-only random
reservoir cannot learn to *selectively* store + protect the cue across distractors; learning the recurrent
weights can. Chance = 1/K = 0.25.

## Three arms (leaky-tanh RNN, H=48; online, one sequence at a time)
- **RESERVOIR** (EQMOD-2 baseline): W_in, W_rec fixed random (echo-state, spectral radius ≈0.9, leak α);
  train only the readout (ridge/RLS) on the final state.
- **RTRL** (exact online gradient; Williams & Zipser 1989 — the unimpeachable reference that the task IS
  learnable online without BPTT): train W_rec, W_in, readout via the exact forward-mode gradient.
- **E-PROP** (Bellec 2020; the substrate-native eligibility method): per-synapse eligibility trace + a
  learning signal backprojected from the readout error; trains all weights, local + online, no BPTT.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| BET-144a | Trainers WORK (impl sanity) | RTRL and E-PROP both ≥ 0.90 on the easy case (D=1, no distractors) |
| BET-144b | Task needs temporal credit (baseline fails) | RESERVOIR ≤ 0.45 on the hard case (D=8, distractors) |
| BET-144c | Exact credit solves it | RTRL ≥ 0.80 on the hard case (D=8, distractors) |
| BET-144d | **Eligibility suffices (the frontier claim)** | E-PROP ≥ 0.70 on the hard case AND ≥ RESERVOIR + 0.25 |

## Verdicts (pre-registered, no post-hoc tuning)
- **PASS** (a–d): substrate-native **eligibility traces (e-prop) achieve deep temporal credit assignment** —
  delayed selective recall over distractors — that a readout-only reservoir cannot, validated against exact
  RTRL, with NO BPTT and NO transformer. The stated frontier is reached (with an established method, named).
- **PARTIAL** (a–c hold, **d fails**): exact RTRL solves it but the e-prop eligibility approximation does not
  → honest: the substrate-native local method is insufficient here; the gap between eligibility and exact
  temporal credit is the real boundary.
- **NULL**: if **b fails** (reservoir already solves it → task too easy, no deep credit needed) or **c fails**
  (even exact RTRL can't learn it → task/net mis-specified, not a credit-assignment result). Honest either way.

Negative controls built in: RESERVOIR (no recurrent learning) must FAIL the hard task for the trained result
to mean anything; the D=1 sanity must PASS or a hard-task NULL is just a buggy trainer, not a finding.
No post-hoc threshold tuning; hyperparameters (H, α, lr, spectral radius) fixed before the run.

## RESULT (2026-06-05): NULL — D=8 is within reservoir memory capacity (no deep-credit gap); e-prop is weak

| arm | D=1 sanity | D=8 + distractors |
|-----|-----------|-------------------|
| RESERVOIR (readout-only) | — | **0.815** |
| RTRL (exact online) | 1.000 | 0.995 |
| E-PROP (eligibility) | 1.000 | 0.613 |
| chance | 0.25 | 0.25 |

- **144a ✓** — sanity passes: both trainers hit 1.000 at D=1, so the implementations LEARN (a hard-task NULL
  is not a buggy trainer).
- **144b ✗** — the **reservoir SOLVES D=8 (0.815 ≫ 0.45)**: an H=24 echo-state reservoir holds the gated cue
  across 8 distractor steps. The task is within its memory capacity → no deep-credit gap to demonstrate → NULL.
- **144c ✓** — RTRL nearly perfect (0.995): exact online credit handles it easily (as expected).
- **144d ✗** — e-prop (0.613) is **below the reservoir (0.815)** and far below RTRL (0.995). At these fixed
  hyperparameters, symmetric e-prop is a *weaker* learner than not training the recurrent weights at all here.

**Two honest findings.** (1) The pre-registered D=8 task was mis-calibrated — too easy; a random reservoir's
fading memory already spans 8 distractor steps at H=24, so this cannot test deep credit. (2) The symmetric
e-prop eligibility approximation underperforms both exact RTRL and the readout-only reservoir on this task —
an early sign that simple eligibility may not deliver the temporal-credit advantage the frontier hoped for.

**Chained follow-up (BET-145, pre-registered separately):** sweep the delay `D ∈ {8,16,24,32,48}` to LOCATE
the reservoir's memory horizon (where readout-only breaks toward chance), then test whether RTRL (exact) and
e-prop (eligibility) extend *past* that horizon — the regime where deep temporal credit actually matters. This
is principled (characterizing the capacity boundary), not post-hoc bar-tuning: the verdict logic is unchanged,
only the independent variable (D) is swept to reach the intended hard regime.
</content>

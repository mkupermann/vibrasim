# Marker protocol — addendum for G20–G23 (text chain)

**Pre-registered: 2026-05-11. Frozen.**

This addendum extends `docs/marker_protocol.md` with the pre-registered
thresholds for the English-text amendment chain (G20–G23). Same rule
applies: a threshold edited after a run that "almost passed" is overfitting
evidence, and the verdict of that run is void. New thresholds are added
under new amendment numbers (G21′, G22′, …), never by editing the row
below.

The main marker-protocol document (`docs/marker_protocol.md`) defines the
five-marker conjunction trigger and its negative-control discriminator.
This addendum does not change those five markers. It pre-registers
**amendment-specific acceptance thresholds**, which are a separate concept
from the conjunction-trigger markers.

---

## Gate before G20 can begin

G20 is **blocked indefinitely** until **all three** hold:

| # | Gate condition | Source of truth |
|---|---|---|
| G | `result.json["verdict"] == "PASS"` on a real-corpus G19 run (≥ 24-hour, all four substrates, 2σ bar) | `~/.eqmod/babble/run-*/result.json` |
| G | Five-marker conjunction fires on the trained-engram run, stable for ≥5 consecutive cycles | `agent/run_autonomous.py::check_emergence_markers` |
| G | Matched-config negative control does **not** fire the markers (`max_markers_seen < 5`) | `~/.eqmod/autonomous/NEGATIVE_CONTROL.json` |

Source: `docs/amendments/G20-G23.md` §1.

---

## G20 acceptance — text port primitive

Mechanical I/O only. No learning. See `docs/amendments/G20-G23.md` §3.2.

| # | Check | Pass condition |
|---|---|---|
| G20.1 | Geometric correctness | 27 sub-cubes are disjoint, each 6×6×6, union fits in substrate |
| G20.2 | Write-only smoke | `write_symbol('a')` 30×/sec → vibrations in `a` sub-cube > 0; in `b` sub-cube = 0 |
| G20.3 | Read-only smoke | Forced atom firing in `a` sub-cube → `read_symbol() == 'a'`; same for `b` with stronger firing → `'b'` |
| G20.4 | Round-trip without binding | `write_symbol('a')` for 1 sim-sec then `read_symbol()` ∈ {None, `'a'`} |

All four must hold. G20 has no negative control because it does no learning.

---

## G21 acceptance — single-letter `a` round-trip

See `docs/amendments/G20-G23.md` §4.2.

| # | Metric | Pass | NULL | FAIL |
|---|---|---|---|---|
| G21.1 | Trained round-trip accuracy on `a` (20 trials) | ≥ 16/20 (80%) | 12–15/20 | < 12/20 |
| G21.2 | Negative control accuracy (substrate trained on `b`, tested on `a`, 20 trials) | ≤ 2/20 (≤ 10%) | 3–5/20 | ≥ 6/20 |
| G21.3 | Trained − control margin (percentage points) | ≥ 68 pp | 50–68 pp | < 50 pp |

PASS requires all three rows in the PASS column. Any single row in NULL or
FAIL downgrades the whole verdict to that row's category.

A "round-trip" counts as success only if **both** un-stimulated modalities
produce `a` within the test window.

Wall-clock ceiling: 8 weeks from G21's first commit. At ceiling: FAILED,
post-mortem, retry under G21′ with new pre-registered acceptance.

---

## G22 acceptance — 5-letter set + forgetting

See `docs/amendments/G20-G23.md` §5.2.

Run order: train `a`, `b`, `c`, `d`, `e` sequentially (each 20 sim-min,
G21 protocol). After all five trained, run 20 trials per letter in random
order.

| # | Metric | PASS unqualified | PASS qualified | NULL | FAIL |
|---|---|---|---|---|---|
| G22.1 | Per-letter round-trip accuracy (each of 5 letters) | All ≥ 16/20 via strategy C or D (no `pattern_id` segregation) | All ≥ 16/20 via strategy B (`pattern_id` segregation) | Mixed: 3–4 letters at 16/20 | < 3 letters at 16/20 |
| G22.2 | Forgetting on earliest-trained letter (`a` re-tested after `e` is trained) | ≤ 10% drop relative to G21 baseline | ≤ 10% drop | 10–25% drop | > 25% drop |
| G22.3 | Negative control: substrate trained on `f`–`j`, tested on `a`–`e`, 20 trials each | ≤ chance + 2σ (≤ 12%) on all 5 | ≤ 12% on all 5 | 12–25% on any | > 25% on any |

The qualification (PASS unqualified vs PASS qualified) is permanent and
appears in:

- This addendum row, marked.
- The README status table.
- The post-mortem (if applicable).
- Any external write-up.

Wall-clock ceiling: 24 weeks from G22's first commit.

---

## G23 acceptance — open-loop text babble

See `docs/amendments/G20-G23.md` §6.2. Direct character-trigram analogue
of G19's MFCC-histogram protocol.

| # | Metric | PASS | FAIL | NULL |
|---|---|---|---|---|
| G23.1 | Trained-EN character-trigram-KL vs white-noise | z-score ≥ 2.0, AND `kl_mean[trained] < kl_mean[control]` | z-score ≤ 0 | otherwise |
| G23.2 | Trained-EN vs reversed-EN | z-score ≥ 2.0 | z-score ≤ 0 | otherwise |
| G23.3 | Trained-EN vs French | z-score ≥ 2.0 | z-score ≤ 0 | otherwise |
| G23.4 | Bootstrap count | 100 | < 100 | n/a |

PASS requires G23.1 AND G23.2 AND G23.3 in PASS. FAIL on any of them is
FAIL overall. NULL on any (with no FAIL) is NULL overall, with
`null_against` listing the controls that didn't separate.

Output JSON shape identical to G19's `result.json`, substituting
`character-trigram-KL` for `MFCC-KL`.

Wall-clock ceiling: 32 weeks from G23's first commit. Compute ceiling for
the production run itself: 7 days continuous on the author's Mac.

---

## G24–G26 acceptance — German chain

Acceptance for G24/G25/G26 will be added to this addendum **before**
G24 begins, not now. The shape is pre-committed in
`docs/amendments/G20-G23.md` §7 but the numeric thresholds depend on
empirical findings from G20–G23 and will be pre-registered then.

Pre-committing the *shape*:

| Amendment | Required test |
|---|---|
| G24 (fresh substrate, German only) | G23-shape PASS on German with DE/WN/reversed-DE/French controls |
| G25 (English-fork → German) | G24's PASS bar AND wall-clock to convergence < 0.7 × G24's wall-clock |
| G26 (continual learning, English-PASSed substrate trained on German) | G24's PASS bar AND English round-trip degrades ≤ 10% from pre-German baseline |

G26 is **expected to FAIL on the first attempt**. This expectation is
recorded so that the eventual FAIL is not news and the eventual PASS is
not overclaimed.

---

## Retry rule — frozen

A FAILED amendment's row in this table is **permanent**. The author may
design a new amendment with a new number (e.g. G21 → G21′) with its own
acceptance row added below the original. The original is never edited
except to record the FAILED verdict and a link to the post-mortem.

This is the operationalisation of the discipline that the project's
README §1 commits to: a process for breaking deadlocks cannot rely on
retroactively softening the bar.

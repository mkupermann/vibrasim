# ER-02 — Freeze turnover at consolidation: does a STATIC engram persist quietly without contamination?

## Motivation
ER-01 reframed atom "erosion" as TURNOVER (old atoms dissolve, new form) and showed that freezing
constituent (pair/triad) decay makes the structure perfectly static. The deadlock's two horns are
active→contaminated and quiet→eroded. ER-02 tests the structural fix: form a localized engram, then at
consolidation FREEZE the constituents (stop turnover), and run a QUIET POST. If the engram persists by
ATOM IDENTITY and its bridges hold while the control region stays blank (quiet = no ambient flux to
contaminate), that is selective persistent recall — the deadlock cracked at its turnover root. This is
a genuine structural attempt motivated by chasing the root; the freeze is a config knob, but the
INSIGHT (the block is turnover, stoppable at consolidation) would be a real mechanistic finding.

## Method (`tools/run_er02_static_engram.py`)
Reuse the G94 quiet-substrate protocol (WARMUP cull+blank → STIM writes a localized engram → capture
engram atom IDENTITIES (idx+birth) and strong bridges). At STIM_END, two arms (seeds 42 & 7):
- **default:** normal POST (quiet, cull) — engram turns over (G93).
- **frozen:** set `pair_decay_time = triad_decay_time = 1e9` at STIM_END (stop turnover), then quiet POST.
Readouts over POST: engram atom-IDENTITY persistence (survivors / captured), engram strong-bridge
persistence, control-region strong-bridge count.

## Pre-registered PREDICTION + bars (BEFORE the run)
- **ER02a (frozen preserves atom identity):** frozen engram atom-identity persistence ≥ 0.70, both seeds
  (the specific atoms survive, not just the count).
- **ER02b (SELECTIVE persistent recall):** frozen engram bridge-persist ≥ 0.40 AND frozen control
  strong-bridge count ≤ 2, both seeds.
- **ER02c (frozen beats default):** frozen atom-identity persistence − default ≥ 0.30, both seeds.

PASS = freezing turnover at consolidation yields a persistent, selective engram in a quiet substrate —
the first crack in the memory deadlock, found by attacking its turnover root. NULL if ER02a fails (the
specific atoms erode even frozen — turnover is not the identity-loss mechanism) or ER02b fails (atoms
persist but bridges don't, or control still contaminates). Honest either way. Bars locked; no retuning.
No transformer.

## RESULT (2026-06-05): NULL — turnover-freeze does not save the engram; the deadlock re-confirmed

| seed | DEFAULT atom / bridge / ctrl | FROZEN atom / bridge / ctrl |
|------|------------------------------|------------------------------|
| 42 | 0.22 / 0.00 / 2 | 0.26 / 0.33 / 1 |
| 7  | 0.22 / 0.20 / 17 | 0.30 / 0.20 / 13 |

ER02a ✗ (frozen atom-identity persist 0.26–0.30, not ≥0.70), ER02b ✗ (bridge < 0.40; seed 7 control 13),
ER02c ✗ → **NULL.**

**Honest finding — freezing constituent turnover does NOT preserve the engram's atom IDENTITY** (0.26,
exactly G93's eroded value). The identity loss is therefore NOT driven by pair/triad decay. The
discrepancy with ER-01 is the key insight: a membrane (G43, no aggressive culling) froze to a constant
COUNT, but a quiet-CULLED stim engram still loses its SPECIFIC atoms even with decay frozen — because
the **culling itself** (removing free vibrations every tick, which is required to keep control blank)
removes the substrate the engram atoms depend on, and/or the atoms get recycled. So "quiet → eroded"
holds at the atom-identity level and is robust to the turnover-freeze fix.

**Net (PR-01 + ER-01 + ER-02, three fresh attacks this round, all NULL).** The memory deadlock is
re-confirmed robust under genuinely new structural attacks: paced reactivation (Neuron 2026) doesn't
separate write from leak (PR-01); the engram is dynamic turnover not net loss (ER-01); and freezing
turnover doesn't preserve engram identity because the quiet/cull condition itself erodes it (ER-02).
The deadlock's root — the SAME condition that keeps control blank (quiet/cull) is the one that erodes
the engram — is now characterized one level deeper, not broken. Honest; bars held; no retuning.

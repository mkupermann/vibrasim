# ER-01 — Atom erosion: isolate the mechanism (the structural root of the memory deadlock)

## Motivation
Every memory attempt (incl. PR-01's paced reactivation) failed on the same structural root: engram
level≥4 atoms ERODE in the quiet substrate (G93: ~74% lost), so the engram dissolves; and the only
thing that keeps atoms alive — ambient flux — is the same flux that contaminates control. PR-01 showed
re-FIRING the atoms does not stop erosion. So the new-science question is: WHAT erodes the atoms, and
can they be made permanent in a QUIET substrate (which would give a persistent engram with NO
contamination — the deadlock cracked at its source)?

Hypothesis (from the physics): with `lambda_dec_mol=0` (default) the level-4 decay path is off, so
atoms are not killed directly — they erode because their CONSTITUENTS (level-2 pairs / level-3 triads)
decay via `pair_decay_time`/`triad_decay_time`, breaking atoms apart faster than they reform when no
ambient flux supplies replacements. If so, disabling constituent decay should make atoms persist
quietly.

## Method (`tools/run_er01_atom_erosion.py`)
Form a structure with the G43 proto-cell cfg (active settle), then go QUIET (cull free vibrations,
lambda_gen=0) and run a long POST, recording the level≥4 atom count over time. Two arms, seeds 42 & 7:
- **default:** g43 cfg (pair_decay_time=12, triad_decay_time=80).
- **no-constituent-decay:** same but `pair_decay_time = triad_decay_time = 1e9` (constituents frozen).

## Pre-registered PREDICTION + bars (BEFORE the run)
- **ER01a (erosion is real in default quiet):** default level-4 count drops to ≤ 0.5 × its post-settle
  value by the POST horizon, both seeds (reproduces G93).
- **ER01b (constituent decay is the mechanism):** no-constituent-decay retains ≥ 0.85 × its post-settle
  level-4 count at the horizon, both seeds — atoms persist quietly when constituents don't decay.
- **ER01c (it is attributable):** no-constituent-decay retention − default retention ≥ 0.35, both seeds.

PASS = constituent decay is the erosion mechanism AND disabling it makes atoms persist in a quiet
substrate — the structural root identified and a candidate fix found (next: test if this gives
persistent selective recall with no contamination). NULL if ER01b fails (atoms erode even with
constituents frozen — the mechanism is elsewhere, e.g. direct unbinding or displacement). Honest
either way. Bars locked; no retuning. No transformer.

## RESULT (2026-06-05): NULL (metric flaw) — but reveals TURNOVER vs STATIC, and a promising fix

| seed | DEFAULT n0→final (ret) | FROZEN n0→final (ret) |
|------|------------------------|-----------------------|
| 42 | 142 → 286 (2.02) | 145 → 145 (1.00) |
| 7  | 144 → 303 (2.10) | 144 → 144 (1.00) |

ER01a ✗ (default count did NOT drop — it DOUBLED), ER01b ✓ (frozen ret 1.00), ER01c ✗ → **NULL.**

**The metric was wrong (honest).** I measured TOTAL level-4 count, which in the default quiet substrate
GROWS (142→286) because new atoms keep forming — masking G93's finding, which is about the SPECIFIC
engram atoms losing IDENTITY. So total-count is the wrong observable. But the run is informative:
- **Default = dynamic TURNOVER:** the structure is not static — old atoms dissolve while new ones form,
  net count rising. The engram (specific atoms) can erode by identity even as the count grows. This
  reframes "erosion": it is atom TURNOVER, not net loss.
- **Frozen constituents = perfectly STATIC:** count held exactly constant (145→145, 144→144). Freezing
  pair/triad decay stops the turnover entirely — strongly suggesting the original atoms persist by
  IDENTITY (no dissolution, no new formation).

**This points at the structural fix.** If freezing constituents preserves engram-atom IDENTITY in a
QUIET substrate, then the engram persists with NO ambient flux → NO contamination — the deadlock's two
horns (active→contaminated, quiet→eroded) could BOTH be escaped. Re-run with proper IDENTITY tracking
(G93's measure: tag the atoms at t0, count survivors) AND a control-region readout, as ER-02. Recorded
NULL against the locked bars; no retuning — the next experiment fixes the metric and tests the fix.

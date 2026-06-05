# JEP-374 — Stronger dimension factor (load ≤ D/8) to fully recover negative probes

## Motivation
JEP-373 showed dimension-scaled consolidation is the right lever but `load ≤ D/4` (→D=8192) left seed-0 negative is-a
probes at 0.867 (< 0.95). The random cleanup floor scales ~√(load/D); halving load/D (→ `load ≤ D/8`, D=16384) should
push the floor well below the decision gate and recover negatives on both seeds. This changes only the auto_scale
DIMENSION POLICY (a design parameter), not the acceptance bar. No transformer.

## Method
Same end-to-end harness as JEP-372/373 (read a ~300-node taxonomy via `read_text`, ask deep + negative is-a via
`Conversation.say()`), now with `consolidate_closure(auto_scale=True)` using the `load ≤ D/8` factor.

## Pre-registered PREDICTION + bars (BEFORE the run)
Prediction: at the stronger factor (D→16384 for ~1900 facts), negative-probe accuracy recovers to ≥0.95 on BOTH seeds
while deep stays ≥0.95, exceptions hold, persistence holds, suite green.

- **J374a (negatives recovered):** negative is-a via `say()` ≥0.95, BOTH seeds (0, 7).
- **J374b (deep still reliable):** deep is-a via `say()` ≥0.95, both seeds.
- **J374c (exceptions + persistence + no regression):** `not`-is-a respected; save→load keeps deep ≥0.95;
  `pytest -m "not slow" tests/test_conversation.py tests/test_substrate_memory.py` passes.

If negatives STILL miss at D=16384, the residual is not pure cleanup noise and brute-force D is the wrong fix — then a
calibrated-gate / structural approach is needed (would be the next finding). Predicted: D/8 fixes it. Bars fixed. No
transformer.

## Result (seeds 0, 7): **NULL — falsifies the brute-force-D hypothesis; redirects to the gate**
- **J374a (negatives recovered): NOT met, and NON-MONOTONIC** — at D=16384: seed 0 = **0.933** (up from 0.867 at
  8192), but seed 7 = **0.9** (DOWN from 0.967 at 8192). Raising D did not monotonically help; negative-probe accuracy
  floors around ~0.9–0.93 regardless of D.
- **J374b (deep still reliable): PASS** — deep is-a via `say()` = 1.0 / 1.0.
- **J374c (exceptions + persistence + no regression): PASS** — exceptions respected, reload deep = 1.0, 23 tests pass.

### What this tells us (the real finding)
If the negative false-positives were pure cleanup noise, accuracy would rise monotonically toward 1.0 as D grows
(floor ~√(load/D) → 0). Instead it is **non-monotonic and floored ~0.9** — so the residual is **structural, not
noise**. The most likely cause is **decision-gate placement**: after consolidation a node carries ~depth× is-a edges,
which shifts the edge-similarity distribution, and the globally auto-calibrated gate mis-separates a minority of
non-ancestor probes. Brute-force dimension is therefore the WRONG fix (it also doubled storage for no net gain).

## Verdict: **NULL — D is not the lever for negatives; the fix is gate calibration (JEP-375)**
Honest negative result: dimension scaling fixed the DEEP-reasoning compounding (JEP-370/371/372) but does NOT reliably
fix NEGATIVE is-a probes after consolidation — those float ~0.9 and even regress with more D on one seed. The cause is
structural (gate placement under the post-consolidation similarity distribution), so the next experiment recalibrates
the is-a decision gate on the consolidated store rather than enlarging D. The auto_scale factor is reverted to the
cheaper `load ≤ D/4` (D=8192) point, since D/8 (16384) bought nothing. Bars not moved. No transformer.

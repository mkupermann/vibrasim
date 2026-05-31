# BET-112 — Noise Robustness (Error-Correcting Recall)

Pre-registered: 2026-05-31 (BEFORE the run). Follows BET-110/111. Question: how
much input corruption can the energy memory correct? A stored pattern is flipped
in a fraction f of its bits and the FULL noisy state is relaxed freely (no clamp);
the attractor should pull it back to the clean pattern up to some noise radius.

## Method

Train the BET-110 net (N=80, 6 patterns) self-supervised. For corruption levels
f ∈ {0.05 … 0.5}, flip f·N random bits of a stored pattern, relax freely, measure
recovered overlap with the true pattern (averaged over trials/patterns). Compare
to an untrained (shuffled-weight) control.

## Acceptance bars (locked pre-run)

| ID | Criterion | Bar |
|----|-----------|-----|
| T112a | Corrects light noise | at f=0.10, recovered overlap ≥ 0.95 |
| T112b | Basin radius | recovered overlap ≥ 0.90 for all f ≤ 0.20 (corrects up to ~20% flipped bits) |
| T112c | Control fails | the shuffled-weight control's recovery at f=0.10 is far worse (< 0.75) — the correction is learned structure, not trivial |
| T112d | Graceful | recovery is monotone non-increasing in f (no pathological behaviour) |

PASS = T112a–d. PASS = the memory is a genuine error-correcting attractor (a basin
of attraction), not just exact lookup. Plot: recovered overlap vs noise level.

## RESULT (2026-05-31): PASS — genuine error-correcting attractor

Recovered overlap vs corruption f: 0.05→1.00, 0.10→1.00, 0.15→1.00, 0.20→0.996,
0.25→0.952, 0.30→0.862, 0.40→0.762, 0.50→0.445. Shuffled-weight control at
f=0.10 = 0.552.

| Bar | Outcome |
|-----|---------|
| T112a corrects light noise (@0.10 ≥ 0.95) | ✓ 1.00 |
| T112b basin (f ≤ 0.20 → ≥ 0.90) | ✓ |
| T112c control fails (@0.10 < 0.75) | ✓ 0.55 |
| T112d graceful (monotone) | ✓ |

**BET-112: PASS.** The memory is a real error-correcting attractor with a basin
radius of ~25 % flipped bits: it pulls a heavily corrupted input back to the clean
stored pattern. This is content-addressable, robust associative recall — exactly
the capability the spontaneous substrate could never hold. Plot: `bet112_noise.png`.

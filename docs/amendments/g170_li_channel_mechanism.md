# G170 — the LI channel: which mechanism owns the R2-exclusive losses?

**Status: SIGNED OFF 2026-08-13 (round 10: xiii carried by A, D, F with A's
multi-arm condition — ARM-SIM absorbs E's xiv in substance; B2 abstention
after two pings; C's (iv) association conditions are on file for the next
round; D explicit bars-JA) — committed before any data (D2). Bars final
per D3.**
**Verdict 2026-08-13: H-INDEX CONFIRMED** — SWAP migrates losses 100% to R1,
SIM (H-TIME's ~zero-loss prediction) shows 37 loss runs incl. 111
interior-interior cross-bonds destroying both registers (mean 0.785). The
R2-exclusivity is an allocation-index artifact of form_bridges' fixed
pair-scan — a substrate trap, documented in the pattern doc. LOGBOOK
2026-08-13.

## 1. The one question (D1)

> G169 certified COUPLED-BUT-SEPARABLE but falsified the loss model
> (hit rate 0.375) and left two facts unexplained: LI bonds (chain-end →
> interior) exist, and ALL decode losses sit on R2 (9/9 runs). Two candidate
> mechanisms make DIFFERENT pre-registered predictions — which one owns the
> phenomenon?

**H-TIME (researcher A):** R1 is already consolidated and valence-saturated
when cross-bonding happens; R2's interiors are still open — theft runs one
way in time.
**H-INDEX (chair, from harness review):** consolidation was de facto
simultaneous (both chains pinned from tick 1); the asymmetry lives in
form_bridges' FIXED pair-scan order (triu over slot indices): R1 is
allocated first (low indices), so the scan settles R1-internal and cross
pairs before R2-internal pairs — cross bonds win the valence race against
R2's own bonds deterministically.

## 2. Protocol — three arms, NEAR geometry (Δy = 10), all else = G169

8 pattern-pairs × seeds {42, 7, 13} per arm; all G169 metrics (per-register
per-seed accuracy PERSISTED this time, cross-bond location classes, margins,
censuses, boundary gate, order-effect metric).

- **ARM-BASE:** allocation order R1 then R2 (G169 replication).
- **ARM-SWAP:** allocation order R2 then R1 (chain 2 gets the LOW indices).
- **ARM-SIM:** interleaved allocation (R1[0], R2[0], R1[1], R2[1], …) —
  neither chain owns the low-index block.

## 3. Pre-registered point predictions (the verdict axis; D3)

Loss-register distribution per arm (a "loss run" = any run with ≥ 1 bit
error; register attribution recorded per run):

| Arm | H-TIME predicts | H-INDEX predicts |
|-----|-----------------|------------------|
| BASE | losses on R2 only | losses on R2 only |
| SWAP | losses on R1 only (the later-consolidated) | losses on **R1** only (now high-index) |
| SIM | ~zero losses (no open-interior window) | losses persist, SPLIT between registers |

(SWAP does not discriminate — both predict migration; **SIM is the
discriminator.** H-TIME: interleaved allocation still consolidates both
chains in the same pinned phase, so no window → ~0 losses. H-INDEX: the
scan-order race persists under any allocation, only its victims mix.)

**Verdict:**
- **H-INDEX CONFIRMED:** SWAP losses ≥ 80% on R1 AND SIM shows ≥ 3 loss
  runs with BOTH registers represented.
- **H-TIME CONFIRMED:** SWAP losses ≥ 80% on R1 AND SIM shows ≤ 1 loss run.
- **BOTH FALSIFIED:** SWAP losses do NOT migrate (≥ 1 loss run on R2 with
  clean R1 majority broken) — a third mechanism; record and stop.
- **MIXED/NULL:** anything else (patterns too weak to attribute; the loss
  base rate may simply be too low at 24 runs/arm — recorded as NULL with
  the observed distribution).
- Gates: G169 controls carried (boundary ≤ 10%, censuses logged; no
  OLDREST/NEG arms needed — this is a mechanism attribution among
  treatment variants, no capability claim is made).

## 4. Predictions (calibration, before data)

- Chair: H-INDEX 60%, H-TIME 25%, BOTH-FALSIFIED 5%, MIXED/NULL 10%.
- Loss base rate ≈ G169's (9/24 NEAR runs): 70%.

## 5. Budget

Harness: allocation-order parameter + per-register persistence: 25 min.
Compute: 3 arms × 24 runs × ~11k ticks ≈ 30 min. Verdict + LOGBOOK +
FRONTIER: 30 min. **Realistic 1.5 h → hard cap 3 h.**

## 6. Out of scope

Association (C's conditions for it are on file for the next round),
mitigation engineering, kinematics dossier, capability claims of any kind.

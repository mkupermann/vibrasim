# G132 — Can substrate PRIMITIVES learn A->B? (charter-faithful, proper readout)

## Pre-registration (locked BEFORE run)
Re-run the R2 learnability rung correctly: enable the substrate's OWN learning machinery (STDP, BTSP,
correlation plasticity, bistable wells, charge/atom propagation — no bolted-on ML), train A->B pairing
N=80 times, then probe A alone and read the B-region BTSP ELIGIBILITY (k_eligibility, which accumulates
from firing — a real activity readout, fixing G131's dead probe). Compare to untrained and to a control
region C. Both seeds.

**Bars (locked):**
- G132 PASS (learned): trained A->B eligibility > 1.5x untrained AND > 1.5x control-region C, both seeds.
NULL otherwise → substrate primitives cannot form the association (charter-faithful evidence).

## Result
| seed | trained A→B elig | control-region C | untrained A→B |
|------|------------------|------------------|----------------|
| 42   | 17.84            | 17.82            | 15.96          |
| 7    | 7.31             | 6.52             | 7.10           |

G132: **NULL** — trained ≈ untrained (1.1×, below 1.5× bar) AND trained-B ≈ trained-C (no A→B specificity).

## Finding — substrate primitives do NOT learn (clean, charter-faithful evidence)
With the full learning machinery active and a real activity readout (BTSP eligibility, non-zero), training
A→B for 80 pairings produced NO selective association: A's probe raises activity at B no more than at an
unrelated control region C, and no more than in the untrained substrate. The substrate does not wire A→B.

This is the clean version of the G131 test (dead probe) and the decisive evidence for the campaign's R2
rung: **the substrate's own primitives cannot form a learned association.** Combined with the charter rule
forbidding bolted-on neural-net layers and the prior NULLs (substrate-as-reservoir G78–G80), every route
to a learning/cognitive layer on this substrate is either forbidden or empirically empty. Honest campaign
conclusion: a cognitive/learning layer cannot be built on this substrate within the charter; the
substrate's role is memory + I/O only. See HUMAN_AI_CAMPAIGN.md (R2 = NULL).

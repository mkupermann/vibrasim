# G165 — register capacity: where does the rest-length code break?

**Status: SIGNED OFF 2026-08-12 by round-table majority (A, C, D of cast votes;
B unresponsive→abstention per protocol; D/E's boundary-confounder objection was
resolved by HARDENING into the anti-bias INCONCLUSIVE@K gate, C's no-early-stop
and anchor-FAIL conditions incorporated) — committed before any data (D2).
Bars final per D3.**
**Verdict 2026-08-12: PASS** — P ≥ 0.90 at all K on 3/3 seeds (K6 1.000, K12
0.986, K24 1.000), controls ≤ 0.6, censuses valid, boundary rate 0.0, and real
strain at K=24 (min non-neighbour distance 11.68 < formation window). LOGBOOK
2026-08-12.

## 1. The one question (D1)

> Does the G163 write→scramble→retrieve protocol still decode at ≥ 0.90 when
> the register scales from 6 to 12 and 24 bits — and if it breaks, does the
> pre-registered diagnostic identify WHERE (bonds never formed / bonds formed
> but decode wrong / cross-bond frustration)?

Physics framing (researcher A): a short chain is a path graph — unfrustrated,
every rest length independently satisfiable; G163/G164 therefore tested
relaxation into a trivial minimum. Longer chains are the cheapest way to
GENERATE frustration: a 12/24-bit chain can fold in 3D until non-neighbour
carriers cross the formation cutoff 12, cross-bonds freeze their own geometry,
and the code acquires real constraint conflict. The break point is a physical
observable, not a numerology.

## 2. Protocol

G163 protocol unchanged (write 8 ticks → scramble to uniform 8.5 → retrieve
800 ticks, carrier-0 pin, formation freeze + census, encoding 6.5/10.5,
decode > 8.5, thermal 0 throughout) at **K ∈ {6 (anchor), 12, 24} bits**
(7/13/25 carriers). 8 random patterns (≥1 one, ≥1 zero) × seeds {42, 7, 13}
per K. **Box scales linearly with K (researcher A's condition):**
box_x = X0 + K·10.5 + 30 margin, rounded up to tens (K=6 → 120, K=12 → 180,
K=24 → 300); repulsion_cell_size = box_x. A worst-case all-long chain fits
stretched with margin — a fixed 240-box would NOT fit K=24 (up to 263 units)
and wrap/folding would be mislabelled by the classifier.
**Boundary-contact gate (mandatory; hardened after D/E objection):** any
carrier within 5 units of any box face at any sampled tick flags the run
BOUNDARY-CONFOUND. Such runs count NEITHER as pass NOR as break (excluded
from the accuracy denominator), their count is ALWAYS reported, and —
the anti-bias gate — if more than 10% of a P-arm's runs at any K are
boundary-confounded, that K is **INCONCLUSIVE@K** (capacity unanswerable at
this box; follow-up needs a larger box under a new ID). Selective exclusion
can therefore never silently mask the capacity limit: it converts into an
explicit INCONCLUSIVE verdict instead.
Arms per K: **P** and **OLDREST** (attribution); NEG only at K=24.

**Mandatory strain metrics (researcher A, fixed now):** per run, over the
retrieve phase: minimum non-neighbour carrier distance (min over time and
pairs |i−j| ≥ 2) and the chain's gyration radius at decode time. Reported per
K — a smooth PASS with min distance ≫ 12 means NOTHING was strained and the
verdict text must say so.

**Break-point diagnostic (researcher B, fixed now):** every sub-0.90 run is
classified by census before any interpretation:
- **W-FAIL:** write census invalid (bonds never formed / wrong graph /
  allocation ceiling hit — reported with node/bond counts) — an ENGINEERING
  bound, not a code capacity result;
- **X-BOND:** write census valid but new cross-bonds appeared during retrieve
  freeze-kills or scramble state (frustration written in);
- **D-FAIL:** censuses clean, decode simply wrong (dynamics/topology limit —
  the actual capacity boundary).

## 3. Pre-registered bars (fixed before any data; D3)

Accuracy on total bits per arm/seed/K (8 × K bits). **All three K are run to
completion before ANY verdict is read (researcher C's condition) — no early
stop after a clean K=12.** The K=6 < 0.90 case is NOT a capacity verdict but
FAIL (anchor regression against the standing G163 PASS — see FAIL clause).

- **PASS:** P ≥ 0.90 at ALL of K=6,12,24 on ≥ 2/3 seeds, OLDREST ≤ 0.6
  everywhere, NEG@24 ≤ 0.6, write censuses valid at all K.
- **PARTIAL:** P ≥ 0.90 at K=6 and 12 but < 0.90 at 24 with the break
  classified (X-BOND or D-FAIL) — the capacity curve + mechanism is the
  finding.
- **NULL:** P < 0.90 already at K=12 (no scaling beyond the anchor), controls
  clean.
- **INCONCLUSIVE@K:** > 10% boundary-confounded runs in the P-arm at that K
  (reported per K; a fully clean verdict requires all three K below the 10%
  gate).
- **FAIL:** anchor K=6 < 0.90 (G163 fails to reproduce — engineering stop),
  or OLDREST ≥ 0.75 anywhere, or NEG@24 > 0.6, or sub-0.90 runs dominated by
  W-FAIL (allocation ceiling — engineering bound, fix and new ID, no capacity
  claim either way).

## 4. Predictions (calibration, before data)

- K=6 anchor reproduces: 95%.
- K=12 ≥ 0.90: 70%. K=24 ≥ 0.90: 45% — the 24-bit chain (~200 units long,
  free ends during retrieve from a straight scramble state) plausibly stays
  extended at thermal 0 (no folding driver), which would give a smooth PASS
  with min-distance ≫ 12 and an honest "nothing was strained" note.
- Verdict: PASS 45%, PARTIAL 25%, NULL 10%, FAIL 20% (W-FAIL/allocation risks
  at 25 carriers + 24 bonds).
- Most-likely failure mode: W-FAIL at K=24 (write-phase skip bonds between
  far carriers during the straight consolidation are impossible — distances
  grow monotonically — but allocation/valence bookkeeping at 25 nodes is
  untested; if it breaks, that is the engineering bound, not capacity).

## 5. Budget (hybrid, §5)

Harness generalization (K parameter + strain metrics + break classifier):
30 min. Compute: ~150 runs × ≤1k ticks ≈ 15 min. Verdict + LOGBOOK + FRONTIER
(D10): 30 min. **Realistic 1.5 h → hard cap 3 h.**

## 6. Out of scope

Retention at scale, interference, association, kick agitation, adaptive
rests, efficiency, flux port.

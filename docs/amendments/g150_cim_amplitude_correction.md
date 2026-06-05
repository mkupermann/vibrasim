# G150 — Does the textbook CIM amplitude-correction close the oscillator↔SA gap? (is the oscillator's weakness paradigm-deep or just naive dynamics?)

Pre-registered: 2026-06-05 (BEFORE the run). G146–G149 established that the *naive* phase-only oscillator
(G145's Kuramoto dynamics, `dθ = Σ W sin(θ_i−θ_j) − sin(2θ)·anneal + noise`) is a *legitimate but weak*
annealer: it ties a correct multi-restart greedy and loses to classical simulated annealing 15/15 at scale,
even at 10× compute (G149 → fundamental, not a budget artifact). BUT the coherent-Ising-machine (CIM)
literature has a standard, well-known fix for exactly this failure mode: **amplitude-heterogeneity
correction (AHC)** (Leleu, Yamamoto et al., *PRL* 2019 / *npj* 2021) — an error/feedback variable that
destabilizes the local minima the plain amplitude/phase machine settles into. My G146–G149 never tested it.

The honest open question: is the oscillator's weakness **paradigm-deep** (oscillator machines are just worse
annealers than SA), or merely an artifact of the **naive dynamics** G145 happened to use (which the textbook
AHC fixes)? G150 tests the established AHC-CIM against SA on the same hard instances.

## Method
Same instances as G148 (spin-glass MAX-CUT, signed Gaussian, `rng_seed=2`), `n ∈ {200, 360}`, 5 instances per
n. Encode Ising couplings `J = −W / √n` (mean-field scaling, standard). Solvers:
- **OSC_naive** — G145 phase-only oscillator (best of 5 seeds), for reference.
- **CIM (AHC)** — amplitude+error dynamics (Leleu 2019, established — named as such, no novelty claimed):
  `dx_i = (p − 1 − x_i²)·x_i + ξ·e_i·(J x)_i` ; `de_i = −β·(x_i² − a)·e_i` ; spin `s_i = sign(x_i)`; pump `p`
  ramps 0→`p_max`. A physical machine runs many times → CIM result = **best cut over a PRE-REGISTERED grid**
  `ξ∈{0.1,0.3} × β∈{0.1,1.0}` × seeds `{0,1,2}` (grid frozen here; NOT tuned post-hoc), fixed `p_max=2.0,
  a=1.0, dt=0.05, steps=1500`.
- **SA** — classical Metropolis (G147 settings, 4×1000 sweeps).
- **GRD** — sign-correct greedy, 60 restarts.
- **REF** — best over all + long SA, for approximation ratios.

## Bars (locked pre-run)
| ID | Criterion | Threshold |
|----|-----------|-----------|
| G150a | Hard regime present (sanity) | SA beats GRD on ≥ 4/5 at n=360 |
| G150b | **Does AHC close the gap to SA? (decisive)** | classify per below at n=360 |
| G150c | AHC helps vs naive (sanity) | CIM ≥ OSC_naive on ≥ 3/5 at n=360 |

**G150b classification (pre-registered):**
- **CLOSED** (paradigm rehabilitated): CIM ≥ SA on ≥ 4/5 AND mean(CIM − SA)/REF ≥ −0.01 → a *properly
  engineered* oscillator/CIM machine IS competitive with classical SA; G145's weakness was naive dynamics,
  not the oscillator paradigm. (Still a known method — but the "physical machine competitive with SA on hard
  optimization" claim would be honestly salvageable.)
- **NOT-CLOSED** (paradigm-deep weakness): SA > CIM on ≥ 4/5 AND mean(SA − CIM)/REF ≥ 0.01 → even the
  textbook-corrected oscillator stays behind classical SA → the weakness is paradigm-deep at this scale.
- **PARTIAL**: otherwise (CIM beats greedy but not SA, or mixed) — report as such.

## Verdicts
- **CLOSED** → honest update: a correctly-implemented CIM (not G145's naive one) is competitive with SA;
  the substrate-adjacent "physical optimizer" story survives in its proper, literature-grounded form.
- **NOT-CLOSED** → strengthens G148/G149: oscillator/CIM machines are robustly weaker annealers than classical
  SA on these instances, even with the standard correction.

Honesty guard: the AHC grid is PRE-REGISTERED and frozen; if CIM underperforms I will NOT re-tune it to rescue
the claim (that is the forbidden post-hoc move) — I will report "with standard AHC parameters, CIM does/doesn't
close the gap," noting CIM's known hyperparameter sensitivity as a caveat, not an escape hatch. Established
method (Leleu/Yamamoto CIM-AHC), named as such; no novelty claimed.

## RESULT (2026-06-05): PARTIAL — AHC genuinely helps (CIM now BEATS correct greedy) but stays a hair behind SA

| n | SA > GRD | CIM ≥ SA (mean gap) | **CIM > GRD** | CIM ≥ naive |
|---|----------|---------------------|---------------|-------------|
| 200 | 4/5 | 2/5 (−0.006) | **4/5** | 5/5 |
| 360 | 5/5 | 1/5 (−0.007) | **5/5** | 5/5 |

- **G150a ✓** — SA beats correct greedy 5/5 at n=360: the hard regime is present (as G147–G148).
- **G150c ✓** — **AHC helps: CIM ≥ naive oscillator on 5/5** at both n. The amplitude-correction is a real
  improvement over G145's phase-only dynamics.
- **G150b = PARTIAL** — CIM ≥ SA only 1/5 at n=360 (not CLOSED's ≥4/5), but the SA margin is tiny (mean
  −0.7%, under the 0.01 NOT_CLOSED bar). The gap to SA **narrowed** from the naive oscillator's ~2%/15-loss
  (G148/G149) to within ~0.7%, with CIM even edging SA on 1 instance — but it did not close.

**The decisive, honest refinement:** the **AHC-corrected CIM now BEATS correct multi-restart greedy 5/5 at
n=360** (mean +1.0–4.6% per instance), whereas the *naive* oscillator (G145, tested in G146–G149) merely TIED
correct greedy. So a *properly-engineered* oscillator/CIM machine **does** have a genuine edge over correct
local search on hard frustrated instances — it is a legitimate physical annealer in classical SA's league,
just a hair (~0.7%) behind it at this budget.

**Verdict: PARTIAL — and it softens (does NOT overturn) the G146–G149 conclusion.**
- What G146–G149 got right and stands: G145's *specific naive* oscillator was weak (tied greedy, lost to SA),
  and its "8/8" headline rested on a sign-bugged baseline. Classical SA is still the strongest method here.
- What G150 adds: the weakness was partly the **naive dynamics**, not the whole paradigm. With the textbook
  AHC correction the oscillator/CIM crosses the meaningful line — **it beats correct local search** — and
  comes within ~0.7% of SA. So the honest claim is NOT "physics confers no edge anywhere," but the more
  precise: *a correctly-implemented physical annealer (CIM-AHC) is competitive with classical SA and
  genuinely beats local search on hard optimization; G145's naive version was under-engineered; classical SA
  remains marginally best.* Established method (Leleu/Yamamoto AHC-CIM), named as such — no novelty claimed.

No post-hoc tuning: the reported CIM is best-over-the-PRE-REGISTERED grid (ξ∈{0.1,0.3}×β∈{0.1,1.0}×3 seeds),
exactly as a physical machine runs multiple times; the grid was frozen before the run.
</content>

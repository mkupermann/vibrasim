# V2-P0 — reciprocal field–matter channel

**Status:** FROZEN ON COMMIT, before implementation or experimental data.

## 1. Question and scope

Can one explicit Hamiltonian couple a spatial field and structured matter
bidirectionally, conserve energy numerically, and make field→matter transfer
depend on material topology when coordinates, particle count and bond count
are held fixed?

P0 is an engineering and causal-validity gate. It claims no individuation,
memory, talent, life or cognition.

## 2. Frozen model

All arrays are IEEE-754 float64. The world is a periodic `32 × 32` square
lattice. Each field site `x` has displacement `u_x` and momentum `p_x`. Six
material oscillators have displacement `q_i` and momentum `r_i`; their fixed
2D coordinates only select the six field sites to which they couple.

The Hamiltonian is

```
H = H_f + H_m + H_c
H_f = 1/2 Σ_x p_x² + c²/2 Σ_<x,y> (u_x-u_y)²
H_m = 1/2 Σ_i r_i² + k_b/2 Σ_(i,j)∈B (q_i-q_j)²
H_c = g/2 Σ_i (u_{s_i}-q_i)²
```

`<x,y>` contains each horizontal and vertical periodic lattice edge exactly
once. Constants: `c=1.0`, `k_b=0.5`, `g=1.0`, `dt=0.05`. There is no damping,
drive, stochastic term or external work in P0.

Hamilton's equations are implemented from the gradient of these exact three
terms:

```
u_dot = p
p_dot = c² Δ_periodic u - scatter_i[g(u_si-q_i)]
q_dot = r
r_dot = -k_b L_B q + g(u_s-q)
```

When several particles share a site, `scatter` adds their forces. P0 uses
distinct sites. Integration is velocity Verlet: half momentum, full position,
recomputed force, half momentum. Energy is evaluated after each full step.

The coupling power terms, evaluated with trapezoidal endpoint averaging, are

```
P_f←c = Σ_i p_si · [-g(u_si-q_i)]
P_m←c = Σ_i r_i  · [+g(u_si-q_i)]
```

and `dH_c/dt = -(P_f←c + P_m←c)`. The run persists `H_f`, `H_m`, `H_c`,
`H_total`, both powers and their cumulative trapezoidal integrals.

## 3. Fixtures and initial conditions

Material coupling sites, in particle-index order:

```
s = [(13,16), (14,13), (18,13), (19,16), (18,19), (14,19)]
```

Both fixtures use these same sites and six bonds.

```
CYCLE  = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,0)]
BRANCH = [(0,1),(1,2),(2,0),(2,3),(3,4),(4,5)]
```

BRANCH is a connected branched-unicyclic graph, not an open chain. Particle
count, bond count, coupling sites and all constants are identical. Only the
edge list differs.

Each run starts with `p=q=r=0`. The field displacement is
`u(x)=a·[exp(-d_periodic(x,x0)²/(2σ²)) - spatial_mean]`, with `σ=2.0`.
For each source centre, amplitude `a` is chosen by direct scaling so CYCLE's
evaluated `H_total(t=0)` equals `1.0` within `1e-12`. That exact `u` array is
then reused without rescaling in every arm. CYCLE and BRANCH must therefore
have equal initial energy within `1e-12`; other arms record and use their own
initial energy as denominator. Three source centres are fixed: `(4,16)`,
`(16,4)`, `(4,4)`. These are the three replicates; no RNG is used.

## 4. Arms

- **CYCLE:** full Hamiltonian with `B=CYCLE`.
- **BRANCH:** full Hamiltonian with `B=BRANCH`.
- **NO_BONDS:** same six material oscillators and coupling, with `k_b=0`.
- **DECOUPLED:** the exact same `u` array, with `g=0`; material remains
  present but cannot exchange energy.
- **BROKEN_PAIR:** negative control for the verifier only. The material
  receives `+g(u_s-q)` but the equal field force is omitted. It is deliberately
  non-Hamiltonian and must fail the energy gate.

No mask moves during a run. No arm is described as equal injected work because
there is no drive after initialisation. CYCLE and BRANCH start at energy `1.0`;
all observables use the recorded per-arm initial energy.

## 5. Stage A — numerical and verifier validity

Run CYCLE, BRANCH, NO_BONDS and DECOUPLED for 2,000 steps at all three source
centres. Run BROKEN_PAIR for the same cells solely as the negative control.

For every valid arm:

- all stored values finite;
- global relative energy drift
  `max_t |H_total(t)-H_total(0)| / H_total(0) < 0.005`;
- coupling identity residual
  `|ΔH_c + ∫(P_f←c+P_m←c)dt| / H_total(0) < 0.005`;
- exercised-channel gate for CYCLE and BRANCH:
  `max_t H_m(t) / H_total(0) > 0.01`.

Trajectory-accuracy gate: repeat CYCLE and BRANCH at `dt=0.025` for the same
physical duration (4,000 steps). For every source centre, each fixture's
`A_B` and the signed contrast `A_CYCLE-A_BRANCH` must differ from the registered
`dt=0.05` result by `<0.002`. All comparisons use unrounded float64 values.

Sensitivity gate: BROKEN_PAIR must exceed `0.05` global relative energy drift
for at least one source centre for each fixture. If it does not, the verifier
has not demonstrated sensitivity and P0 is INCONCLUSIVE.

The timestep satisfies `dt·ω_upper < 0.25`, where the implementation computes
`ω_upper² = 8c² + 2g + 2k_b·d_max` from the registered constants and fixture
maximum degree. This is a conservative stability bound, not a fitted result.

## 6. Stage B — topology reaches energy transfer

Stage B uses the already generated valid CYCLE and BRANCH trajectories. The
primary observable is

`A_B = max_{1≤t≤2000} H_m(t) / H_total(0)`.

Registered effect:

- `|A_CYCLE-A_BRANCH| > 0.02` at every source centre;
- the sign of `A_CYCLE-A_BRANCH` is identical at all three centres;
- both values exceed the Stage-A exercised-channel floor `0.01`.

The `0.02` floor is ten times the maximum permitted `dt/2` convergence delta
`0.002`. It prevents a phase/peak-discretisation shift from passing as a
topology effect.

Causal and integrity checks:

- a machine-checked configuration diff confirms that CYCLE and BRANCH differ
  only in their registered edge arrays;
- DECOUPLED material energy remains exactly zero to absolute `<1e-12`;
- a fresh deterministic re-run reproduces every unrounded CYCLE/BRANCH `A_B`
  within absolute `<1e-12`;
- NO_BONDS is reported but is not required to favour either fixture; it proves
  the metric is live without supplying a topology label.

Frames are stored every 10 steps; energy and power are stored every step.

## 7. Ordered verdict

Evaluate in this order:

1. **FAIL:** configuration mismatch outside the registered arm intervention,
   non-finite value, initial-energy mismatch `>1e-12`, or computed stability
   bound `dt·ω_upper ≥0.25`.
2. **INCONCLUSIVE:** any valid-arm energy/coupling-identity or `dt/2`
   convergence gate fails, either fixture misses the exercised-channel gate,
   or BROKEN_PAIR misses its sensitivity gate.
3. **PASS:** every Stage-B registered effect and causal check holds.
4. **NULL:** all validity and sensitivity gates hold but at least one Stage-B
   effect or causal check does not.

The predicates are exhaustive and mutually exclusive. The charter's generic
vocabulary yields to this experiment-specific ordered table.

## 8. Consequences

PASS admits design of P1 conditional persistence. It establishes only a
reciprocal, topology-sensitive energy channel in an engineered oscillator
fixture.

NULL closes this Hamiltonian coupling as the Vibrasim-II foundation. FAIL or
INCONCLUSIVE permits correction only of the named validity problem under a new
pre-registration; no thresholds or fixtures are edited after data.

## 9. Prediction and budget

- PASS 45%, NULL 30%, INCONCLUSIVE 20%, FAIL 5%.
- Most likely failure: topology contrast is valid but below `0.02`.

Implementation and tests: 2 hours. Runs: under 15 minutes. Verdict and review:
30 minutes. Realistic 2.75 hours, hard ceiling 5.5 hours.

Raw output: `archive/run-logs/v2-p0/`. Visual output is observational only and
never enters the verdict.

# Pattern: substrate-native world-model agent (backprop-free)

Reusable architecture validated across EQMOD-4 (JEP-1..21b). A grounded, adaptive agent built ONLY from local
learning + relaxation - mapping onto the substrate's own primitives (STDP/BTSP, no backprop):

```
noisy observation
  -> PERCEPTION   : discriminate states (raw-obs prototype clustering) + denoise (multi-glance)   [JEP-12c]
  -> WORLD MODEL  : Successor Representation learned by LOCAL TD == substrate BTSP/eligibility       [JEP-9/11]
  -> PLANNING     : SR-as-value (value iteration / MPC), NOT greedy-on-embedding                     [JEP-11]
  -> ADAPTATION   : reward change -> V=M@r instant; transition change -> edit explicit model + replan [JEP-14b/15b]
```

## Hard-won design rules (each from a NULL that was diagnosed)
1. **Perception vs value have OPPOSITE objectives.** Perception must DISCRIMINATE states; value/structure must be
   SMOOTH across neighbours. One encoder forced to do both does neither (JEP-12 NULL: temporal-coherence collapsed
   states). Use SEPARATE modules.
2. **Greedy 1-step control is brittle** - a 2% value error creates local maxima that trap it (JEP-13c: R^2=0.999
   yet greedy reach 0.47). Use value-iteration / SR-as-value / MPC lookahead, not greedy-on-approximate-value.
3. **Model-free and model-based are complementary.** Cached value (SR) = instant REWARD revaluation but stale on
   TRANSITION change; explicit editable model + MPC = instant TRANSITION recovery (JEP-14b/15b). Keep both.
4. **Denoise perception or error compounds over horizons** (JEP-12b->12c: 0.59 -> 1.00 with multi-glance).
5. **Spatial == relational.** The SAME SR machinery does transitive (1D) and grid (2D) relational inference
   (JEP-17/20b); a low-dim structural prior generalizes sparse relations beyond transitive closure (JEP-21b).

## Method honesty
All established: Hopfield EBM, predictive coding (Whittington-Bogacz), Successor Representation (Dayan;
Stachenfeld grid cells), TD, MPC/value iteration, proto-value functions (Mahadevan), TEM (Whittington). Named
as such. The contribution is the pre-registered, honestly-bounded demonstration that these map onto the
substrate's local/relaxation primitives - NOT new methods, NOT human-level understanding.

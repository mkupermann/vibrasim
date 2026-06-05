# Energy Model + Discovery Frontier Summary (JEP-425 → 441)

Consolidated end-state of the autonomous run that built Michael's affective "energy-cloud" model on
the substrate and mapped the non-linear feature-discovery frontier. Written 2026-06-05. No
transformer, no pretrained model, no backprop anywhere in the substrate path.

## The vision (Michael's)
Concepts are distributed **energy clouds** with a **valence** (bright/positive vs dark/negative);
connections **strengthen with experience**; we **perceive the energies of the environment**, and the
goal was to learn this through experiments — and to find what "new mathematics" it needs.

## What was BUILT (robust positives)
1. **Affect + strengthening (JEP-425).** Per-concept valence (`sm.valence`) + Hebbian
   experience-strengthening (`sm.strength`). The VSA bundles were already the "cloud"; valence and
   strengthening are established (Damasio somatic-marker; Hebb 1949), named.
2. **Energy-driven non-linear learning (JEP-430).** `world/valence_reservoir.py` —
   `ValenceReservoirLearner`: random nonlinear features φ=tanh(Rx+b) + an ONLINE recursive-least-
   squares readout. Learns a non-linear (XOR) affect rule from the scalar energy signal alone,
   held-out 0.90 vs raw-linear chance. Established (reservoir/ELM — Rahimi-Recht, Huang; RLS).
3. **Transfer to the REAL representation (JEP-433).** Balanced parity over the substrate's actual VSA
   energy-clouds: predicts UNSEEN clouds at 0.88-0.91, raw-linear at chance — the toy result holds on
   real distributed representations.
4. **Live integration (JEP-436).** `SubstrateMemory.entity_cloud / learn_valence / predict_valence`:
   the brain predicts the affect of UNTAUGHT concepts (0.98-0.99) from their feature-cloud, returns
   taught values exactly, fails under a shuffled control. Wired into `brain_query` ("what is the
   energy of X?" answers untaught concepts, honestly tagged "(generalized)") and `conversation`
   (trains as the teacher talks).
5. **Durable + retrofit (JEP-437/440).** The learner persists across save/load byte-identically
   (store w,P; re-seed R,b), and existing pre-energy brains backfill from stored valence on first use.
   Pattern: docs/patterns/affective_energy_generalization.md.

## The frontier — "what new math do we need?" (mapped with data)
The energy SIGNAL is not the wall; the wall is **unsupervised non-linear feature discovery**.
- **JEP-426** scalar valence learns LINEAR rules trivially (an honest MISS — I predicted too pessimistically).
- **JEP-427** at chance on non-linear XOR (Minsky-Papert); the right conjunctive features recover it.
- **JEP-428** exhaustive feature search finds the interaction but cost is combinatorial, C(P,k).
- **JEP-429** random features crack order-2 tractably; order-3 needs many units (residual).
- **JEP-432** low-order affect over VSA clouds is largely LINEARLY readable (presence = linear projection).
- **JEP-438** for a pure order-3 rule with NO low-order signal: greedy/incremental discovery gets
  nothing (no gradient to climb); order-3 OMP solves it but enumerates C(P,3).
- **JEP-439** flat random features do NOT match C(P,k) — they need MORE (mix all monomial orders) and
  degrade with N; so **OMP (targeted, exact) is cheaper than random features**. (This corrected a wrong
  "feature-cost == search-cost" claim I made in 438 — honesty over consistency.)
- **JEP-441** random DEPTH (deep ELM) does not beat width — composition of random layers is still
  untargeted.
- **JEP-442 (upper bound)** a LEARNED 2-layer net (backprop, reference baseline only) cracks order-3
  parity at 1.000 with M=64 ≪ C(18,3)=816 and its feature-importance lands exactly on the true triple;
  matched random features are at chance. So *learned* features escape cheaply — the gap is **non-local
  targeted learning**, not capacity or enumeration.

**Net frontier statement.** For an order-k rule with no lower-order signal, every cheap / backprop-
free / non-enumerative route fails: greedy climbing (no gradient), flat random features (≳C(P,k),
N-sensitive), random depth (untargeted). Only **targeted** routes work — order-k enumeration
(O(C(P,k))) or **learned** features (backprop, NON-LOCAL). The open problem is sharply bounded:
**tractable, LOCAL, targeted high-order feature discovery** — one of the five named open problems
(generalization theory, sample-efficient abstraction, local credit assignment, grounding,
compositionality). I located exactly where the new mathematics is needed; I did not invent it (and
said so honestly throughout).

## Honest scope
Everything here is established method (VSA/HRR, reservoir/ELM, RLS, OMP/boosting, Hopfield energy
memory, Damasio/Hebb), named as such. The contribution is the substrate-native ASSEMBLY (energy model
integrated, durable, live in the GUI) and the precise, data-backed MAP of the discovery frontier —
not new science. Three NULLs in the arc were my own design/instrument flaws (431 memorization, 432
imbalance, 434 noise-scale), each caught, diagnosed, corrected, never bar-tuned; two (435, 439) were
genuine conceptual corrections recorded against consistency.

## Where this could go (a real, hard direction — not a knob)
The escape from C(P,k) without backprop is the e-prop / equilibrium-propagation frontier: a LOCAL
credit-assignment rule that targets interaction terms. That is genuine open research, flagged here as
the next-level problem, not attempted as a quick variant.

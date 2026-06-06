# Pattern — Systematic generalization on the substrate (analog VSA + online readout)

**Surfaced by:** BET-124 → BET-130. **Status:** validated substrate capability.

## The capability
The substrate generalizes a learned RELATION to NOVEL combinations of known symbols
(systematic / symbolic-combination generalization — the thing pure memorization,
BET-117, cannot do), learned strictly ONLINE, with NO transformer / backprop /
pretraining. On a comparison relation (label = v[i]>v[j]) it reaches 90.6% on
symbol pairs it never saw (BET-130).

## The three ingredients (all substrate-native)
1. **Compose with analog VSA** (`world/vsa.py`): code(i,j) = bundle_analog(
   bind(ROLE_left, hv[i]), bind(ROLE_right, hv[j]) ). Binding ties roles to fillers;
   ANALOG (non-sign) superposition is essential — the sign() clamp destroys the
   linear value-recoverability and caps generalization at ~0.61 (BET-125 vs 126).
   Normalize codes to unit norm.
2. **Read out with the substrate reservoir / linear RLS** (`world/reservoir.py`):
   an online linear readout on the composed code. Because analog binding is linear,
   a single linear W = w_l⊙role_l − w_r⊙role_r recovers each slot's value and
   computes the relation for ANY pair. Updated online, one example at a time.
3. **Feed it experience**: held-out accuracy is governed by a CURRICULUM LAW — it
   rises monotonically with the number of compositions seen (BET-129: 0.68→0.88 at
   M=14; BET-130: crosses 0.906 at M=20, still climbing). Dimension D and
   normalization are NOT the scaling axis (BET-127/128 NULL); EXPERIENCE is.

## What this means for the project goal
"The substrate learns from every interaction" is now literal and measured: each new
composition experienced raises generalization to unseen ones. This is the engine a
language layer sits on — symbols composed by VSA, a relation/next-symbol read out
online, generalizing to novel contexts.

## Proven boundaries (honest)
- Generalization scales with #compositions, not with representation size — needs
  experience/curriculum, not just a bigger substrate.
- Demonstrated on a relational comparison. Extending to real written-language
  next-symbol prediction over a vocabulary is the open frontier (BET-131+).
- The relation must be linearly recoverable from the composed code; deeply
  non-separable relations may need nonlinear reservoir features to carry them
  (untested here — reservoir ≈ linear on this separable relation).

## Controls that must hold (and did, every time)
- no-binding (roles removed → code(i,j)==code(j,i)): collapses to/below chance.
- shuffled labels: collapses to chance.
If either does NOT collapse, the result is lookup/leakage, not generalization.

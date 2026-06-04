# JEP-105 — inductive generalization: learn a rule from instances (defeasible), a core human faculty

## Why
The engine reasons DEDUCTIVELY (taxonomy closure). Humans also INDUCE: see robins, sparrows, eagles fly -> "birds
fly" -> predict a new bird flies, defeasibly (penguins don't). Add property facts ("X can VERB" / "X cannot VERB"),
induce category-level properties from >=2 instances with no counterexample, and apply to new instances.

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 100%: >=2 flying bird-instances -> induce "birds fly" -> new bird "wren" inherits "fly"; DEFEASIBLE - "a
  penguin cannot fly" overrides so has_property(penguin,fly)=False. MOST-LIKELY MISS: the "cannot/can't/can not"
  negative parse (surface-form negation again) - handled with all three forms explicitly.

## Acceptance
- PASS: induction battery = 100% (induced inheritance + explicit override). Established (inductive generalization /
  Mill's methods; defeasible inheritance), named; no novelty. HONEST: simple majority-with-no-counterexample
  induction; no statistical confidence, no competing-generalization arbitration - a later tier.

## Result — capability PASS, calibration MISS (defeasibility semantics)
Induction battery 5/5: induced bird property {fly}; robin flies (observed), wren flies (INDUCED, never observed),
penguin does NOT fly (explicit override), robin doesn't 'swim' (not induced). Full suite 16 green.
CALIBRATION: MISS. Predicted the "cannot/can't/can not" parse as the risk — it WORKED (penguin's negative recorded).
The actual miss was my own induce() SEMANTICS: I coded "induce only if NO counterexample", so penguin BLOCKED
"birds fly" entirely (60%). That is non-defeasible — the opposite of intent. LESSON: when implementing DEFEASIBLE
reasoning, the general rule must SURVIVE exceptions (which override per-instance), not be blocked by them; I wrote
the inverse. Fixed: induce when positives >=2 and positives > explicit counterexamples. Tally 10/17. Established
(defeasible inductive generalization, default inheritance with exceptions), named; no novelty. HONEST: simple
majority rule, no statistical confidence or competing-generalization arbitration - a later tier.

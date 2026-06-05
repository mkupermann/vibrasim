# JEP-169 — mereology / taxonomy INTERACTION: a dog's heart is part of an animal (and a poodle has a heart)

## Prediction (locked BEFORE run) [predict-calibrate]
- 🔮 the engine does NEITHER interaction currently (part_of and is_a are separate closures) -> both False, a genuine
  understanding gap. Both valid, tractable. RISK: getting a direction wrong / over-generalizing (is-a on the PART
  side must NOT yield part-of; up-then-down must NOT leak a dog's heart into being part of a cat).

## Result — PASS (HIT)
Confirmed the gap (both interactions False; negatives correctly False). The two VALID interactions, now implemented:
1. X part-of Y, Y is-a Z  =>  X part-of Z   ('a heart is part of a dog, a dog is an animal' -> a heart is part of
   an animal). part_of(heart,animal)=True, part_of(cell,animal)=True (2-hop part + is-a).
2. Z is-a Y, X part-of Y  =>  X part-of Z   (a poodle, being a dog, inherits a dog's parts). part_of(heart,poodle)=True.
CRITICAL LEAK GUARD verified: the interactions are applied to each whole on the part-of chain WITHOUT chaining
up-then-down. heart's part-of closure is {dog} only (animal is derived on-demand, not stored as a whole), so
part_of(heart,cat) stays FALSE even though cat is-a animal and dog is-a animal — a dog's heart is NOT part of a cat.
Negatives all hold: is_a(heart,animal) False (part is not type), part_of(animal,heart) False (asymmetric). This is a
genuine DEEP-REASONING improvement: distinct relation types (mereology, taxonomy) now interact with correct, bounded
semantics — a hallmark of human-like understanding. 52/52 regression tests green (+1). Prediction HIT; tally 61/85.
Established (mereological inference, part-whole/taxonomy interaction); named; no novelty.

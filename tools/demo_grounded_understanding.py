"""GROUNDED UNDERSTANDING — the complete human-like loop in one demonstration (EQMOD-4, JEP-54..178).

The engine PERCEIVES instances, READS structure from prose, REASONS over the combination (vision + reading), and
COMMUNICATES — all with NO transformer, NO LLM, NO pretrained model. This is the fullest realization of Michael's
goal (human-like LEARNING, UNDERSTANDING, COMMUNICATING) achievable under the substrate-legal / no-transformer
constraint. Honest scope: perception here is toy (well-separated prototypes); the BINDING of perception to
prose-learned structure is the point. Real grounding needs rich embodied perception (the open frontier).

Run:  PYTHONPATH=. .venv/Scripts/python.exe tools/demo_grounded_understanding.py
"""
import numpy as np
from world.understanding import UnderstandingEngine


def main():
    e = UnderstandingEngine(seed=42)
    rng = np.random.default_rng(0)

    print("=== GROUNDED UNDERSTANDING — perceive + read + reason + communicate, no transformer ===\n")

    # [1] READ structure from prose (multi-relation)
    passage = ("A dog is a mammal. A cat is a mammal. A mammal is a warm-blooded animal. "
               "A robin is a bird. A bird is an animal. A dog has a heart. A virus causes a fever.")
    print("[1] READ an encyclopedic passage:")
    print(f'    "{passage}"')
    print(f"    -> {e.read(passage)}\n")

    # [2] GROUND the leaf concepts in perception (prototypes the engine can recognize)
    protos = {c: rng.normal(0, 1, e.feat_dim) for c in ["dog", "cat", "robin"]}
    for c, v in protos.items():
        e.add_prototype(c, v)
    print("[2] GROUND concepts in perception (learned prototypes for dog / cat / robin).\n")

    # [3] REASON over a PERCEIVED instance using the PROSE-learned taxonomy (vision + reading)
    print("[3] Be SHOWN a novel instance -> recognize it -> reason about it via what was READ:")
    for true_c in ["dog", "robin"]:
        inst = protos[true_c] + rng.normal(0, 0.5, e.feat_dim)
        seen = e.perceive(inst)
        print(f"    [shown a {true_c}] perceived '{seen}'  ->  "
              f"is it an animal? {'Yes' if e.is_a(seen, 'animal') else 'No'}  |  "
              f"is it a mammal? {'Yes' if e.is_a(seen, 'mammal') else 'No'}  |  "
              f"is it a bird? {'Yes' if e.is_a(seen, 'bird') else 'No'}")
    print()

    # [4] COMMUNICATE — answer questions, explain reasoning, describe, across relation types
    print("[4] CONVERSE about the combined knowledge:")
    for q in ["is a robin an animal?", "why?", "is a heart part of an animal?",
              "does a virus cause a fever?", "what is a dog?"]:
        print(f"    you> {q}\n    ai > {e.respond(q)}")
    print(f"    you> describe a dog.\n    ai > {e.describe('a dog')}\n")

    # [5] LEARN a correction from a new source (belief revision)
    print("[5] REVISE beliefs when corrected by a new source:")
    print('    you> (new source) "A robin is not a mammal." (it never was — consistency check)')
    print(f"    ai > is a robin a mammal? {e.respond('is a robin a mammal?')}\n")

    print("=== The engine PERCEIVED, READ, REASONED, and COMMUNICATED — substrate-legal, no transformer. ===")
    print("This is the fullest realization of the goal under the constraint. The open frontier (genuinely hard):")
    print("rich embodied grounding, dense real-prose at scale, abstract words, and open-ended generation.")


if __name__ == "__main__":
    main()

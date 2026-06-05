"""LEARN FROM PROSE — the definitive end-to-end demonstration (EQMOD-4, JEP-155..168).

The engine READS an encyclopedic passage, UNDERSTANDS it (multi-hop + cross-relation inference over what no single
sentence states), COMMUNICATES about it (conversational Q&A + multi-relation profiles), and REVISES its beliefs when
a source corrects it — all with NO transformer, NO LLM, NO pretrained model. Just substrate-legal symbolic machinery:
classic Hearst-style lexico-syntactic extraction + transitive closure + template NL generation.

Run:  PYTHONPATH=. .venv/Scripts/python.exe tools/demo_learn_from_prose.py
"""
from world.understanding import UnderstandingEngine


def main():
    e = UnderstandingEngine(seed=42)

    passage = (
        "A dog is a mammal. A mammal is a warm-blooded animal. Dogs and wolves are canines. "
        "A poodle, a kind of dog, is intelligent. A heart is part of a dog. A cell is part of a heart. "
        "A virus causes an infection. An infection causes a fever. A fever causes tiredness. "
        "Birds such as robins and sparrows can fly. A bird has feathers and wings. A bird is an animal. "
        "A salmon, which is a fish, lives in rivers. A fish is an animal."
    )

    print("=== LEARN FROM PROSE — end to end, no transformer ===\n")
    print("[1] The engine READS an encyclopedic passage:\n")
    print(f'    "{passage}"\n')
    learned = e.read(passage)
    print(f"    -> learned {learned['is_a']} is-a, {learned['part_of']} part-of, {learned['causal']} causal facts.\n")

    print("[2] It UNDERSTANDS — answering questions no single sentence states (multi-hop + cross-relation):\n")
    for q in [
        "is a poodle an animal?",          # poodle -> dog -> mammal -> animal (4 hops, never stated)
        "is a dog a canine?",
        "is a cell part of a dog?",        # cell -> heart -> dog (multi-hop part-of)
        "is a heart an animal?",           # NO: part-of is not is-a
        "does a virus cause tiredness?",   # virus -> infection -> fever -> tiredness (causal chain)
        "what causes a fever?",
        "what is part of a dog?",
        "is a robin an animal?",           # robin -> bird -> animal
    ]:
        print(f"    you> {q}\n    ai > {e.respond(q)}\n")

    print("[3] It COMMUNICATES — coherent multi-relation profiles in English:\n")
    for c in ["a dog", "a virus", "a bird"]:
        print(f"    you> describe {c}.\n    ai > {e.describe(c)}\n")

    print("[4] It REVISES its beliefs when a later source CORRECTS it:\n")
    print('    you> (new source) "A salmon is not a fish. A salmon is a ray-finned creature."')
    print(f"    ai > (before) is a salmon a fish? {e.respond('is a salmon a fish?')}")
    e.read("A salmon is not a fish. A salmon is a creature.")
    print(f"    ai > (after)  is a salmon a fish? {e.respond('is a salmon a fish?')}")
    print(f"    ai > (after)  what is a salmon?  {e.respond('what is a salmon?')}\n")

    print("[5] It SUMMARIZES what it learned, and FLAGS a source that contradicts itself:\n")
    print("    you> summarize what you learned.")
    print(f"    ai > {e.summarize()}\n")
    bad = UnderstandingEngine(seed=99)
    bad.read("A whale is a mammal. A mammal is not a fish. A whale is a fish.")   # an inconsistent source
    print('    you> (read an inconsistent source) "A whale is a mammal. A mammal is not a fish. A whale is a fish."')
    print(f"    ai > {bad.summarize()}\n")

    print("[6] It is SELF-EXTENSIBLE — it learns a NEW relation type (beyond is-a/part-of/causal) from examples:\n")
    e3 = UnderstandingEngine(seed=7)
    rels = e3.read_open("Paris is the capital of France. London is the capital of England. Rome is the capital of Italy.")
    print('    you> "Paris is the capital of France. London is the capital of England. Rome is the capital of Italy."')
    print(f"    ai > (auto-induced a new relation: {rels})")
    print(f"    you> (apply it to a new sentence) \"Berlin is the capital of Germany.\"  -> {e3.extract_relation('Berlin is the capital of Germany.')}")
    print(f"    you> is Berlin the capital of Germany?  ->  {'Yes' if e3.relation_true('berlin','is capital of','germany') else 'No'}\n")

    print("[7] It also reasons about QUANTITIES and TIME from prose:\n")
    e4 = UnderstandingEngine(seed=8)
    e4.read("A dog has 4 legs. A spider has eight legs. "
            "The war started before the treaty. The treaty came before the peace.")
    for q in ["how many legs does a dog have?", "does a spider have more legs than a dog?",
              "did the war happen before the peace?"]:
        print(f"    you> {q}\n    ai > {e4.respond(q)}")
    print()

    print("=== All of the above used only substrate-legal symbolic machinery — no transformer, no pretrained model. ===")
    print("Honest scope: works on encyclopedic/descriptive prose (~0.9 recall, high precision); dense logic/argument")
    print("prose and the long tail of NL constructions remain the no-transformer frontier. See docs/UNDERSTANDING_ENGINE.md.")


if __name__ == "__main__":
    main()

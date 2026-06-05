"""FULL Q&A — the complete conversational breadth of the Understanding Engine (EQMOD-4).

Read one multi-domain passage, then answer EVERY question type the engine supports — taxonomy, mereology, causal,
comparison, temporal, quantitative, open relations, superlatives, enumeration, explanations, epistemic humility —
all in English, NO transformer. The definitive demonstration of 'communicating WITH me'.

Run:  PYTHONPATH=. .venv/Scripts/python.exe tools/demo_full_qa.py
"""
from world.understanding import UnderstandingEngine


def main():
    e = UnderstandingEngine(seed=42)
    passage = (
        "A dog is a mammal. A cat is a mammal. A mammal is an animal. A poodle is a kind of dog. "
        "A heart is part of a dog. A cell is part of a heart. "
        "A virus causes an infection. An infection causes a fever. "
        "A dog has 4 legs. A spider has eight legs. "
        "An elephant is bigger than a dog. A dog is bigger than a cat. "
        "The war started before the treaty. The treaty came before the peace. "
        "Paris is the capital of France. London is the capital of England."
    )
    print("=== FULL Q&A — read once, answer everything (no transformer) ===\n")
    print(f'READ: "{passage}"')
    print(f"  -> {e.read(passage)}\n")

    qa = [
        ("TAXONOMY (multi-hop)", "is a poodle an animal?"),
        ("ENUMERATION", "what are all the mammals?"),
        ("MEREOLOGY (multi-hop)", "is a cell part of a dog?"),
        ("MEREOLOGY x taxonomy", "is a heart part of an animal?"),
        ("CAUSAL (chain)", "does a virus cause a fever?"),
        ("CAUSAL (abduce)", "what causes a fever?"),
        ("QUANTITATIVE", "how many legs does a dog have?"),
        ("QUANTITATIVE (compare)", "does a spider have more legs than a dog?"),
        ("COMPARISON (transitive)", "is an elephant bigger than a cat?"),
        ("COMPARISON (superlative)", "what is the biggest?"),
        ("TEMPORAL (transitive)", "did the war happen before the peace?"),
        ("TEMPORAL (superlative)", "what happened last?"),
        ("OPEN RELATION (learned)", "what is the capital of France?"),
        ("EXPLANATION", "why?"),
        ("EPISTEMIC HUMILITY", "is a poodle a vegetable?"),
    ]
    for label, q in qa:
        print(f"  [{label}]\n  you> {q}\n  ai > {e.respond(q)}")
    print(f"\n  you> describe a dog.\n  ai > {e.describe('a dog')}")
    print(f"  you> summarize.\n  ai > {e.summarize()}")

    print("\n  --- and a MULTI-TURN conversation (it carries context + explains across turns) ---")
    for q in ["is a dog an animal?", "what about a cat?", "why?",
              "is an elephant bigger than a dog?", "what about a mouse?", "why?"]:
        print(f"  you> {q}\n  ai > {e.respond(q)}")
    print("\n=== One engine, one passage, every question type + multi-turn dialogue — substrate-legal, no transformer. ===")


if __name__ == "__main__":
    main()

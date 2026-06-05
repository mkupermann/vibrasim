"""JEP-213 - large multi-domain document: full engine across taxonomy/parts/causal/numeric/temporal/open at scale."""
from world.understanding import UnderstandingEngine
DOC = """
A dog is a mammal. A cat is a mammal. A mammal is a warm-blooded animal. A poodle is a kind of dog.
A robin is a bird. A bird is an animal. A salmon is a fish. A fish is an animal. An animal is an organism.
A heart is part of a dog. A cell is part of a heart. A bird has feathers and wings. A fish has gills.
A virus causes an infection. An infection causes a fever. A fever causes tiredness. Smoking causes cancer.
A dog has 4 legs. A spider has eight legs. A cat has 2 eyes. A bird has 2 wings.
An elephant is bigger than a dog. A dog is bigger than a cat. A cat is bigger than a mouse.
Rome is the capital of Italy. Paris is the capital of France. Berlin is the capital of Germany.
The famine happened before the war. The war started before the treaty. The treaty came before the peace.
"""
def main():
    print("=== JEP-213: large multi-domain document ===", flush=True)
    e=UnderstandingEngine(seed=213); out=e.read(DOC)
    print(f"read {DOC.count('.')}-sentence document -> {out}", flush=True)
    checks=[
        ("is-a multi-hop poodle->organism", e.is_a("poodle","organism"), True),
        ("part-of multi-hop cell->animal", e.part_of("cell","animal"), True),
        ("part-of has gill->fish", e.part_of("gill","fish"), True),
        ("causal chain virus->tiredness", e.causes_effect("virus","tiredness"), True),
        ("numeric how-many dog legs", e.respond("how many legs does a dog have?")=="A dog has 4 legs.", True),
        ("numeric compare spider>dog legs", e.respond("does a spider have more legs than a dog?")=="Yes.", True),
        ("comparison transitive elephant>mouse", e.respond("is an elephant bigger than a mouse?")=="Yes.", True),
        ("temporal transitive famine before peace", e.respond("did the famine happen before the peace?")=="Yes.", True),
        ("open relation capital Paris->France", e.relation_true("paris","is capital of","france"), True),
        ("open WH capital of Germany", e.respond("what is the capital of Germany?")=="Berlin.", True),
        ("NEG cross-domain heart not is-a animal", e.is_a("heart","animal"), False),
        ("NEG temporal peace not before famine", e.respond("did the peace happen before the famine?").startswith("Not"), True),
    ]
    ok=sum(1 for _,g,exp in checks if g==exp)
    for desc,g,exp in checks:
        print(f"  [{'OK' if g==exp else 'XX'}] {desc}: {g}", flush=True)
    print(f"\nmulti-domain correctness at document scale: {ok}/{len(checks)}", flush=True)
    print(f"consistency audit (should be empty - consistent doc): {e.consistency_audit()}", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()

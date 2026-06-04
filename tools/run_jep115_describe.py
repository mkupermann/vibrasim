"""JEP-115 - describe a concept (generative communication from structure). Target 100%."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-115: describe a concept (generation), target 100% ===", flush=True)
    e=UnderstandingEngine(seed=115)
    for f in ["A poodle is a dog.","A poodle is a pet.","A dog is an animal.","An animal is a living thing.",
              "A robin is a bird.","A bird is an animal.","A robin can fly.","A sparrow is a bird.","A sparrow can fly.",
              "the poodle chases the cat."]:
        e.tell(f)
    e.induce()
    d_poodle=e.describe("a poodle")
    d_robin=e.describe("a robin")
    d_unknown=e.describe("a quark")
    print(f"   describe(poodle): {d_poodle}", flush=True)
    print(f"   describe(robin):  {d_robin}", flush=True)
    print(f"   describe(quark):  {d_unknown}", flush=True)
    checks=[
        ("poodle: is a dog and a pet", "is a dog and a pet" in d_poodle or "is a pet and a dog" in d_poodle, True),
        ("poodle: also animal/living thing", "animal" in d_poodle and "living thing" in d_poodle, True),
        ("poodle: chases the cat", "chases the cat" in d_poodle, True),
        ("robin: can fly (induced or own)", "can fly" in d_robin, True),
        ("robin: also animal", "animal" in d_robin, True),
        ("unknown handled", d_unknown.startswith("I don't know"), True),
    ]
    res=[(n,(g==x)) for n,g,x in checks]
    for (n,g,x) in checks:
        print(f"   [{'ok' if g==x else 'MISS'}] {n}: {g}", flush=True)
    npass=sum(b for _,b in res); n=len(res)
    print(f"\n   describe battery: {npass}/{n} = {npass/n*100:.1f}%", flush=True)
    print("JEP-115: PASS - the engine GENERATES coherent descriptions from its knowledge (no transformer)." if npass==n
          else f"JEP-115: NOT YET 100% - {npass/n*100:.1f}%.", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()

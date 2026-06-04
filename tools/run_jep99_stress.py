"""JEP-99 - natural-input stress test: find where the engine breaks on varied phrasings (predict per item)."""
from world.understanding import UnderstandingEngine
def main():
    print("=== JEP-99: natural-input stress test (predict per item, then fix tractable) ===", flush=True)
    e=UnderstandingEngine(seed=99)
    # baseline facts in varied forms
    facts=["A poodle is a dog.","A dog is an animal.","An animal is a living thing.",
           "A big dog is an animal.","Poodles chase cats.","the cat eats the mouse."]
    parsed=[(f, e.tell(f)[0]) for f in facts]
    print("   --- parsing varied facts (isa/rel = parsed, none = FAILED) ---", flush=True)
    for f,t in parsed: print(f"      [{t:>4}] {f}", flush=True)
    # comprehension probes (q, expected, predicted-pass?)
    probes=[
        ("is a poodle an animal", True),
        ("is a poodle a living thing", True),
        ("is a big dog an animal", True),       # adjectival subject
        ("does the poodle chase the cat", True), # plural SVO correctly linked
        ("does the cat eat the mouse", True),
    ]
    print("   --- comprehension ---", flush=True)
    for q,exp in probes:
        got=e.ask(q)
        mark = "ok" if got==exp else "**MISS**"
        print(f"      [{mark}] {q!r} -> {got} (expected {exp})", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()

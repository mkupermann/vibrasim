"""JEP-103 - ingest a small NATURAL paragraph, answer comprehension; locate the next boundary."""
from world.understanding import UnderstandingEngine
PARA = [
    "A robin is a bird.",
    "A bird is an animal.",
    "Robins and sparrows are birds.",     # conjunction (predicted FAIL)
    "the robin eats worms.",
    "It is an animal.",                    # pronoun (predicted FAIL)
    "An animal is a living thing.",
]
def main():
    print("=== JEP-103: small natural paragraph - ingest + comprehend (locate boundary) ===", flush=True)
    e=UnderstandingEngine(seed=103)
    print("   --- ingestion ---", flush=True)
    for s in PARA:
        t=e.tell(s); print(f"      [{t[0]:>7}] {s}", flush=True)
    qs=[
        ("is a robin an animal", True),
        ("is a robin a living thing", True),
        ("is a sparrow a bird", True),      # depends on conjunction parse (predicted miss)
        ("does the robin eat worms", True),
    ]
    print("   --- comprehension ---", flush=True)
    npass=0
    for q,exp in qs:
        got=e.ask(q); ok=(got==exp); npass+=ok
        print(f"      [{'ok' if ok else 'MISS'}] {q!r} -> {got} (exp {exp})", flush=True)
    print(f"\n   paragraph comprehension: {npass}/{len(qs)}", flush=True)
    print("   (predicted: conjunction 'Robins and sparrows...' and pronoun 'It is...' fail -> boundary located)", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()

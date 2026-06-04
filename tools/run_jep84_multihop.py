"""JEP-84 - multi-hop inference: bare VSA retrieval vs substrate+structured transitive closure. The honest line."""
import numpy as np, re
from world.knowledge import KnowledgeBase, tokenize
# single-hop facts only (the 2-hop conclusions are NEVER stated)
FACTS = [
    ("poodle","dog"),("collie","dog"),("dog","animal"),("animal","living_thing"),
    ("salmon","fish"),("fish","animal"),("sparrow","bird"),("bird","animal"),
    ("oak","tree"),("tree","plant"),("plant","living_thing"),
]
def corpus():
    return " ".join(f"A {a} is a {b}." for a,b in FACTS)
# held-out multi-hop (>=2) IS-A queries that are TRUE by transitive closure, plus FALSE distractors
def closure(facts):
    parent={a:b for a,b in facts}; 
    def anc(x):
        out=set(); 
        while x in parent: x=parent[x]; out.add(x)
        return out
    return {x:anc(x) for x in set([a for a,_ in facts])}
def main():
    print("=== JEP-84: multi-hop inference - bare retrieval vs substrate+structure (the understanding line) ===",flush=True)
    anc=closure(FACTS)
    # build true 2+-hop pairs and false pairs
    pos=[(x,c) for x,cs in anc.items() for c in cs if c!=({a:b for a,b in FACTS}).get(x)]  # skip the 1-hop parent
    allcats=set([b for _,b in FACTS])|set([a for a,_ in FACTS])
    rng=np.random.default_rng(84)
    neg=[]
    while len(neg)<len(pos):
        x=rng.choice(list(anc.keys())); c=rng.choice(list(allcats))
        if c not in anc[x] and c!=x and ({a:b for a,b in FACTS}).get(x)!=c: neg.append((x,c))
    # (i) BARE retrieval: ask "is X a C" -> does top passage assert it? (it never will for 2-hop)
    kb=KnowledgeBase(dim=4096); kb.ingest(corpus())
    def bare_isa(x,c):
        ans=kb.answer(f"is a {x} a {c}"); toks=tokenize(ans)
        return (x in toks and c in toks)  # only true if a single passage names both (never, for 2-hop)
    bare=[bare_isa(x,c) for x,c in pos]+[not bare_isa(x,c) for x,c in neg]
    bare_acc=float(np.mean(bare))
    # (ii) substrate + STRUCTURE: parse single-hop facts -> transitive IS-A graph -> closure
    parsed={}
    for p in re.split(r"(?<=\.)\s+", corpus()):
        m=re.match(r"A (\w+) is a (\w+)\.",p)
        if m: parsed[m.group(1)]=m.group(2)
    def struct_anc(x):
        out=set()
        while x in parsed: x=parsed[x]; out.add(x)
        return out
    def struct_isa(x,c): return c in struct_anc(x)
    st=[struct_isa(x,c) for x,c in pos]+[not struct_isa(x,c) for x,c in neg]
    st_acc=float(np.mean(st))
    print(f"   2-hop+ IS-A queries: {len(pos)} true, {len(neg)} false", flush=True)
    print(f"   (i)  BARE VSA retrieval accuracy           = {bare_acc:.3f}", flush=True)
    print(f"   (ii) substrate + structured transitive clos = {st_acc:.3f}", flush=True)
    print("\n--- VERDICT ---",flush=True)
    if st_acc>=0.90 and (st_acc-bare_acc)>=0.30:
        print(f"JEP-84: PASS - multi-hop inference (understanding-by-inference) is reachable WHEN single-hop facts are",flush=True)
        print(f"parsed into the substrate's STRUCTURED primitive (transitive IS-A graph): {st_acc:.2f} on 2-hop+ queries",flush=True)
        print(f"NEVER stated in the source, vs bare retrieval {bare_acc:.2f}. This LOCATES the line: retrieval alone does",flush=True)
        print(f"NOT infer; structure over retrieved facts does. The inference is the structure layer's, not the corpus'.",flush=True)
    else:
        print(f"JEP-84: NULL/PARTIAL - structured {st_acc:.2f}, bare {bare_acc:.2f}. Recorded honestly.",flush=True)
    print("HONEST: the 'understanding' here is transitive closure over PARSED facts - it needs reliable parsing of",flush=True)
    print("source sentences into relations (here regex; real text needs robust extraction) and only does IS-A chains.",flush=True)
    print("Genuine open understanding (arbitrary inference, learned structure) remains the frontier. Established, named.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()

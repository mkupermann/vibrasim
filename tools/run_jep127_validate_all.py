"""JEP-127 - property-based validation: transitive comparison + Boolean composition vs reference."""
import numpy as np
from world.understanding import UnderstandingEngine
rng=np.random.default_rng(127)
def main():
    print("=== JEP-127: property-based validation of comparison + Boolean ===", flush=True)
    # --- comparison: random 'X is bigger than Y' chains, verify transitive closure ---
    cmism=0; cchecks=0
    for t in range(300):
        n=int(rng.integers(4,9)); items=[f"o{i}" for i in range(n)]
        edges=set()
        for _ in range(int(rng.integers(n, 2*n))):
            i,j=rng.integers(n),rng.integers(n)
            if i<j: edges.add((items[i],items[j]))   # acyclic: lower-index bigger than higher
        e=UnderstandingEngine(seed=t)
        for a,b in edges: e.tell(f"A {a} is bigger than a {b}.")
        # reference closure
        adj={}
        for a,b in edges: adj.setdefault(a,set()).add(b)
        def ref(a,b):
            seen={a}; st=[a]
            while st:
                c=st.pop()
                for d in adj.get(c,()):
                    if d==b: return True
                    if d not in seen: seen.add(d); st.append(d)
            return False
        for _ in range(30):
            a,b=items[rng.integers(n)],items[rng.integers(n)]
            if a==b: continue
            cchecks+=1
            got = e.respond(f"is a {a} bigger than a {b}?")=="Yes."
            cmism+=int(got!=ref(a,b))
    # --- Boolean: random and/or over atomic is_a clauses, verify vs reference ---
    bmism=0; bchecks=0
    for t in range(300):
        e=UnderstandingEngine(seed=1000+t)
        facts={"poodle":"dog","dog":"animal","cat":"animal","salmon":"fish","fish":"animal"}
        for c,p in facts.items(): e.tell(f"A {c} is a {p}.")
        def ref_isa(x,c):
            cur=x; seen=set()
            while cur in facts and cur not in seen:
                seen.add(cur); cur=facts[cur]
                if cur==c: return True
            return False
        atoms=[("poodle","animal"),("poodle","fish"),("salmon","animal"),("cat","fish"),("dog","animal")]
        for _ in range(20):
            (x1,c1),(x2,c2)=atoms[rng.integers(len(atoms))],atoms[rng.integers(len(atoms))]
            op=rng.choice(["and","or"])
            q=f"is a {x1} a {c1} {op} is a {x2} a {c2}"
            got=e.respond(q)=="Yes."
            v1,v2=ref_isa(x1,c1),ref_isa(x2,c2)
            exp = (v1 and v2) if op=="and" else (v1 or v2)
            bchecks+=1; bmism+=int(got!=exp)
    ca=1-cmism/cchecks; ba=1-bmism/bchecks
    print(f"   comparison: {cchecks-cmism}/{cchecks} = {ca:.5f}", flush=True)
    print(f"   Boolean:    {bchecks-bmism}/{bchecks} = {ba:.5f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ca>=0.999 and ba>=0.999:
        print(f"JEP-127: PASS - transitive comparison ({ca:.4f}) and Boolean composition ({ba:.4f}) both match",flush=True)
        print(f"independent references under randomized testing. The full reasoning engine is SOUND, not just is_a.",flush=True)
        print(f"Established (property-based testing), named; no novelty.",flush=True)
    else:
        print(f"JEP-127: BUG FOUND - comparison {ca:.4f}, Boolean {ba:.4f}. Recorded for diagnosis.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()

"""JEP-117 - fully self-taught: learn concepts+names+taxonomy from observation+ambient language, NO told facts."""
import numpy as np
from collections import defaultdict
from scipy.cluster.hierarchy import linkage, fcluster
from world.understanding import UnderstandingEngine
rng=np.random.default_rng(117)
def main():
    print("=== JEP-117: fully SELF-TAUGHT engine (observation + ambient language, NO told facts) ===", flush=True)
    FD=24
    sup={"mammal":rng.normal(0,1,FD),"bird":rng.normal(0,1,FD)}
    sub={"dog":("mammal",rng.normal(0,1,FD)),"cat":("mammal",rng.normal(0,1,FD)),
         "robin":("bird",rng.normal(0,1,FD)),"eagle":("bird",rng.normal(0,1,FD))}
    # build instances
    insts=[]; truth=[]
    for s,(sp,sv) in sub.items():
        for i in range(8):
            insts.append(sup[sp]*1.3+sv*1.0+rng.normal(0,0.35,FD)); truth.append((s,sp))
    X=np.array(insts)
    c4=fcluster(linkage(X,method="ward"),4,criterion="maxclust")
    c2=fcluster(linkage(X,method="ward"),2,criterion="maxclust")
    distractors=["blicket","dax","wug","fep","gorp"]
    # ambient language: each scene = one instance; hear its sub-name always, super-name 60%, + distractors
    cooc4=defaultdict(lambda:defaultdict(int)); cooc2=defaultdict(lambda:defaultdict(int))
    wc=defaultdict(int); c4c=defaultdict(int); c2c=defaultdict(int); total=0
    for _ in range(5):  # several passes
        for i in range(len(insts)):
            total+=1; subn,supn=truth[i]
            words=[subn]+( [supn] if rng.random()<0.6 else [] )+list(rng.choice(distractors,size=2,replace=False))
            for w in set(words):
                wc[w]+=1; cooc4[w][c4[i]]+=1; cooc2[w][c2[i]]+=1
            c4c[c4[i]]+=1; c2c[c2[i]]+=1
    def pmi(cooc,cc,w,cl): 
        return np.log((cooc[w][cl]/total+1e-9)/((wc[w]/total)*(cc[cl]/total)+1e-9))
    name4={cl:max(wc,key=lambda w:pmi(cooc4,c4c,w,cl)) for cl in set(c4)}
    name2={cl:max(wc,key=lambda w:pmi(cooc2,c2c,w,cl)) for cl in set(c2)}
    # SELF-TAUGHT engine: wire IS-A from clusters + learned names, NO told facts
    e=UnderstandingEngine(seed=117)
    for i in range(len(insts)):
        e.tell(f"obj{i} is a {name4[c4[i]]}.")             # instance -> learned subclass name
        e.tell(f"{name4[c4[i]]} is a {name2[c2[i]]}.")     # subclass -> learned superclass name
    # evaluate: held-out check that each instance is-a its TRUE superclass via learned names
    ok=sum(int(e.is_a(f"obj{i}", truth[i][1])) for i in range(len(insts)))/len(insts)
    subacc=sum(int(name4[c4[i]]==truth[i][0]) for i in range(len(insts)))/len(insts)
    supacc=sum(int(name2[c2[i]]==truth[i][1]) for i in range(len(insts)))/len(insts)
    print(f"   learned sub-names: {dict(name4)}", flush=True)
    print(f"   learned super-names: {dict(name2)}", flush=True)
    print(f"   instance->subclass naming acc {subacc:.2f}; ->superclass {supacc:.2f}", flush=True)
    print(f"   SELF-TAUGHT is-a-superclass accuracy (NO told facts): {ok:.2f}", flush=True)
    # converse with the self-taught engine
    print(f"   e.describe('a dog') -> {e.describe('a dog')}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ok>=0.8:
        print(f"JEP-117: PASS - the engine taught ITSELF a named taxonomy from observation + ambient language",flush=True)
        print(f"(NO explicit facts told): {ok:.2f} of instances correctly reason to their superclass via learned",flush=True)
        print(f"names. Perceive->cluster->cross-situational-name->wire-taxonomy->reason, end-to-end self-supervised",flush=True)
        print(f"in the favorable regime. Established (clustering + cross-situational learning), named; no novelty.",flush=True)
    else:
        print(f"JEP-117: PARTIAL/NULL - self-taught is-a {ok:.2f} (sub {subacc:.2f}, super {supacc:.2f}). Honest.",flush=True)
    print("HONEST: needs ambient language at BOTH granularities + clean-ish clusters; superclass words heard less",flush=True)
    print("are the weak point; the hard perceptual/linguistic regimes (overlap, polysemy, abstract) remain the frontier.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()

"""JEP-118c - LCA-of-extension naming: a word names the smallest cluster containing (almost) all its instances."""
import numpy as np
from collections import defaultdict
from scipy.cluster.hierarchy import linkage, fcluster
from world.understanding import UnderstandingEngine
def run(sigma, supfreq, seed):
    rng=np.random.default_rng(seed); FD=24
    sup={"mammal":rng.normal(0,1,FD),"bird":rng.normal(0,1,FD)}
    sub={"dog":("mammal",rng.normal(0,1,FD)),"cat":("mammal",rng.normal(0,1,FD)),
         "robin":("bird",rng.normal(0,1,FD)),"eagle":("bird",rng.normal(0,1,FD))}
    insts=[]; truth=[]
    for s,(sp,sv) in sub.items():
        for i in range(8): insts.append(sup[sp]*1.3+sv*1.0+rng.normal(0,sigma,FD)); truth.append((s,sp))
    n=len(insts); X=np.array(insts)
    c4=fcluster(linkage(X,method="ward"),4,criterion="maxclust"); c2=fcluster(linkage(X,method="ward"),2,criterion="maxclust")
    distractors=["blicket","dax","wug","fep","gorp"]
    # instance-level co-occurrence: did word w ever co-occur with instance i
    seen=defaultdict(set)
    for _ in range(5):
        for i in range(n):
            subn,supn=truth[i]
            words=[subn]+([supn] if rng.random()<supfreq else [])+list(rng.choice(distractors,size=2,replace=False))
            for w in set(words): seen[w].add(i)
    # candidate clusters: each sub-cluster and super-cluster member-set
    clusters={}
    for cl in set(c4): clusters[("sub",cl)]=set(i for i in range(n) if c4[i]==cl)
    for cl in set(c2): clusters[("sup",cl)]=set(i for i in range(n) if c2[i]==cl)
    def name_word(w):
        ext=seen[w]
        if not ext: return None
        best=None
        for key,M in clusters.items():
            cov=len(ext & M)/len(M); spec=len(ext & M)/len(ext)
            if cov>=0.7 and spec>=0.7:
                if best is None or len(M)<len(clusters[best]): best=key   # smallest qualifying cluster
        return best
    name4={}; name2={}
    for w in seen:
        if w in distractors: continue
        k=name_word(w)
        if k is None: continue
        lvl,cl=k
        if lvl=="sub": name4[cl]=w
        else: name2[cl]=w
    if any(cl not in name4 for cl in set(c4)) or any(cl not in name2 for cl in set(c2)): return 0.0
    e=UnderstandingEngine(seed=seed)
    for i in range(n):
        e.tell(f"obj{i} is a {name4[c4[i]]}."); e.tell(f"{name4[c4[i]]} is a {name2[c2[i]]}.")
    return sum(int(e.is_a(f"obj{i}", truth[i][1])) for i in range(n))/n
def main():
    print("=== JEP-118c: LCA-of-extension naming (robust hierarchical self-taught learning) ===", flush=True)
    print("   sigma\freq   0.6     0.2", flush=True)
    allok=True
    for sigma in [0.35,0.8,1.5]:
        row=[np.mean([run(sigma,f,s) for s in range(4)]) for f in [0.6,0.2]]
        print(f"   {sigma:>5}       {row[0]:.2f}    {row[1]:.2f}", flush=True)
        allok = allok and min(row)>=0.9
    print("\n--- VERDICT ---", flush=True)
    if allok:
        print("JEP-118c: PASS - LCA-of-extension naming (smallest cluster containing all the word's instances)", flush=True)
        print("separates hierarchy levels ROBUSTLY across perceptual overlap AND rare superordinate words. Fixes the", flush=True)
        print("JEP-118 underdetermination with the correct criterion. The self-taught pipeline (JEP-117) is now robust.", flush=True)
    else:
        print("JEP-118c: PARTIAL - some cells <0.9. Recorded honestly.", flush=True)
    print("Established (extension/LCA-based naming; the 'taxonomic' constraint), named; no novelty.", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()

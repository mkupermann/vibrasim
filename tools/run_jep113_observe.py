"""JEP-113 - discover a taxonomy by clustering observations, feed it to the engine, reason over it."""
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from world.understanding import UnderstandingEngine
rng=np.random.default_rng(113)
def main():
    print("=== JEP-113: learn taxonomy by OBSERVATION -> reason over self-discovered structure ===", flush=True)
    # ground-truth hierarchy: 2 superclasses x 2 subclasses x instances, hierarchically-structured features
    FD=24
    sup={ "mammal":rng.normal(0,1,FD), "bird":rng.normal(0,1,FD) }
    sub={ "dog":("mammal",rng.normal(0,1,FD)), "cat":("mammal",rng.normal(0,1,FD)),
          "robin":("bird",rng.normal(0,1,FD)), "eagle":("bird",rng.normal(0,1,FD)) }
    leaves=[]; truth={}   # leaf -> (subclass, superclass)
    for s,(sp,sv) in sub.items():
        for i in range(6):
            feat = sup[sp]*1.3 + sv*1.0 + rng.normal(0,0.35,FD)   # coarse-distinctive (JEP-54 condition)
            name=f"{s}{i}"; leaves.append((name,feat)); truth[name]=(s,sp)
    X=np.array([f for _,f in leaves]); names=[n for n,_ in leaves]
    Z=linkage(X,method="ward")
    # cut into 2 (superclass) and 4 (subclass) clusters -> build IS-A from the two granularities
    c2=fcluster(Z,2,criterion="maxclust"); c4=fcluster(Z,4,criterion="maxclust")
    e=UnderstandingEngine(seed=113)
    # name discovered clusters and wire IS-A: leaf -> sub-cluster -> super-cluster
    for i,n in enumerate(names):
        e.tell(f"{n} is sub{c4[i]}.")
        e.tell(f"sub{c4[i]} is super{c2[i]}.")
    # evaluate: do two leaves of the SAME true subclass share a discovered ancestor? (purity of structure)
    def disc_anc(n): return e.ancestors(n)
    agree=0; tot=0
    for i in range(len(names)):
        for j in range(i+1,len(names)):
            same_sub = truth[names[i]][0]==truth[names[j]][0]
            shares = len(disc_anc(names[i]) & disc_anc(names[j]))>0
            # same subclass should share an ancestor; different superclass should NOT share the top
            agree += int(same_sub == shares if truth[names[i]][1]!=truth[names[j]][1] else True)
            tot+=1
    # cleaner metric: cluster purity of c4 vs true subclass
    from collections import Counter
    pur=0
    for cl in set(c4):
        members=[truth[names[i]][0] for i in range(len(names)) if c4[i]==cl]
        pur+=Counter(members).most_common(1)[0][1]
    purity=pur/len(names)
    # super purity
    psup=0
    for cl in set(c2):
        members=[truth[names[i]][1] for i in range(len(names)) if c2[i]==cl]
        psup+=Counter(members).most_common(1)[0][1]
    spurity=psup/len(names)
    print(f"   discovered 4 subclusters: purity vs true subclass = {purity:.2f}", flush=True)
    print(f"   discovered 2 superclusters: purity vs true superclass = {spurity:.2f}", flush=True)
    # the engine reasons over the discovered graph: a leaf is-a its discovered super
    ok=sum(int(f"super{c2[i]}" in e.ancestors(names[i])) for i in range(len(names)))/len(names)
    print(f"   engine multi-hop over self-discovered taxonomy (leaf is-a its supercluster): {ok:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if purity>=0.8 and spurity>=0.8 and ok>=0.99:
        print(f"JEP-113: PASS - taxonomy LEARNED BY OBSERVATION (clustering, no IS-A told) feeds the engine: subclass",flush=True)
        print(f"purity {purity:.2f}, superclass {spurity:.2f}; the engine reasons multi-hop over the self-discovered",flush=True)
        print(f"graph ({ok:.2f}). Learning-by-observation -> reasoning, end-to-end. Works when features are",flush=True)
        print(f"hierarchically structured (JEP-54 condition). Established (agglomerative clustering), named; no novelty.",flush=True)
    else:
        print(f"JEP-113: PARTIAL/NULL - purity {purity:.2f}/{spurity:.2f}, reasoning {ok:.2f}. Recorded honestly.",flush=True)
    print("HONEST: works because features are coarse-distinctive (the JEP-54 condition); non-hierarchical features",flush=True)
    print("would degrade (JEP-69/70 limit). Cluster NAMES are arbitrary (super1/sub3) - no semantic labels learned.",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()

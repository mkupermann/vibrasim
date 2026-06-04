"""JEP-114 - name self-discovered clusters from a few labels; reason with real names. Target >=0.9."""
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from collections import Counter
from world.understanding import UnderstandingEngine
rng=np.random.default_rng(114)
def main():
    print("=== JEP-114: name discovered clusters from a few labels (structure->meaning) ===", flush=True)
    FD=24
    sup={"mammal":rng.normal(0,1,FD),"bird":rng.normal(0,1,FD)}
    sub={"dog":("mammal",rng.normal(0,1,FD)),"cat":("mammal",rng.normal(0,1,FD)),
         "robin":("bird",rng.normal(0,1,FD)),"eagle":("bird",rng.normal(0,1,FD))}
    names=[]; truth={}; feats=[]
    for s,(sp,sv) in sub.items():
        for i in range(6):
            feats.append(sup[sp]*1.3+sv*1.0+rng.normal(0,0.35,FD)); n=f"obj{len(names)}"; names.append(n); truth[n]=(s,sp)
    X=np.array(feats)
    c4=fcluster(linkage(X,method="ward"),4,criterion="maxclust")
    c2=fcluster(linkage(X,method="ward"),2,criterion="maxclust")
    # ONE label per sub-cluster and per super-cluster (semi-supervised)
    sub_label={}; 
    for cl in set(c4):
        idx=[i for i in range(len(names)) if c4[i]==cl]; sub_label[cl]=truth[names[idx[0]]][0]   # 1 label
    sup_label={}
    for cl in set(c2):
        idx=[i for i in range(len(names)) if c2[i]==cl]; sup_label[cl]=truth[names[idx[0]]][1]
    e=UnderstandingEngine(seed=114)
    # build NAMED taxonomy: every instance is-a its (named) subclass; subclass is-a its (named) superclass
    labeled_idx=set()
    for cl in set(c4):
        idx=[i for i in range(len(names)) if c4[i]==cl]; labeled_idx.add(idx[0])
    for i,n in enumerate(names):
        e.tell(f"{n} is a {sub_label[c4[i]]}.")
        e.tell(f"{sub_label[c4[i]]} is a {sup_label[c2[i]]}.")
    # evaluate on instances that were NOT the labeled exemplar
    ok=tot=0
    for i,n in enumerate(names):
        if i in labeled_idx: continue
        tot+=1
        ok+= int(e.is_a(n, truth[n][0]) and e.is_a(n, truth[n][1]))   # real-name sub + super
    acc=ok/tot
    print(f"   labeled exemplars: {len(labeled_idx)} (1 per sub-cluster); unlabeled instances tested: {tot}", flush=True)
    print(f"   unlabeled instances correctly is-a their NAMED category + supercategory: {acc:.2f}", flush=True)
    print(f"   example: {[n for i,n in enumerate(names) if i not in labeled_idx][0]} -> "
          f"{sorted(e.ancestors([n for i,n in enumerate(names) if i not in labeled_idx][0]))}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc>=0.9:
        print(f"JEP-114: PASS - ONE label per discovered cluster NAMES it; {acc:.2f} of never-labeled instances then",flush=True)
        print(f"reason with REAL names over the self-discovered taxonomy. Structure (clustering) + meaning (few labels)",flush=True)
        print(f"-> a named taxonomy the engine reasons over. Semi-supervised, human-like (one example names a kind).",flush=True)
    else:
        print(f"JEP-114: PARTIAL/NULL - {acc:.2f} < 0.9. Recorded honestly.",flush=True)
    print("HONEST: needs >=1 label per cluster + pure clusters (JEP-113 condition); a cluster with no label stays",flush=True)
    print("nameless, an impure cluster mislabels. Bridges structure->meaning ONLY with a labeling signal (not zero-shot).",flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()

"""JEP-62 - functional concept formation from AFFORDANCES (interaction outcomes) vs appearance."""
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from collections import Counter
rng=np.random.default_rng(62)
N=60; F=4; VD=12; AD=10
func=rng.integers(0,F,N)                       # hidden function per item
visual=rng.normal(0,1,(N,VD))                  # appearance: UNCORRELATED with function
func_proto=rng.normal(0,1,(F,AD))              # each function affords a distinct outcome
def purity(feat):
    Z=linkage(feat,method="ward"); cl=fcluster(Z,F,criterion="maxclust")
    tot=0
    for c in set(cl):
        idx=[i for i in range(N) if cl[i]==c]
        tot+=Counter(func[i] for i in idx).most_common(1)[0][1]
    return tot/N
def main():
    print("=== JEP-62: functional concepts from AFFORDANCE (interaction) vs APPEARANCE ===", flush=True)
    pv=purity(visual)
    print(f"  appearance-based cluster purity = {pv:.3f}  (chance ~{1/F:.2f})", flush=True)
    print("   affordance-noise   affordance-cluster-purity", flush=True)
    rows=[]
    for sigma in [0.3,0.8,1.5,2.5]:
        aff=np.array([func_proto[func[i]]+rng.normal(0,sigma,AD) for i in range(N)])
        pa=purity(aff); rows.append((sigma,pa)); print(f"   {sigma:.1f}              {pa:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    low=rows[0][1]
    if low>=0.9 and low>=pv+0.3:
        print(f"JEP-62: PASS - INTERACTION/AFFORDANCE grounding recovers functional categories appearance CANNOT:", flush=True)
        print(f"clustering on affordance outcomes (what interacting reveals) reaches purity {low:.2f} vs appearance's", flush=True)
        print(f"{pv:.2f} (~chance). When function is UNCORRELATED with appearance, the agent must ACT to discover", flush=True)
        print(f"categories - and affordances do recover them, degrading gracefully with affordance noise. This is the", flush=True)
        print(f"non-visual-signal path (JEP-60 frontier) made concrete: functional concepts from interaction.", flush=True)
        print(f"Established (clustering, affordance learning), named as such.", flush=True)
    else:
        print(f"JEP-62: PARTIAL/NULL - affordance {low:.2f}, appearance {pv:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()

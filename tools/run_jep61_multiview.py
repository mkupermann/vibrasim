"""JEP-61 - multi-view (pixels+shape) concept formation vs each alone (Fashion-MNIST functional purity)."""
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from collections import Counter
d=np.load("data/fashion_mnist.npz")
X=d["x_train"].reshape(-1,28,28).astype(np.float32)/255.0; y=d["y_train"]
names=["t-shirt","trouser","pullover","dress","coat","sandal","shirt","sneaker","bag","ankle_boot"]
means=np.array([X[y==k].mean(0) for k in range(10)])
pixels=means.reshape(10,784)
rowp=means.sum(2); colp=means.sum(1)
shape=np.concatenate([rowp/rowp.max(1,keepdims=True), colp/colp.max(1,keepdims=True)],1)
def z(F): return (F-F.mean(0))/(F.std(0)+1e-9)
fusion=np.concatenate([z(pixels), z(shape)],1)
# functional ground-truth groups
fg={0:0,2:0,4:0,6:0, 1:1,3:1, 5:2,7:2,9:2, 8:3}  # tops/lower/footwear/accessory
true=np.array([fg[i] for i in range(10)])
def purity(F):
    Z=linkage(F,method="ward"); cl=fcluster(Z,4,criterion="maxclust")
    tot=0
    for c in set(cl):
        idx=[i for i in range(10) if cl[i]==c]
        maj=Counter(true[i] for i in idx).most_common(1)[0][1]; tot+=maj
    return tot/10, cl
def main():
    print("=== JEP-61: multi-view fusion concept formation (functional purity) ===", flush=True)
    pp,_=purity(pixels); sp,_=purity(shape); fp,fcl=purity(fusion)
    print(f"  cluster purity vs functional groups:  pixels={pp:.2f}  shape={sp:.2f}  fusion={fp:.2f}", flush=True)
    print("  fusion clusters:", flush=True)
    for c in sorted(set(fcl)):
        print(f"    {[names[i] for i in range(10) if fcl[i]==c]}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if fp>=max(pp,sp) and fp>=0.8:
        print(f"JEP-61: PASS - multi-view FUSION (pixels+shape) >= best single view on functional purity ({fp:.2f} vs", flush=True)
        print(f"pixels {pp:.2f}, shape {sp:.2f}). Combining two real feature views improves (or matches-best)", flush=True)
        print(f"functional concept formation, unsupervised - a concrete step on the multi-view path toward functional", flush=True)
        print(f"grounding (JEP-60 frontier). Established (multi-view clustering), named as such.", flush=True)
    elif fp>=max(pp,sp):
        print(f"JEP-61: PARTIAL - fusion matches best single view ({fp:.2f}) but <0.8; multi-view helps but limited.", flush=True)
    else:
        print(f"JEP-61: NULL - fusion ({fp:.2f}) < best single view (pixels {pp:.2f}, shape {sp:.2f}); naive concat", flush=True)
        print(f"fusion does NOT beat the best single view here (the weaker view's noise can hurt). Honest.", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()

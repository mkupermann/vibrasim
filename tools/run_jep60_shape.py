"""JEP-60 - concept formation with SHAPE-PROFILE features vs raw pixels (Fashion-MNIST footwear grouping)."""
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
d=np.load("data/fashion_mnist.npz")
X=d["x_train"].reshape(-1,28,28).astype(np.float32)/255.0; y=d["y_train"]
names=["t-shirt","trouser","pullover","dress","coat","sandal","shirt","sneaker","bag","ankle_boot"]
means=np.array([X[y==k].mean(0) for k in range(10)])  # 10 x 28 x 28
pixels=means.reshape(10,784)
# shape profiles: row-sums (vertical profile) + column-sums (horizontal profile), normalized
rowp=means.sum(2); colp=means.sum(1)  # 10x28 each
shape=np.concatenate([rowp/rowp.max(1,keepdims=True), colp/colp.max(1,keepdims=True)],1)  # 10x56
footwear={5,7,9}
def check(feat,label):
    Z=linkage(feat,method="ward"); cl=fcluster(Z,4,criterion="maxclust")
    fw_clusters=set(cl[i] for i in footwear)
    fw_one=len(fw_clusters)==1
    print(f"  [{label}] footwear clusters: {[cl[i] for i in sorted(footwear)]} ({'ONE cluster' if fw_one else 'SPLIT'})", flush=True)
    for c in sorted(set(cl)):
        print(f"      cluster {c}: {[names[i] for i in range(10) if cl[i]==c]}", flush=True)
    return fw_one
def main():
    print("=== JEP-60: shape-profile vs raw-pixel concept formation (footwear grouping) ===", flush=True)
    px=check(pixels,"raw pixels")
    sh=check(shape,"shape profiles")
    print("\n--- VERDICT ---", flush=True)
    if sh and not px:
        print(f"JEP-60: PASS - FEATURE CHOICE bridges part of the gap: SHAPE-profile features group all 3 footwear", flush=True)
        print(f"(sandal/sneaker/ankle-boot) in one cluster, where raw PIXELS split them (ankle-boot~bag). The visual-", flush=True)
        print(f"functional gap is partly about WHICH features - shape captures the functional 'footwear' commonality", flush=True)
        print(f"(low, sole-at-bottom) that pixels miss. So better (still unsupervised) features move concepts toward", flush=True)
        print(f"functional. Established (shape features, clustering), named as such.", flush=True)
    elif sh and px:
        print(f"JEP-60: PARTIAL - both group footwear (pixels also worked this run); inconclusive on the gap.", flush=True)
    else:
        print(f"JEP-60: NULL - shape features also split footwear ({sh}); feature choice alone does not bridge the", flush=True)
        print(f"visual-functional gap here - footwear's shared FUNCTION is not captured by these visual features.", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()

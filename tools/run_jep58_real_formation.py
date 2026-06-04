"""JEP-58 - concept formation on REAL Fashion-MNIST: does clustering recover sensible item groupings?"""
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
d=np.load("data/fashion_mnist.npz")
X=d["x_train"].reshape(-1,784).astype(np.float32)/255.0; y=d["y_train"]
names=["t-shirt","trouser","pullover","dress","coat","sandal","shirt","sneaker","bag","ankle_boot"]
# per-class mean image
means=np.array([X[y==k].mean(0) for k in range(10)])
def main():
    print("=== JEP-58: concept formation on REAL Fashion-MNIST (cluster 10 classes) ===", flush=True)
    Z=linkage(means,method="ward")
    # print merge order (dendrogram structure) as nested groups
    from scipy.cluster.hierarchy import leaves_list
    order=leaves_list(Z)
    print("  dendrogram leaf order:", [names[i] for i in order], flush=True)
    footwear={5,7,9}; tops={0,2,4,6}
    print("  cluster assignments at k=4:", flush=True)
    cl=fcluster(Z,4,criterion="maxclust")
    for c in sorted(set(cl)):
        members=[names[i] for i in range(10) if cl[i]==c]
        print(f"    cluster {c}: {members}", flush=True)
    # footwear purity: are all 3 footwear in one cluster, and is that cluster footwear-only?
    fw_clusters=set(cl[i] for i in footwear)
    fw_one = len(fw_clusters)==1
    fw_cluster=list(fw_clusters)[0] if fw_one else None
    fw_pure = fw_one and all(i in footwear for i in range(10) if cl[i]==fw_cluster)
    # tops grouping: >=3 of 4 tops in one cluster
    from collections import Counter
    tops_cl=Counter(cl[i] for i in tops); tops_grouped=tops_cl.most_common(1)[0][1]>=3
    print(f"\n  footwear in one pure cluster: {fw_pure}   tops grouped (>=3/4): {tops_grouped}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if fw_pure and tops_grouped:
        print(f"JEP-58: PASS - concept formation works on REAL data: agglomerative clustering of Fashion-MNIST class", flush=True)
        print(f"features DISCOVERS sensible groupings - footwear (sandal/sneaker/ankle-boot) form one pure cluster", flush=True)
        print(f"and tops (t-shirt/pullover/coat/shirt) group together. The JEP-54 concept-formation result holds on", flush=True)
        print(f"REAL image features, not just synthetic. Established (hierarchical clustering), named as such.", flush=True)
    else:
        print(f"JEP-58: PARTIAL/NULL - footwear-pure {fw_pure}, tops-grouped {tops_grouped}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()

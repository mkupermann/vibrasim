"""JEP-189 - hierarchical concept discovery from REAL images: does visual clustering recover a sensible taxonomy?"""
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from collections import Counter
from world.understanding import UnderstandingEngine
def purity(labels, truth):
    return sum(Counter([truth[i] for i in range(len(truth)) if labels[i]==c]).most_common(1)[0][1]
               for c in set(labels))/len(truth)
def main():
    print("=== JEP-189: hierarchical concept discovery from Fashion-MNIST ===", flush=True)
    d=np.load("data/fashion_mnist.npz"); X=d["x_train"].astype(np.float32)/255.0; y=d["y_train"]
    # 2 super-categories: TOPS {tshirt0, pullover2, coat4}  vs  FOOTWEAR {sandal5, sneaker7, ankleboot9}
    sup={0:"tops",2:"tops",4:"tops",5:"footwear",7:"footwear",9:"footwear"}
    rng=np.random.default_rng(0); idx=[]
    for c in sup: idx+=list(rng.choice(np.where(y==c)[0], 15, replace=False))
    rng.shuffle(idx); Xs=X[idx]; ys=y[idx]; ysup=[sup[c] for c in ys]
    Z=linkage(Xs, method="ward")
    # TOP-level split (2 clusters): does it separate tops vs footwear?
    top=fcluster(Z, t=2, criterion="maxclust"); top_pur=purity(top, ysup)
    # SUB-level (6 clusters): does it recover individual classes?
    sub=fcluster(Z, t=6, criterion="maxclust"); sub_pur=purity(sub, list(ys))
    print(f"  top-level (2 clusters) purity vs tops/footwear: {top_pur:.2f}", flush=True)
    print(f"  sub-level (6 clusters) purity vs individual classes: {sub_pur:.2f}", flush=True)
    # build the discovered 2-level taxonomy, ground with prose, reason multi-hop
    e=UnderstandingEngine(seed=189, feat_dim=784)
    # map each sub-cluster to its majority class + super
    for sc in sorted(set(sub)):
        members=[Xs[i] for i in range(len(Xs)) if sub[i]==sc]
        majcls=Counter([ys[i] for i in range(len(ys)) if sub[i]==sc]).most_common(1)[0][0]
        majtop=Counter([top[i] for i in range(len(top)) if sub[i]==sc]).most_common(1)[0][0]
        e.learn_concept(f"sub{sc}", members)
        # ground: the discovered sub-concept is-a its discovered super-concept (named by majority super)
        supname=Counter([ysup[i] for i in range(len(ysup)) if sub[i]==sc]).most_common(1)[0][0]
        e.read(f"A sub{sc} is a {supname}.")
    e.read("Tops is a garment. Footwear is a garment. A garment is a clothing item.")
    # reason: a NEW test image -> sub-concept -> super -> garment (multi-hop over the DISCOVERED hierarchy)
    ok=[]
    for c in sup:
        te=rng.choice(np.where(d["y_test"]==c)[0], 10, replace=False)
        for i in te:
            seen=e.perceive(d["x_test"][i].astype(np.float32)/255.0)
            ok.append(bool(seen) and e.is_a(seen,"garment"))   # all are garments (sanity that the hierarchy connects)
    print(f"  NEW image -> discovered sub -> super -> 'is it a garment?' (multi-hop over discovered hierarchy): {np.mean(ok):.2f}", flush=True)
    print("\n--- FINDING (fill from numbers) ---", flush=True)
    print("DONE",flush=True)
if __name__=="__main__": main()

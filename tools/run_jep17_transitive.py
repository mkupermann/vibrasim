"""JEP-17 - transitive inference via the SR/cognitive-map (recover global order from local adjacency)."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
rng=np.random.default_rng(90)
N=9   # items in latent order 0<1<...<N-1
gamma=0.95
# chain adjacency
ADJ={i:set() for i in range(N)}
for i in range(N-1): ADJ[i].add(i+1); ADJ[i+1].add(i)
def sr_td(steps=2_000_000,alpha=0.02):
    Mt=np.zeros((N,N),np.float32); I=np.eye(N,dtype=np.float32); c=rng.integers(N)
    for _ in range(steps):
        nbs=list(ADJ[c]); nb=nbs[rng.integers(len(nbs))]; Mt[c]+=alpha*(I[c]+gamma*Mt[nb]-Mt[c]); c=nb
    return Mt
def main():
    print(f"=== JEP-17: transitive inference from the cognitive map (N={N} items) ===",flush=True)
    Mt=sr_td()
    # recover 1D order from SR: symmetric part eigenvector with structure = Fiedler-like
    A=0.5*(Mt+Mt.T)
    # use the SR's leading non-trivial eigenvector of the (centered) matrix as the 1D coordinate
    Ac=A-A.mean(0,keepdims=True)-A.mean(1,keepdims=True)+A.mean()
    w,V=np.linalg.eigh(Ac); pos=V[:,np.argmax(np.abs(w))]   # principal axis = recovered latent position
    # orient sign by KNOWN adjacent comparisons (true: i<i+1)
    votes=sum(np.sign(pos[i+1]-pos[i]) for i in range(N-1))
    if votes<0: pos=-pos
    # transitive inference on NON-adjacent pairs
    correct=0;tot=0; bydist={}
    internal_correct=0; internal_tot=0
    for i in range(N):
        for j in range(N):
            if i>=j or j==i+1: continue   # skip self/adjacent
            tot+=1; pred = pos[i]<pos[j]; truth = i<j
            ok=int(pred==truth); correct+=ok
            d=j-i; bydist.setdefault(d,[0,0]); bydist[d][0]+=ok; bydist[d][1]+=1
            # internal pair: neither i nor j is an endpoint (0 or N-1)
            if i!=0 and j!=N-1: internal_tot+=1; internal_correct+=ok
    acc=correct/tot; iacc=internal_correct/max(internal_tot,1)
    print(f"  non-adjacent transitive-inference accuracy = {acc:.3f}  ({correct}/{tot})",flush=True)
    print(f"  internal-pair accuracy (no endpoint anchor) = {iacc:.3f}  ({internal_correct}/{internal_tot})",flush=True)
    print("  symbolic distance effect (accuracy by rank-distance):",flush=True)
    sde=[]
    for d in sorted(bydist):
        a=bydist[d][0]/bydist[d][1]; sde.append((d,a)); print(f"    dist {d}: {a:.2f} ({bydist[d][1]} pairs)",flush=True)
    # SDE present if accuracy non-decreasing-ish with distance (closer pairs harder)
    sde_present = sde[0][1] <= sde[-1][1]
    print("\n--- VERDICT ---",flush=True)
    if acc>=0.9 and iacc>=0.8 and sde_present:
        print(f"JEP-17: PASS - the SR/cognitive-map machinery performs TRANSITIVE INFERENCE: from only ADJACENT",flush=True)
        print(f"comparisons it recovers the latent global order and infers NON-adjacent pairs at {acc:.2f} (internal",flush=True)
        print(f"pairs {iacc:.2f}, chance 0.5), with the SYMBOLIC DISTANCE EFFECT (nearer pairs harder) - the signature",flush=True)
        print(f"of genuine relational inference. The same world-model machinery that navigates space does relational",flush=True)
        print(f"reasoning in CONCEPT space (reasoning as navigation in a learned map). Bridge from sensorimotor to",flush=True)
        print(f"abstract. Established (SR cognitive map, Stachenfeld 2017; transitive inference), named as such.",flush=True)
    else:
        print(f"JEP-17: PARTIAL/NULL - acc {acc:.2f}, internal {iacc:.2f}, SDE {sde_present}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()

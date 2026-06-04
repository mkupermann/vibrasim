"""JEP-21b - low-dim structural prior generalizes sparse relational observations vs transitive closure."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
rng=np.random.default_rng(303)
N=60
truth=rng.uniform(0,1,(N,2))  # true 2D coords (continuous structure)
# all axis comparisons: for axis a, pairs (i,j) with i>j on that axis
def all_pairs():
    P=[]
    for i in range(N):
        for j in range(N):
            if i==j: continue
            for a in range(2):
                if abs(truth[i,a]-truth[j,a])>0.05: P.append((i,j,a,truth[i,a]>truth[j,a]))
    return P
ALL=all_pairs()
def fit_2d(obs,epochs=4000,lr=0.5,margin=0.1):
    Z=rng.normal(0,0.1,(N,2))
    obs=np.array([(i,j,a,1 if g else 0) for (i,j,a,g) in obs])
    for ep in range(epochs):
        # hinge: for (i,j,a,g=i>j): want Z[i,a]-Z[j,a] > margin (if g) else < -margin
        i=obs[:,0].astype(int); j=obs[:,1].astype(int); a=obs[:,2].astype(int); g=obs[:,3]
        d=Z[i,a]-Z[j,a]; sign=np.where(g==1,1.0,-1.0)
        viol=(margin - sign*d)>0
        grad=np.zeros_like(Z)
        gi=-sign*viol
        np.add.at(grad,(i,a),gi); np.add.at(grad,(j,a),-gi)
        Z-=lr*grad/len(obs)
    return Z
def transitive_closure_predict(obs,queries):
    # build per-axis reachability (i>j) then transitive closure; predict if derivable
    import numpy as np
    pred={}
    for a in range(2):
        gt=np.zeros((N,N),bool)
        for (i,j,aa,g) in obs:
            if aa!=a: continue
            if g: gt[i,j]=True
            else: gt[j,i]=True
        # Floyd-Warshall transitive closure
        reach=gt.copy()
        for k in range(N):
            reach |= (reach[:,k][:,None] & reach[k,:][None,:])
        pred[a]=reach
    correct=0;tot=0
    for (i,j,a,g) in queries:
        r=pred[a]
        if r[i,j]: p=True
        elif r[j,i]: p=False
        else: p=None
        tot+=1
        if p is None: correct+=0.5  # chance
        else: correct+=int(p==g)
    return correct/tot
def main():
    print(f"=== JEP-21b: low-dim structural prior vs transitive closure on sparse relations (N={N}) ===",flush=True)
    print(f"  total comparisons available: {len(ALL)}",flush=True)
    res={}
    for p in [0.05,0.10,0.20]:
        m=rng.random(len(ALL))<p; obs=[ALL[k] for k in range(len(ALL)) if m[k]]; unobs=[ALL[k] for k in range(len(ALL)) if not m[k]]
        Z=fit_2d(obs)
        # predict unobserved from fitted coords
        ok=0
        for (i,j,a,g) in unobs: ok+=int((Z[i,a]>Z[j,a])==g)
        acc_prior=ok/len(unobs)
        acc_tc=transitive_closure_predict(obs,unobs)
        res[p]=(acc_prior,acc_tc)
        print(f"  p={p:.2f} ({len(obs)} obs): 2D-prior acc on unobserved={acc_prior:.3f}   transitive-closure baseline={acc_tc:.3f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    ap,atc=res[0.10]
    if ap>=0.9 and ap>=atc+0.2:
        print(f"JEP-21b: PASS - a low-dim STRUCTURAL PRIOR generalizes sparse relational observations: fitting 2D",flush=True)
        print(f"coords to only {int(0.10*len(ALL))} observed comparisons (p=0.10) predicts UNOBSERVED pairs at",flush=True)
        print(f"{ap:.2f}, vs transitive-closure (no structural prior) {atc:.2f}. The structural prior genuinely",flush=True)
        print(f"REDUCES what must be observed - the useful core of structure-content factorization. Ordinal",flush=True)
        print(f"embedding / structural priors established - named as such. (Corrects JEP-21's weaker test.)",flush=True)
    else:
        print(f"JEP-21b: PARTIAL/NULL - p=0.10 prior {ap:.2f} vs transitive {atc:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()

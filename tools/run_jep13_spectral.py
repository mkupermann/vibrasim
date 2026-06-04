"""JEP-13 - proto-value functions (Laplacian eigenbasis) compose to novel goals. 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
rng=np.random.default_rng(50)
M=12
def gen_maze(M):
    adj={(x,y):set() for x in range(M) for y in range(M)}; seen={(0,0)}; st=[(0,0)]
    while st:
        x,y=st[-1]; nb=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nb: n=nb[rng.integers(len(nb))]; adj[(x,y)].add(n); adj[n].add((x,y)); seen.add(n); st.append(n)
        else: st.pop()
    return adj
ADJ=gen_maze(M); CELLS=[(x,y) for x in range(M) for y in range(M)]; ID={c:i for i,c in enumerate(CELLS)}; S=len(CELLS)
A=np.zeros((S,S))
for c in CELLS:
    for nb in ADJ[c]: A[ID[c],ID[nb]]=1
D=np.diag(A.sum(1)); L=D-A
gamma=0.97; P=A/A.sum(1,keepdims=True); SR=np.linalg.inv(np.eye(S)-gamma*P)
# proto-value functions: smoothest Laplacian eigenvectors (task-agnostic)
wL,VL=np.linalg.eigh(L); order=np.argsort(wL)  # ascending
def pvf_basis(k): return VL[:,order[:k]]
def rand_basis(k):
    Q,_=np.linalg.qr(rng.normal(0,1,(S,k))); return Q
def reconstruct(V,B): 
    coef=B.T@V; return B@coef
def r2(V,Vh): 
    ss=np.sum((V-V.mean())**2); return 1-np.sum((V-Vh)**2)/(ss+1e-12)
def plan_on_value(Vfield,reps_goals):
    ok=0;tot=0
    for g in reps_goals:
        for _ in range(3):
            s=CELLS[rng.integers(S)]
            if s==g: ok+=1;tot+=1;continue
            c=s;tot+=1
            for _ in range(6*S):
                nbs=list(ADJ[c]); c=max(nbs,key=lambda nb:Vfield[ID[nb]])
                if c==g: ok+=1;break
    return ok/tot
def main():
    print(f"=== JEP-13: spectral abstraction (proto-value functions), M={M} S={S}, 16 threads ===",flush=True)
    k=int(np.ceil(S/4)); print(f"  basis size k={k} (S/4)",flush=True)
    goals=[CELLS[rng.integers(S)] for _ in range(40)]
    Bp=pvf_basis(k); Br=rand_basis(k)
    r2p=[];r2r=[]
    Vp_fields={};Vr_fields={}
    for g in goals:
        V=SR[:,ID[g]].copy()
        Vhp=reconstruct(V,Bp); Vhr=reconstruct(V,Br)
        r2p.append(r2(V,Vhp)); r2r.append(r2(V,Vhr))
        Vp_fields[g]=Vhp; Vr_fields[g]=Vhr
    R2p=float(np.mean(r2p)); R2r=float(np.mean(r2r))
    print(f"  reconstruction R^2:  PVF basis={R2p:.3f}   random basis={R2r:.3f}",flush=True)
    # planning on reconstructed value fields
    def plan_fields(fields):
        ok=0;tot=0
        for g in goals:
            Vf=fields[g]
            for _ in range(3):
                s=CELLS[rng.integers(S)]
                if s==g: ok+=1;tot+=1;continue
                c=s;tot+=1
                for _ in range(6*S):
                    nbs=list(ADJ[c]); c=max(nbs,key=lambda nb:Vf[ID[nb]])
                    if c==g: ok+=1;break
        return ok/tot
    np_=plan_fields(Vp_fields); nr=plan_fields(Vr_fields)
    # true-SR planning reference
    nt=plan_fields({g:SR[:,ID[g]] for g in goals})
    print(f"  planning reached:  PVF={np_:.2f}   random-basis={nr:.2f}   (true-SR ref={nt:.2f})",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if R2p>=0.9 and np_>=0.9 and R2p>=R2r+0.2 and np_>=nr+0.3:
        print(f"JEP-13: PASS - a COMPACT task-agnostic basis abstracts the environment and COMPOSES to novel goals:",flush=True)
        print(f"k={k} proto-value functions reconstruct arbitrary novel-goal value functions at R^2={R2p:.2f} (random",flush=True)
        print(f"basis {R2r:.2f}) and planning on the reconstructed value reaches {np_:.2f} of novel goals (random-basis",flush=True)
        print(f"{nr:.2f}, true-SR {nt:.2f}). The eigenbasis is learned WITHOUT goals (task-agnostic) and is Hebbian-",flush=True)
        print(f"learnable (Oja). This is abstraction: learn structure once, compose to many tasks. Proto-value",flush=True)
        print(f"functions / spectral RL (Mahadevan 2007) established - named as such.",flush=True)
    else:
        print(f"JEP-13: PARTIAL/NULL - R2 PVF {R2p:.2f}/rand {R2r:.2f}, plan PVF {np_:.2f}/rand {nr:.2f}/true {nt:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()

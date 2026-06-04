"""JEP-9 - Successor Representation (closed-form + local TD) vs contrastive on a random maze. Multi-thread BLAS."""
import os
os.environ.setdefault("OMP_NUM_THREADS","16"); os.environ.setdefault("MKL_NUM_THREADS","16")
import numpy as np
from collections import deque
rng=np.random.default_rng(11)
M=12  # cells per side -> M*M states
def gen_maze(M):
    # DFS spanning tree; edges between adjacent cells
    adj={(x,y):set() for x in range(M) for y in range(M)}
    seen=set(); stack=[(0,0)]; seen.add((0,0))
    while stack:
        c=stack[-1]; x,y=c
        nbrs=[(x+dx,y+dy) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nbrs:
            n=nbrs[rng.integers(len(nbrs))]; adj[c].add(n); adj[n].add(c); seen.add(n); stack.append(n)
        else: stack.pop()
    return adj
ADJ=gen_maze(M)
CELLS=[(x,y) for x in range(M) for y in range(M)]; ID={c:i for i,c in enumerate(CELLS)}; S=len(CELLS)
def geodesic(src):
    d={src:0}; q=deque([src])
    while q:
        c=q.popleft()
        for nb in ADJ[c]:
            if nb not in d: d[nb]=d[c]+1; q.append(nb)
    return d
GEO={c:geodesic(c) for c in CELLS}
# transition matrix (random walk on carved edges)
P=np.zeros((S,S))
for c in CELLS:
    nbs=list(ADJ[c]); 
    for nb in nbs: P[ID[c],ID[nb]]=1/len(nbs)
gamma=0.95
def spearman(u,v):
    ru=np.argsort(np.argsort(u)); rv=np.argsort(np.argsort(v)); return float(np.corrcoef(ru,rv)[0,1])

def sr_closed(): return np.linalg.inv(np.eye(S)-gamma*P)
def sr_td(steps=2_000_000,alpha=0.02):
    Mt=np.zeros((S,S)); c=CELLS[rng.integers(S)]
    I=np.eye(S)
    for _ in range(steps):
        nbs=list(ADJ[c]); nb=nbs[rng.integers(len(nbs))]
        i,j=ID[c],ID[nb]
        Mt[i]+=alpha*(I[i]+gamma*Mt[j]-Mt[i])
        c=nb
    return Mt
def emb_from(Mx,k=8):
    # symmetric-ize and SVD -> low-dim diffusion-like embedding
    A=0.5*(Mx+Mx.T); U,s,_=np.linalg.svd(A); return U[:,:k]*s[:k]
def contrastive_emb(steps=600000,Du=24,eta=0.05,margin=1.0):
    E={c:rng.normal(0,0.3,Du) for c in CELLS}; c=CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs=list(ADJ[c]); nb=nbs[rng.integers(len(nbs))]
        d=E[nb]-E[c]; E[c]+=eta*d; E[nb]-=eta*d
        p,q=CELLS[rng.integers(S)],CELLS[rng.integers(S)]
        if p!=q:
            diff=E[p]-E[q]; dist=np.linalg.norm(diff)+1e-9
            if dist<margin: push=eta*(margin-dist)*diff/dist; E[p]+=push; E[q]-=push
        c=nb
    return np.array([E[c] for c in CELLS])

def corr_to_geo(emb):
    pairs=[(CELLS[rng.integers(S)],CELLS[rng.integers(S)]) for _ in range(4000)]; pairs=[(a,b) for a,b in pairs if a!=b]
    ed=np.array([np.linalg.norm(emb[ID[a]]-emb[ID[b]]) for a,b in pairs])
    gd=np.array([GEO[a][b] for a,b in pairs]); eu=np.array([abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in pairs])
    return spearman(ed,gd),spearman(ed,eu)
def navigate(emb,reps=120):
    ok=0
    for _ in range(reps):
        s=CELLS[rng.integers(S)]; g=CELLS[rng.integers(S)]
        if s==g: ok+=1; continue
        c=s; seen=set()
        for _ in range(6*S):
            nbs=list(ADJ[c]); bc=min(nbs,key=lambda nb:np.linalg.norm(emb[ID[nb]]-emb[ID[g]]))
            c=bc
            if c==g: ok+=1; break
            if c in seen: break
            seen.add(c)
    return ok/reps
EUC=np.array([[c[0]/M,c[1]/M] for c in CELLS])
def main():
    print(f"=== JEP-9: Successor Representation on a random maze (M={M}, S={S} states, 16 threads) ===",flush=True)
    Mc=sr_closed(); print("  closed-form SR done",flush=True)
    Mt=sr_td(); td_corr=spearman(Mc.flatten(),Mt.flatten()); print(f"  TD-learned SR vs closed-form: corr={td_corr:.2f}",flush=True)
    e_sr=emb_from(Mc); e_srtd=emb_from(Mt); e_con=contrastive_emb()
    g_sr,u_sr=corr_to_geo(e_sr); g_con,u_con=corr_to_geo(e_con); g_eu,u_eu=corr_to_geo(EUC)
    print(f"  Spearman geodesic/euclid:  SR={g_sr:.2f}/{u_sr:.2f}   contrastive={g_con:.2f}/{u_con:.2f}   euclid-emb={g_eu:.2f}/{u_eu:.2f}",flush=True)
    n_sr=navigate(e_sr); n_srtd=navigate(e_srtd); n_con=navigate(e_con); n_eu=navigate(EUC)
    rok=0
    for _ in range(120):
        s=CELLS[rng.integers(S)]; g=CELLS[rng.integers(S)]
        if s==g: rok+=1; continue
        c=s
        for _ in range(6*S):
            nbs=list(ADJ[c]); c=nbs[rng.integers(len(nbs))]
            if c==g: rok+=1; break
    n_rand=rok/120
    print(f"  navigate reached:  SR={n_sr:.2f}  SR-TD={n_srtd:.2f}  contrastive={n_con:.2f}  euclid={n_eu:.2f}  random={n_rand:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    ok1=g_sr>=0.7 and g_sr>=u_sr+0.15
    ok2=n_sr>=0.7 and n_sr>=n_eu+0.2 and n_sr>=n_rand+0.2
    ok3=g_sr>g_con and n_sr>n_con
    ok4=td_corr>=0.9
    if ok1 and ok2 and ok3 and ok4:
        print(f"JEP-9: PASS - the Successor Representation captures GEODESIC structure (Spearman {g_sr:.2f} geodesic vs",flush=True)
        print(f"{u_sr:.2f} euclid) and navigates the maze at {n_sr:.2f} (euclid control {n_eu:.2f}, random {n_rand:.2f}),",flush=True)
        print(f"BEATING the contrastive rule (geo {g_con:.2f}, nav {n_con:.2f}) that failed in JEP-8. TD-learned SR",flush=True)
        print(f"matches closed-form (corr {td_corr:.2f}) - so a LOCAL TD rule (substrate-compatible) suffices. SR",flush=True)
        print(f"(Dayan 1993) + diffusion-map embedding = established methods, named as such. Fixes JEP-8's limit.",flush=True)
    else:
        print(f"JEP-9: PARTIAL/NULL - ok1={ok1} ok2={ok2} ok3={ok3} ok4={ok4} (SR geo {g_sr:.2f}, nav {n_sr:.2f}, con geo {g_con:.2f}/nav {n_con:.2f}, td {td_corr:.2f})",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()

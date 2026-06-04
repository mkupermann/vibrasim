"""JEP-8 - locally-learned encoder captures geodesic maze structure (vs Euclidean), enables maze MPC."""
import numpy as np
from collections import deque
rng=np.random.default_rng(8)
N=8; Du=20
# wall barrier: column x=4 blocked except a gap at y=6
WALLS={(4,y) for y in range(0,6)}
FREE=[(x,y) for x in range(N) for y in range(N) if (x,y) not in WALLS]
FSET=set(FREE)
DIRS={0:(1,0),1:(-1,0),2:(0,1),3:(0,-1)}
def step(x,y,a):
    dx,dy=DIRS[a]; nx,ny=x+dx,y+dy
    if 0<=nx<N and 0<=ny<N and (nx,ny) in FSET: return nx,ny
    return x,y
def geodesic(src):
    d={src:0}; q=deque([src])
    while q:
        c=q.popleft()
        for a in range(4):
            nb=step(*c,a)
            if nb not in d and nb!=c: d[nb]=d[c]+1; q.append(nb)
    return d
GEO={s:geodesic(s) for s in FREE}

def learn_encoder(steps=60000,eta=0.05,margin=1.0):
    E={k:rng.normal(0,0.3,Du) for k in FREE}
    c=FREE[rng.integers(len(FREE))]
    for _ in range(steps):
        a=rng.integers(0,4); nb=step(*c,a)
        if nb!=c:
            d=E[nb]-E[c]; E[c]+=eta*d; E[nb]-=eta*d
        p,q=FREE[rng.integers(len(FREE))],FREE[rng.integers(len(FREE))]
        if p!=q:
            diff=E[p]-E[q]; dist=np.linalg.norm(diff)+1e-9
            if dist<margin:
                push=eta*(margin-dist)*diff/dist; E[p]+=push; E[q]-=push
        c=nb
    M=np.mean([E[k] for k in FREE],0)
    for k in FREE: E[k]=E[k]-M
    return E

def spearman(u,v):
    ru=np.argsort(np.argsort(u)); rv=np.argsort(np.argsort(v)); return float(np.corrcoef(ru,rv)[0,1])

def main():
    print("=== JEP-8: maze - geodesic vs Euclidean structure in the learned encoder ===",flush=True)
    print(f"  free cells={len(FREE)}, wall barrier col x=4 (gap at y=6,7)",flush=True)
    E=learn_encoder()
    Eu={k:np.array([k[0]/N,k[1]/N]) for k in FREE}  # Euclidean-coords encoder (knows position, not walls)
    pairs=[(FREE[rng.integers(len(FREE))],FREE[rng.integers(len(FREE))]) for _ in range(3000)]
    pairs=[(a,b) for a,b in pairs if a!=b and b in GEO[a]]
    gd=np.array([GEO[a][b] for a,b in pairs])
    ed=np.array([np.linalg.norm(E[a]-E[b]) for a,b in pairs])
    eu=np.array([abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in pairs])
    sp_geo=spearman(ed,gd); sp_euc=spearman(ed,eu)
    print(f"  Spearman(emb-dist, GEODESIC)  = {sp_geo:.2f}",flush=True)
    print(f"  Spearman(emb-dist, EUCLIDEAN) = {sp_euc:.2f}",flush=True)
    def mpc(emb,reps=80):
        ok=0
        for _ in range(reps):
            s=FREE[rng.integers(len(FREE))]; g=FREE[rng.integers(len(FREE))]
            if s==g: ok+=1; continue
            x,y=s; seen=set()
            for _ in range(4*N):
                ba=min(range(4),key=lambda a:np.linalg.norm(emb[step(x,y,a)]-emb[g]))
                x,y=step(x,y,ba)
                if (x,y)==g: ok+=1; break
                if (x,y) in seen: break   # stuck in a loop/local min
                seen.add((x,y))
        return ok/reps
    r_learn=mpc(E); r_euc=mpc(Eu)
    rok=0
    for _ in range(80):
        s=FREE[rng.integers(len(FREE))]; g=FREE[rng.integers(len(FREE))]
        if s==g: rok+=1; continue
        x,y=s
        for _ in range(4*N):
            x,y=step(x,y,rng.integers(4))
            if (x,y)==g: rok+=1; break
    r_rand=rok/80
    print(f"  energy-MPC reached (LEARNED encoder)   = {r_learn:.2f}",flush=True)
    print(f"  energy-MPC reached (EUCLIDEAN control)  = {r_euc:.2f}",flush=True)
    print(f"  random-action baseline                  = {r_rand:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    ok1 = sp_geo>=0.7 and sp_geo>=sp_euc+0.15
    ok2 = r_learn>=0.7 and r_learn>=r_euc+0.2 and r_learn>=r_rand+0.2
    if ok1 and ok2:
        print(f"JEP-8: PASS - the LOCAL contrastive rule learned GEODESIC structure: emb-dist tracks shortest-path",flush=True)
        print(f"distance (Spearman {sp_geo:.2f}) better than Euclidean ({sp_euc:.2f}), and energy-MPC navigates the",flush=True)
        print(f"maze at {r_learn:.2f} vs a Euclidean-coords encoder {r_euc:.2f} (gets stuck at the wall) and random",flush=True)
        print(f"{r_rand:.2f}. The learned representation captures the task's CONNECTIVITY, not just position - which",flush=True)
        print(f"is what lets it plan around walls. Strengthens JEP-7: the encoder does real topological work.",flush=True)
        print(f"Contrastive/slow-feature learning = established, named as such.",flush=True)
    else:
        print(f"JEP-8: PARTIAL/NULL - geo {sp_geo:.2f}/euc {sp_euc:.2f} (ok1={ok1}); learned {r_learn:.2f}/euclid {r_euc:.2f}/rand {r_rand:.2f} (ok2={ok2})",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()

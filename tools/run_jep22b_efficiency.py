"""JEP-22b - EFFICIENCY of SR-value policy under noise: steps/optimal, vs random walk. 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
from collections import deque
rng=np.random.default_rng(221)
M=12
def gen_looped(M,extra=40):
    adj={(x,y):set() for x in range(M) for y in range(M)}; seen={(0,0)}; st=[(0,0)]
    while st:
        x,y=st[-1]; nb=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nb: n=nb[rng.integers(len(nb))]; adj[(x,y)].add(n); adj[n].add((x,y)); seen.add(n); st.append(n)
        else: st.pop()
    cells=[(x,y) for x in range(M) for y in range(M)]; added=0
    while added<extra:
        c=cells[rng.integers(len(cells))]; x,y=c
        opts=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in adj[c]]
        if opts: n=opts[rng.integers(len(opts))]; adj[c].add(n); adj[n].add(c); added+=1
    return adj
ADJ=gen_looped(M); CELLS=[(x,y) for x in range(M) for y in range(M)]; ID={c:i for i,c in enumerate(CELLS)}; S=len(CELLS)
gamma=0.97
def bfs(src):
    d={src:0}; q=deque([src])
    while q:
        c=q.popleft()
        for nb in ADJ[c]:
            if nb not in d: d[nb]=d[c]+1; q.append(nb)
    return d
GEO={c:bfs(c) for c in CELLS}
def sr_td(steps=3_000_000,alpha=0.02):
    Mt=np.zeros((S,S),np.float32); I=np.eye(S,dtype=np.float32); c=CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs=list(ADJ[c]); nb=nbs[rng.integers(len(nbs))]; Mt[ID[c]]+=alpha*(I[ID[c]]+gamma*Mt[ID[nb]]-Mt[ID[c]]); c=nb
    return Mt
Mt=sr_td()
def slip(c,intended,eps):
    nbs=list(ADJ[c])
    return nbs[rng.integers(len(nbs))] if rng.random()<eps else intended
def run(policy,eps,reps=300):
    ratios=[]
    for _ in range(reps):
        s=CELLS[rng.integers(S)]; g=CELLS[rng.integers(S)]
        opt=GEO[s].get(g,0)
        if opt==0: continue
        c=s; steps=0
        for _ in range(20*S):
            steps+=1
            if policy=="sr":
                nbs=list(ADJ[c]); intended=max(nbs,key=lambda nb:Mt[ID[nb],ID[g]])
            else:
                nbs=list(ADJ[c]); intended=nbs[rng.integers(len(nbs))]
            c=slip(c,intended,eps)
            if c==g: break
        ratios.append(steps/opt)
    return float(np.mean(ratios))
def main():
    print(f"=== JEP-22b: efficiency (steps/optimal) under noise, SR-policy vs random (S={S}) ===",flush=True)
    print("   eps    SR steps/opt   random steps/opt",flush=True)
    rows=[]
    for eps in [0.0,0.1,0.2,0.3,0.5]:
        sr=run("sr",eps); rd=run("rand",eps); rows.append((eps,sr,rd))
        print(f"   {eps:.1f}     {sr:6.2f}        {rd:6.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    d={e:(s,r) for e,s,r in rows}
    ok = d[0.0][0]<=1.3 and d[0.2][0]<=2.5 and all(d[e][0] < d[e][1]*0.6 for e,_,_ in rows)
    if ok:
        print(f"JEP-22b: PASS - the SR-value policy is genuinely DIRECTING under noise (not budget-reliant):",flush=True)
        print(f"near-optimal when deterministic ({d[0.0][0]:.2f}x optimal) and efficient under noise ({d[0.2][0]:.2f}x",flush=True)
        print(f"at 20% slip), FAR better than random walk at every level (e.g. eps=0.2: SR {d[0.2][0]:.1f}x vs random",flush=True)
        print(f"{d[0.2][1]:.1f}x). Efficiency degrades GRACEFULLY with noise - the real, honest robustness story",flush=True)
        print(f"(JEP-22's reach=1.0 was budget-saturated). SR + closed-loop control established - named as such.",flush=True)
    else:
        print(f"JEP-22b: PARTIAL/NULL - {rows}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()

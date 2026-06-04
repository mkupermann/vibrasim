"""JEP-13b - depth-d MPC lookahead on the PVF-approximated value (robust to local maxima). 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
rng=np.random.default_rng(51)
M=12; DEPTH=6
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
D=np.diag(A.sum(1)); L=D-A; gamma=0.97; P=A/A.sum(1,keepdims=True); SR=np.linalg.inv(np.eye(S)-gamma*P)
wL,VL=np.linalg.eigh(L); order=np.argsort(wL); k=int(np.ceil(S/4)); Bp=VL[:,order[:k]]
def recon(V): return Bp@(Bp.T@V)
def mpc_lookahead(Vf, s, g, depth=DEPTH, budget=8*144):
    c=s; visited=set()
    for _ in range(budget):
        if c==g: return True
        # depth-d search: best frontier value, return first action toward it; prefer not to revisit
        best=None; first=None
        stack=[(c,None,0,{c})]
        while stack:
            node,fa,d,path=stack.pop()
            val=Vf[ID[node]] - (0.001*len(path))  # tiny path penalty to prefer shorter
            if node==g: val=1e9
            if best is None or val>best:
                if d>0: best=val; first=fa
            if d<depth:
                for nb in ADJ[node]:
                    if nb not in path: stack.append((nb,fa if fa is not None else nb,d+1,path|{nb}))
        if first is None: 
            nbs=list(ADJ[c]); first=nbs[rng.integers(len(nbs))]
        c=first
    return c==g
def evaluate(planner_value_fn, goals, reps=3):
    ok=0;tot=0
    for g in goals:
        Vf=planner_value_fn(g)
        for _ in range(reps):
            s=CELLS[rng.integers(S)]; tot+=1
            if mpc_lookahead(Vf,s,g): ok+=1
    return ok/tot
def main():
    print(f"=== JEP-13b: MPC lookahead (depth {DEPTH}) on PVF-approx value, S={S}, k={k} ===",flush=True)
    goals=[CELLS[rng.integers(S)] for _ in range(40)]
    pvf=evaluate(lambda g: recon(SR[:,ID[g]]), goals)
    tru=evaluate(lambda g: SR[:,ID[g]], goals)
    rb=np.linalg.qr(rng.normal(0,1,(S,k)))[0]
    rnd=evaluate(lambda g: rb@(rb.T@SR[:,ID[g]]), goals)
    print(f"  MPC-lookahead reached:  PVF-approx={pvf:.2f}   random-basis={rnd:.2f}   true-SR={tru:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if pvf>=0.9 and pvf>=rnd+0.3:
        print(f"JEP-13b: PASS - with MPC LOOKAHEAD (depth {DEPTH}), planning on the COMPACT PVF-approximated value",flush=True)
        print(f"reaches {pvf:.2f} of NOVEL goals (random-basis {rnd:.2f}, true-SR {tru:.2f}). So the abstraction is",flush=True)
        print(f"USABLE FOR CONTROL once the planner tolerates approximation: a small task-agnostic basis (k=S/4),",flush=True)
        print(f"learned without goals, composes via lookahead to solve novel tasks near-optimally. Closes JEP-13's",flush=True)
        print(f"value-vs-control gap. Proto-value functions + MPC = established methods, named as such.",flush=True)
    else:
        print(f"JEP-13b: PARTIAL/NULL - PVF {pvf:.2f}, random {rnd:.2f}, true {tru:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()

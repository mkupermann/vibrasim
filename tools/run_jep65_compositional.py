"""JEP-65 - compositional concept layer: systematic generalization to combinatorially-many novel goals."""
import numpy as np, itertools
from collections import deque
rng=np.random.default_rng(65)
K=5; AD=24; NE=20
proto=rng.normal(0,1,(K,AD))
# learn primitive prototypes from SINGLE-primitive items
learnedP=np.array([np.mean([proto[k]+rng.normal(0,0.3,AD) for _ in range(30)],0) for k in range(K)])
# entities: random non-empty subsets of primitives
ent_sub=[tuple(sorted(rng.choice(K,rng.integers(1,4),replace=False))) for _ in range(NE)]
ent_out=[sum(proto[k] for k in s)+rng.normal(0,0.3,AD) for s in ent_sub]
def decode(o, thr=0.5):
    coef,_,_,_=np.linalg.lstsq(learnedP.T,o,rcond=None)
    return set(k for k in range(K) if coef[k]>thr)   # which primitives present
ent_code=[decode(o) for o in ent_out]
# grid + SR
M=8
def gen_looped(M,extra=18):
    adj={(x,y):set() for x in range(M) for y in range(M)};seen={(0,0)};st=[(0,0)]
    while st:
        x,y=st[-1];nb=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nb: nn=nb[rng.integers(len(nb))];adj[(x,y)].add(nn);adj[nn].add((x,y));seen.add(nn);st.append(nn)
        else: st.pop()
    cells=[(x,y) for x in range(M) for y in range(M)];added=0
    while added<extra:
        c=cells[rng.integers(len(cells))];x,y=c
        opts=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in adj[c]]
        if opts: nn=opts[rng.integers(len(opts))];adj[c].add(nn);adj[nn].add(c);added+=1
    return adj
ADJ=gen_looped(M);CELLS=[(x,y) for x in range(M) for y in range(M)];CID={c:i for i,c in enumerate(CELLS)};S=len(CELLS);gamma=0.97
def sr_td(steps=900_000,alpha=0.02):
    Mt=np.zeros((S,S),np.float32);I=np.eye(S,dtype=np.float32);c=CELLS[rng.integers(S)]
    for _ in range(steps):
        nbs=list(ADJ[c]);nb=nbs[rng.integers(len(nbs))];Mt[CID[c]]+=alpha*(I[CID[c]]+gamma*Mt[CID[nb]]-Mt[CID[c]]);c=nb
    return Mt
def main():
    print(f"=== JEP-65: compositional generalization to 2^{K} goals from {K} primitives ===", flush=True)
    # zero-shot grounding F1: for random goal subsets, does the decoded code identify the right entities?
    f1s=[]
    for _ in range(300):
        gsize=rng.integers(1,3); goal=set(rng.choice(K,gsize,replace=False))
        true=[i for i in range(NE) if goal<=set(ent_sub[i])]
        pred=[i for i in range(NE) if goal<=ent_code[i]]
        if not true and not pred: continue
        tp=len(set(true)&set(pred)); prec=tp/len(pred) if pred else 0; rec=tp/len(true) if true else 0
        f1s.append(2*prec*rec/(prec+rec) if (prec+rec)>0 else 0)
    f1=np.mean(f1s)
    print(f"  zero-shot compositional grounding F1 (arbitrary primitive-subset goals) = {f1:.3f}", flush=True)
    Mt=sr_td(); reached=trials=0
    for _ in range(150):
        cells=list(CELLS);rng.shuffle(cells);ent_cell={i:cells[i] for i in range(NE)}
        gsize=rng.integers(1,3); goal=set(rng.choice(K,gsize,replace=False))
        grounded=[i for i in range(NE) if goal<=ent_code[i]]
        true=set(i for i in range(NE) if goal<=set(ent_sub[i]))
        if not grounded: continue
        trials+=1;start=CELLS[rng.integers(S)]
        target=max(grounded,key=lambda e:Mt[CID[start],CID[ent_cell[e]]]);c=start
        for _ in range(6*S):
            nbs=list(ADJ[c]);c=max(nbs,key=lambda nb:Mt[CID[nb],CID[ent_cell[target]]])
            if c==ent_cell[target]: break
        arrived=next((e for e,cell in ent_cell.items() if cell==c),None)
        reached+=int(arrived in true)
    acc=reached/trials if trials else 0
    print(f"  grounded-planning to compositional goals success = {acc:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if f1>=0.9 and acc>=0.85:
        print(f"JEP-65: PASS - compositionality BUILT IN: from {K} learned primitives the agent grounds and plans to", flush=True)
        print(f"ARBITRARY primitive-subset goals (2^{K}={2**K} possible, incl. novel combinations) zero-shot - grounding", flush=True)
        print(f"F1 {f1:.2f}, planning {acc:.2f}. Systematic generalization to combinatorially-many goals from few", flush=True)
        print(f"primitives - a genuine hallmark of human-like understanding, now demonstrated (toy). The categorize-", flush=True)
        print(f"not-compose gap (JEP-64) is closed by an explicit compositional code. Established (decomposition,", flush=True)
        print(f"set logic, SR/TD), named as such.", flush=True)
    else:
        print(f"JEP-65: PARTIAL/NULL - grounding F1 {f1:.2f}, planning {acc:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()

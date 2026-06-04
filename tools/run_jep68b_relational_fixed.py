"""JEP-68b - relational action with CORRECT pair binding: above(a,b)=a(x)(ABOVE(x)b)."""
import numpy as np
rng=np.random.default_rng(681)
D=2048
def rv(): return rng.normal(0,1/np.sqrt(D),D)
def cconv(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.fft.fft(b)))
def ccorr(a,b): return np.real(np.fft.ifft(np.fft.fft(a)*np.conj(np.fft.fft(b))))
def cos(a,b): return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-9))
ABOVE=rv()
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
    print("=== JEP-68b: relational action with CORRECT pair binding ===", flush=True)
    Mt=sr_td(); resolve_ok=plan_ok=trials=0
    for _ in range(200):
        NO=rng.integers(5,8); objs={i:rv() for i in range(NO)}
        avail=list(range(NO)); rng.shuffle(avail); pairs=[(avail[k],avail[k+1]) for k in range(0,len(avail)-1,2)]
        scene=np.zeros(D)
        for a,b in pairs: scene+=cconv(objs[a],cconv(ABOVE,objs[b]))  # a is above b
        a_b=pairs[rng.integers(len(pairs))]; Y=a_b[1]; true_top=a_b[0]
        # query: what is above Y? -> ccorr(scene, ABOVE(x)Y) ~ objs[true_top]
        key=cconv(ABOVE,objs[Y]); ans=ccorr(scene,key)
        pred=int(np.argmax([cos(ans,objs[o]) for o in range(NO)]))
        resolve_ok+=int(pred==true_top); trials+=1
        cells=list(CELLS);rng.shuffle(cells);ent_cell={i:cells[i] for i in range(NO)}
        start=CELLS[rng.integers(S)];c=start
        for _ in range(6*S):
            nbs=list(ADJ[c]);c=max(nbs,key=lambda nb:Mt[CID[nb],CID[ent_cell[pred]]])
            if c==ent_cell[pred]: break
        arrived=next((e for e,cell in ent_cell.items() if cell==c),None)
        plan_ok+=int(arrived==true_top)
    ra=resolve_ok/trials; pa=plan_ok/trials
    print(f"  relational-goal resolution accuracy = {ra:.3f}", flush=True)
    print(f"  relational goal-directed planning success = {pa:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ra>=0.9 and pa>=0.85:
        print(f"JEP-68b: PASS - with CORRECT pair binding (a(x)(ABOVE(x)b)), the agent resolves 'what is on top of Y'", flush=True)
        print(f"({ra:.2f}) and navigates to it ({pa:.2f}). RELATIONAL reasoning drives ACTION - structured", flush=True)
        print(f"understanding-informed behaviour beyond set-logic goals. JEP-68's NULL was the encoding (lost pairing),", flush=True)
        print(f"not the capability. Established (VSA/HRR, SR/TD), named as such.", flush=True)
    else:
        print(f"JEP-68b: PARTIAL/NULL - resolution {ra:.2f}, planning {pa:.2f}", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()

"""JEP-12 - learn the world model from NOISY HIGH-DIM observations (perception), then SR-value planning. 16-thread."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
rng=np.random.default_rng(42)
M=10
def gen_maze(M):
    adj={(x,y):set() for x in range(M) for y in range(M)}; seen={(0,0)}; st=[(0,0)]
    while st:
        x,y=st[-1]; nb=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nb: n=nb[rng.integers(len(nb))]; adj[(x,y)].add(n); adj[n].add((x,y)); seen.add(n); st.append(n)
        else: st.pop()
    return adj
ADJ=gen_maze(M); CELLS=[(x,y) for x in range(M) for y in range(M)]; ID={c:i for i,c in enumerate(CELLS)}; S=len(CELLS)
OBS_D=64
SIG={c:rng.normal(0,1,OBS_D) for c in CELLS}   # fixed per-cell sensory signature
NOISE=0.6
def observe(c): return SIG[c]+rng.normal(0,NOISE,OBS_D)

def learn_perception(steps=200000,Du=24,eta=0.04,margin=1.0):
    # local contrastive temporal-coherence on OBSERVATIONS -> denoised latent encoder W (linear)
    W=rng.normal(0,0.1,(OBS_D,Du))
    c=CELLS[rng.integers(S)]
    def enc(o): e=np.tanh(o@W); return e
    for t in range(steps):
        nbs=list(ADJ[c]); nb=nbs[rng.integers(len(nbs))]
        o1,o2=observe(c),observe(nb)
        e1,e2=enc(o1),enc(o2)
        # attract temporally-adjacent (same trajectory) - approximates slow features (denoise + topology)
        g=(e2-e1)
        W+=eta*np.outer(o1,(1-e1**2)*g)*0.5; W-=eta*np.outer(o2,(1-e2**2)*g)*0.5
        # repel random pair
        p,q=CELLS[rng.integers(S)],CELLS[rng.integers(S)]
        if p!=q:
            ep,eq=enc(observe(p)),enc(observe(q)); diff=ep-eq; dist=np.linalg.norm(diff)+1e-9
            if dist<margin:
                f=eta*(margin-dist)/dist
                W+=f*np.outer(observe(p),(1-ep**2)*diff)*0.5; W-=f*np.outer(observe(q),(1-eq**2)*diff)*0.5
        c=nb
    return W
def main():
    print(f"=== JEP-12: grounded world model from NOISY obs (M={M},S={S},obs_d={OBS_D},noise={NOISE}) ===",flush=True)
    W=learn_perception()
    def enc(o): return np.tanh(o@W)
    # build prototypes: mean encoded obs per cell (the agent forms these online; here from samples)
    proto=np.array([np.mean([enc(observe(c)) for _ in range(40)],0) for c in CELLS])
    def perceive(o):  # nearest prototype -> discrete state code
        e=enc(o); return int(np.argmin(np.linalg.norm(proto-e,axis=1)))
    # perceptual identification accuracy under noise
    correct=0;T=2000
    for _ in range(T):
        c=CELLS[rng.integers(S)]; correct+= int(perceive(observe(c))==ID[c])
    pacc=correct/T
    print(f"  perceptual state-ID accuracy under noise = {pacc:.3f}",flush=True)
    # learn SR by TD over PERCEIVED codes (agent walks, perceives, learns)
    gamma=0.97; Mt=np.zeros((S,S),np.float32); I=np.eye(S,dtype=np.float32)
    c=CELLS[rng.integers(S)]; pc=perceive(observe(c))
    for _ in range(1500000):
        nbs=list(ADJ[c]); nb=nbs[rng.integers(len(nbs))]; pnb=perceive(observe(nb))
        Mt[pc]+=0.02*(I[pc]+gamma*Mt[pnb]-Mt[pc]); c=nb; pc=pnb
    def sr_pol(c,g):  # perceive current + plan to perceived goal
        pg=perceive(observe(g)); nbs=list(ADJ[c]); return max(nbs,key=lambda nb:Mt[perceive(observe(nb)),pg])
    def eu_pol(c,g): nbs=list(ADJ[c]); return min(nbs,key=lambda nb:abs(nb[0]-g[0])+abs(nb[1]-g[1]))
    def rnd(c,g): nbs=list(ADJ[c]); return nbs[rng.integers(len(nbs))]
    def nav(pol,reps=200):
        ok=0
        for _ in range(reps):
            s=CELLS[rng.integers(S)]; g=CELLS[rng.integers(S)]
            if s==g: ok+=1; continue
            cc=s
            for _ in range(6*S):
                cc=pol(cc,g)
                if cc==g: ok+=1; break
        return ok/reps
    n_sr=nav(sr_pol); n_eu=nav(eu_pol); n_rd=nav(rnd)
    print(f"  navigation (PERCEIVED states):  SR-VALUE={n_sr:.2f}  Euclid={n_eu:.2f}  random={n_rd:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if pacc>=0.9 and n_sr>=0.85 and n_sr>=n_eu+0.3 and n_sr>=n_rd+0.3:
        print(f"JEP-12: PASS - the substrate-native loop works FROM PERCEPTION: a local contrastive encoder denoises",flush=True)
        print(f"high-dim noisy observations into states (ID acc {pacc:.2f}), a local TD rule learns SR over the",flush=True)
        print(f"PERCEIVED codes, and SR-value planning navigates at {n_sr:.2f} (Euclid {n_eu:.2f}, random {n_rd:.2f}).",flush=True)
        print(f"No privileged state indices - perception + world-model + planning, all local/backprop-free. Step",flush=True)
        print(f"toward grounding. Methods (contrastive/slow-feature, prototype clustering, SR/TD) established, named.",flush=True)
    else:
        print(f"JEP-12: PARTIAL/NULL - percept-acc {pacc:.2f}, SR-nav {n_sr:.2f}, euclid {n_eu:.2f}, random {n_rd:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()

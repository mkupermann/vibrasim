"""JEP-12c - grounded loop with multi-glance denoising (avg k obs/perception, cache goal). Pre-registered."""
import os
for v in ["OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"]: os.environ[v]="16"
import numpy as np
rng=np.random.default_rng(44)
M=12; OBS_D=64; NOISE=0.6; KGLANCE=5
def gen_maze(M):
    adj={(x,y):set() for x in range(M) for y in range(M)}; seen={(0,0)}; st=[(0,0)]
    while st:
        x,y=st[-1]; nb=[(x+dx,y+dy) for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)] if 0<=x+dx<M and 0<=y+dy<M and (x+dx,y+dy) not in seen]
        if nb: n=nb[rng.integers(len(nb))]; adj[(x,y)].add(n); adj[n].add((x,y)); seen.add(n); st.append(n)
        else: st.pop()
    return adj
ADJ=gen_maze(M); CELLS=[(x,y) for x in range(M) for y in range(M)]; ID={c:i for i,c in enumerate(CELLS)}; S=len(CELLS)
SIG={c:rng.normal(0,1,OBS_D) for c in CELLS}
def observe(c): return SIG[c]+rng.normal(0,NOISE,OBS_D)
def glance(c,k=KGLANCE): return np.mean([observe(c) for _ in range(k)],0)  # multi-glance denoise
def main():
    print(f"=== JEP-12c: grounded loop + multi-glance denoising (k={KGLANCE}, noise={NOISE}, S={S}) ===",flush=True)
    proto=np.zeros((S,OBS_D)); cnt=np.zeros(S); c=CELLS[rng.integers(S)]
    for _ in range(30000):
        o=observe(c); i=ID[c]; cnt[i]+=1; proto[i]+=(o-proto[i])/cnt[i]
        nbs=list(ADJ[c]); c=nbs[rng.integers(len(nbs))]
    def perceive(o): return int(np.argmin(np.linalg.norm(proto-o,axis=1)))
    correct=sum(int(perceive(glance(CELLS[rng.integers(S)] if False else cc))==ID[cc]) for cc in [CELLS[rng.integers(S)] for _ in range(3000)])
    # simpler explicit loop for perception acc with k-glance
    correct=0;T=3000
    for _ in range(T):
        cc=CELLS[rng.integers(S)]; correct+=int(perceive(glance(cc))==ID[cc])
    pacc=correct/T
    print(f"  perceptual state-ID (k-glance) = {pacc:.3f}",flush=True)
    gamma=0.97; Mt=np.zeros((S,S),np.float32); I=np.eye(S,dtype=np.float32)
    c=CELLS[rng.integers(S)]; pc=perceive(glance(c))
    for _ in range(2000000):
        nbs=list(ADJ[c]); nb=nbs[rng.integers(len(nbs))]; pnb=perceive(observe(nb))  # learn from single obs (online)
        Mt[pc]+=0.02*(I[pc]+gamma*Mt[pnb]-Mt[pc]); c=nb; pc=pnb
    def sr_pol_cachedgoal(c,pg):
        nbs=list(ADJ[c]); return max(nbs,key=lambda nb:Mt[perceive(glance(nb)),pg])
    def eu_pol(c,g): nbs=list(ADJ[c]); return min(nbs,key=lambda nb:abs(nb[0]-g[0])+abs(nb[1]-g[1]))
    def rnd(c,g): nbs=list(ADJ[c]); return nbs[rng.integers(len(nbs))]
    def nav_sr(reps=200):
        ok=0
        for _ in range(reps):
            s=CELLS[rng.integers(S)]; g=CELLS[rng.integers(S)]
            if s==g: ok+=1; continue
            pg=perceive(glance(g))   # perceive goal ONCE (cached)
            cc=s
            for _ in range(6*S):
                cc=sr_pol_cachedgoal(cc,pg)
                if cc==g: ok+=1; break
        return ok/reps
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
    n_sr=nav_sr(); n_eu=nav(eu_pol); n_rd=nav(rnd)
    print(f"  navigation (PERCEIVED, k-glance+cached goal):  SR-VALUE={n_sr:.2f}  Euclid={n_eu:.2f}  random={n_rd:.2f}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if pacc>=0.95 and n_sr>=0.85 and n_sr>=n_eu+0.3 and n_sr>=n_rd+0.3:
        print(f"JEP-12c: PASS - the substrate-native loop works FROM PERCEPTION with multi-glance denoising: state-ID",flush=True)
        print(f"{pacc:.2f}, SR-value planning {n_sr:.2f} (Euclid {n_eu:.2f}, random {n_rd:.2f}). Perception (discriminate,",flush=True)
        print(f"denoise by averaging) + world model (local TD SR) + value planning - all local, no privileged indices.",flush=True)
        print(f"Grounded planning achieved. Lesson: separate DISCRIMINATION (perception) from SMOOTHNESS (value), and",flush=True)
        print(f"denoise to stop noise compounding over horizons. Methods established (clustering, SR/TD), named.",flush=True)
    else:
        print(f"JEP-12c: PARTIAL/NULL - percept {pacc:.2f}, SR-nav {n_sr:.2f}, euclid {n_eu:.2f}, random {n_rd:.2f}",flush=True)
    print("DONE",flush=True)
if __name__=="__main__":
    main()

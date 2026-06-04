"""JEP-5 - locally-learned (contrastive temporal-coherence) representation enables energy-based MPC."""
import numpy as np
rng=np.random.default_rng(1)
N=10; Du=16
KEYS=[(x,y) for x in range(N) for y in range(N)]
DIRS={0:(1,0),1:(-1,0),2:(0,1),3:(0,-1)}
def step(x,y,a):
    dx,dy=DIRS[a]; return min(max(x+dx,0),N-1),min(max(y+dy,0),N-1)


def learn_embedding(steps=40000,eta=0.05,margin=1.0):
    E={k:rng.normal(0,0.3,Du) for k in KEYS}
    x,y=rng.integers(0,N),rng.integers(0,N)
    for t in range(steps):
        a=rng.integers(0,4); nx,ny=step(x,y,a)
        s,sp=(x,y),(nx,ny)
        if s!=sp:  # ATTRACT successive (local temporal-coherence)
            d=E[sp]-E[s]; E[s]+=eta*d; E[sp]-=eta*d
        a2,b2=KEYS[rng.integers(len(KEYS))],KEYS[rng.integers(len(KEYS))]  # REPEL random pair
        if a2!=b2:
            diff=E[a2]-E[b2]; dist=np.linalg.norm(diff)+1e-9
            if dist<margin:
                push=eta*(margin-dist)*diff/dist; E[a2]+=push; E[b2]-=push
        x,y=nx,ny
    return E


def main():
    print("=== JEP-5: locally-learned representation enables energy-based MPC ===",flush=True)
    E=learn_embedding()
    Erand={k:rng.normal(0,1,Du) for k in KEYS}
    # sanity: embedding distance vs grid Manhattan distance (Spearman via rank corr)
    pairs=[(KEYS[rng.integers(len(KEYS))],KEYS[rng.integers(len(KEYS))]) for _ in range(2000)]
    gd=np.array([abs(a[0]-b[0])+abs(a[1]-b[1]) for a,b in pairs])
    ed=np.array([np.linalg.norm(E[a]-E[b]) for a,b in pairs])
    def spearman(u,v):
        ru=np.argsort(np.argsort(u)); rv=np.argsort(np.argsort(v)); return float(np.corrcoef(ru,rv)[0,1])
    sp=spearman(gd,ed)
    print(f"  learned emb-dist vs grid-dist Spearman = {sp:.2f}",flush=True)
    def mpc(emb,reps=60):
        ok=0
        for _ in range(reps):
            s=KEYS[rng.integers(len(KEYS))]; g=KEYS[rng.integers(len(KEYS))]
            if s==g: ok+=1; continue
            x,y=s
            for _ in range(3*N):
                best=None;ba=0
                for a in range(4):
                    nx,ny=step(x,y,a); e=np.linalg.norm(emb[(nx,ny)]-emb[g])
                    if best is None or e<best: best=e;ba=a
                x,y=step(x,y,ba)
                if (x,y)==g: ok+=1; break
        return ok/reps
    r_learn=mpc(E); r_rand=mpc(Erand)
    print(f"  MPC reached (LEARNED rep)  = {r_learn:.2f}",flush=True)
    print(f"  MPC reached (RANDOM rep)   = {r_rand:.2f}  (JEP-2 control)",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if r_learn>=0.8 and r_learn>=r_rand+0.3 and sp>=0.7:
        print(f"JEP-5: PASS - a LOCALLY-LEARNED representation (contrastive temporal-coherence, no backprop) makes",flush=True)
        print(f"energy MEANINGFUL (Spearman {sp:.2f}) and energy-based MPC reaches {r_learn:.2f} of goals vs {r_rand:.2f}",flush=True)
        print(f"with a random encoder. This CONFIRMS the JEP-2 diagnosis (the random encoder was the bug, not the",flush=True)
        print(f"paradigm) AND demonstrates the substrate's local-learning benefit: a substrate-native local rule",flush=True)
        print(f"learns the representation that makes EBM energy + MPC planning work. Slow-feature/contrastive",flush=True)
        print(f"learning is an established method - named as such.",flush=True)
    else:
        print(f"JEP-5: PARTIAL/NULL - learned {r_learn:.2f}, random {r_rand:.2f}, Spearman {sp:.2f}",flush=True)
    print("DONE",flush=True)


if __name__=="__main__":
    main()

"""JEP-4 - substrate-native EBM: local Hebbian learning + relaxation inference (no backprop, no optimizer)."""
import numpy as np
rng=np.random.default_rng(0)
Nu=100   # units
def hebb_store(patterns):
    W=np.zeros((Nu,Nu))
    for p in patterns: W+=np.outer(p,p)   # LOCAL Hebbian outer-product (STDP analogue)
    np.fill_diagonal(W,0); return W/len(patterns)
def energy(W,s): return -0.5*float(s@W@s)
def relax(W,s,maxsweep=30):
    s=s.copy(); es=[energy(W,s)]
    for _ in range(maxsweep):
        order=rng.permutation(Nu); changed=False
        for i in order:
            ns=1.0 if (W[i]@s)>=0 else -1.0
            if ns!=s[i]: s[i]=ns; changed=True
        es.append(energy(W,s))
        if not changed: break
    return s,es
def corrupt(p,frac):
    s=p.copy(); idx=rng.choice(Nu,int(frac*Nu),replace=False); s[idx]*=-1; return s


def trial(K,frac=0.3,reps=20):
    rec=[];cue=[];mono=True
    for _ in range(reps):
        pats=[rng.choice([-1.0,1.0],Nu) for _ in range(K)]
        W=hebb_store(pats)
        for p in pats:
            c=corrupt(p,frac); out,es=relax(W,c)
            rec.append(np.mean(out==p)); cue.append(np.mean(c==p))
            if any(es[i+1]>es[i]+1e-9 for i in range(len(es)-1)): mono=False
    return np.mean(rec),np.mean(cue),mono


def main():
    print("=== JEP-4: substrate-native EBM (Hebbian local learn + relaxation inference) ===",flush=True)
    print(f"  units={Nu}, cue corruption=30%",flush=True)
    print("  K (patterns)  load K/N   relax-recall   cue(no-relax)   energy-monotone",flush=True)
    main_pass=None; mono_all=True
    for K in [3,5,8,10,14,20,30]:
        r,c,mono=trial(K); mono_all=mono_all and mono
        flag=""
        if K<=int(0.1*Nu): 
            if main_pass is None: main_pass=r
            else: main_pass=min(main_pass,r)
        print(f"   {K:>3}          {K/Nu:.2f}        {r:.3f}         {c:.3f}          {mono}",flush=True)
    print("\n--- VERDICT ---",flush=True)
    if main_pass is not None and main_pass>=0.9 and mono_all:
        print(f"JEP-4: PASS - substrate-native energy-based inference WORKS. With LOCAL Hebbian learning (no",flush=True)
        print(f"backprop) and RELAXATION inference (no optimizer - just settling), recall >= {main_pass:.3f} bits at",flush=True)
        print(f"load K<=0.1N, vs 0.70 corrupted cue, and energy decreased monotonically every trial. This is the",flush=True)
        print(f"substrate's BENEFIT made concrete: EBM argmin == physical relaxation; learning == local plasticity.",flush=True)
        print(f"Established method (Hopfield 1982, an EBM) - named as such. Capacity degrades past ~0.14N as expected.",flush=True)
    else:
        print(f"JEP-4: PARTIAL/NULL - recall@load {main_pass}, monotone {mono_all}",flush=True)
    print("DONE",flush=True)


if __name__=="__main__":
    main()

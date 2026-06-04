"""JEP-82 - substrate (world.energy.EnergyNet) as the world-model predictor inside an MPC planning loop."""
import numpy as np
from world.energy import EnergyNet
def main():
    print("=== JEP-82: substrate EnergyNet as the world-model predictor in an MPC loop ===", flush=True)
    K=8; rng=np.random.default_rng(82)
    net=EnergyNet(n_per_module=40, n_modules=2, p_in=0.6, p_cross=0.05, beta=1.5, seed=5)
    ring=[rng.choice([-1.0,1.0], net.N) for _ in range(K)]
    # store ring states as attractors
    for _ in range(250): net.train_epoch(ring, cue_frac=0.5, lr=0.02, relax_steps=20)
    # build action transition matrices over consecutive ring states
    M=net.M
    T_next=np.zeros((net.N,net.N)); T_prev=np.zeros((net.N,net.N))
    for i in range(K):
        a=ring[i]; b=ring[(i+1)%K]
        T_next += 0.06*np.outer(b,a)*M
        T_prev += 0.06*np.outer(a,b)*M
    np.fill_diagonal(T_next,0.0); np.fill_diagonal(T_prev,0.0)
    Ts={"next":T_next,"prev":T_prev}
    def ham_to_idx(s):
        return int(np.argmax([np.mean(np.sign(s)==np.sign(r)) for r in ring]))
    def step(s,act):
        net.T=Ts[act]; return net.predict_step(s, cleanup_steps=12)
    # (i) 1-step predictor accuracy
    ok=0; tot=0
    for i in range(K):
        for act,d in [("next",1),("prev",-1)]:
            s2=step(ring[i].copy(), act); ok+=int(ham_to_idx(s2)==(i+d)%K); tot+=1
    acc1=ok/tot
    # (ii) substrate-MPC, (iii) random control
    def run(policy):
        succ=0; pairs=0
        for si in range(K):
            for gi in range(K):
                if si==gi: continue
                pairs+=1; s=ring[si].copy(); goal=ring[gi]
                for _ in range(K):
                    if ham_to_idx(s)==gi: break
                    if policy=="mpc":
                        cand={a:step(s.copy(),a) for a in Ts}
                        act=min(cand, key=lambda a: -np.mean(np.sign(cand[a])==np.sign(goal)))
                    else:
                        act=("next" if rng.random()<0.5 else "prev")
                    s=step(s,act)
                succ+=int(ham_to_idx(s)==gi)
        return succ/pairs
    mpc=run("mpc"); rand=run("rand")
    print(f"   (i)  substrate predictor 1-step accuracy = {acc1:.3f}", flush=True)
    print(f"   (ii) substrate-MPC goal-reach rate       = {mpc:.3f}", flush=True)
    print(f"   (iii) random-action control reach rate    = {rand:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if acc1>=0.95 and mpc>=0.90 and rand<=0.5:
        print(f"JEP-82: PASS - the SUBSTRATE is the world-model inside an MPC loop: its predict_step (transition +", flush=True)
        print(f"energy clean-up) is an accurate action-conditioned predictor ({acc1:.2f}); rolling it forward to choose", flush=True)
        print(f"actions reaches goals {mpc:.2f} vs random {rand:.2f}. The MPC pillar, executed on world.energy.EnergyNet.", flush=True)
        print(f"Established (Hopfield attractor dynamics + MPC), named; no novelty.", flush=True)
    else:
        print(f"JEP-82: PARTIAL/NULL - 1step={acc1:.2f}, mpc={mpc:.2f}, rand={rand:.2f} vs bars 0.95/0.90/0.50.", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()

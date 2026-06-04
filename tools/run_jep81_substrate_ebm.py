"""JEP-81 - run the EBM + predictor pillars on the ACTUAL substrate engine (world.energy.EnergyNet)."""
import numpy as np
from world.energy import EnergyNet, make_patterns
def main():
    print("=== JEP-81: EBM + predictor pillars on the ACTUAL substrate (world.energy.EnergyNet) ===", flush=True)
    print("    (first of 109 JEP experiments to import the substrate engine)", flush=True)
    # (a) + (b): completion / energy-based inference + local Hebbian learning
    net=EnergyNet(n_per_module=40, n_modules=2, p_in=0.6, p_cross=0.05, beta=1.5, seed=3)
    pats=make_patterns(net, n_patterns=5, seed=7)
    untrained=net.recall_accuracy(pats, cue_frac=0.5, trials=40)
    for _ in range(250): net.train_epoch(pats, cue_frac=0.5, lr=0.02, relax_steps=20)
    trained=net.recall_accuracy(pats, cue_frac=0.5, trials=40)
    # energy descent during relaxation (EBM inference)
    traj=[]; net.complete(pats[0], cue_frac=0.5, relax_steps=30, record=traj)
    E=[net.energy(s) for s in traj]
    diffs=np.diff(E); monotone=float(np.mean(diffs<=1e-9))  # fraction of non-increasing steps
    print(f"   (a) EBM inference: energy over {len(E)} relax steps {E[0]:.1f} -> {E[-1]:.1f}; non-increasing frac={monotone:.2f}", flush=True)
    print(f"   (b) local Hebbian learning: completion acc untrained={untrained:.3f} -> trained={trained:.3f} (chance~0.5)", flush=True)
    # (c) predictor / world-model: sequence learning via asymmetric T
    net2=EnergyNet(n_per_module=40, n_modules=2, seed=11)
    seq=make_patterns(net2, n_patterns=5, seed=21)
    net2.train_sequence(seq, lr_T=0.06, lr_W=0.02, assoc_epochs=120)
    rec=net2.recall_sequence(seq[0], length=len(seq), cleanup_steps=12)
    # untrained control
    net3=EnergyNet(n_per_module=40, n_modules=2, seed=11)
    rec0=net3.recall_sequence(seq[0], length=len(seq), cleanup_steps=12)
    def seqacc(rec):
        a=[]
        for t in range(1,len(seq)):
            a.append(float(np.mean(np.sign(rec[t])==np.sign(seq[t]))))
        return float(np.mean(a))
    sa=seqacc(rec); sa0=seqacc(rec0)
    print(f"   (c) predictor/world-model: sequence recall per-step acc trained={sa:.3f} vs untrained={sa0:.3f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    a_ok=monotone>=0.95; b_ok=trained>=0.90 and untrained<=0.7; c_ok=sa>=0.90 and sa>sa0+0.2
    if a_ok and b_ok and c_ok:
        print(f"JEP-81: PASS - the SUBSTRATE engine performs all three on its own dynamics: (a) relaxation is energy-", flush=True)
        print(f"minimizing EBM inference (energy monotone {monotone:.2f}); (b) contrastive-Hebbian LOCAL learning lifts", flush=True)
        print(f"completion {untrained:.2f}->{trained:.2f} with NO backprop; (c) the asymmetric transition matrix is a", flush=True)
        print(f"predictive world-model (sequence recall {sa:.2f}). The substrate IS the backprop-free EBM+predictor the", flush=True)
        print(f"chain abstracted - now executed on world.energy.EnergyNet. Established (Hopfield/contrastive-Hebbian), named.", flush=True)
    else:
        print(f"JEP-81: PARTIAL/NULL - a={a_ok}(mono {monotone:.2f}) b={b_ok}({untrained:.2f}->{trained:.2f}) c={c_ok}(sa {sa:.2f}/{sa0:.2f})", flush=True)
    print("HONEST SCOPE: EnergyNet = the ENGINEERED energy layer (world/); spontaneous-matter long-term MEMORY closed", flush=True)
    print("NEGATIVE separately (G88-96). Defensible claim: substrate as energy engine + local learner + short predictor.", flush=True)
    print("DONE", flush=True)
if __name__=="__main__": main()

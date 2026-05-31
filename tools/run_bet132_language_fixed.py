"""BET-132 — micro-language next-word generation with a corrected no-rule control."""
import json
from pathlib import Path
import numpy as np
from world.vsa import rand_hv, bind, bundle_analog, CleanupMemory
from world.reservoir import SubstrateReservoir

D = 512
N_SUBJ, N_VERB, N_OBJ = 8, 6, 6

def setup(seed):
    rng = np.random.default_rng(seed)
    subj = [rand_hv(D, rng) for _ in range(N_SUBJ)]
    verb = [rand_hv(D, rng) for _ in range(N_VERB)]
    obj  = [rand_hv(D, rng) for _ in range(N_OBJ)]
    role_s = rand_hv(D, rng); role_v = rand_hv(D, rng)
    cleanup = CleanupMemory()
    for k in range(N_OBJ):
        cleanup.add(f"obj{k}", obj[k])
    return rng, subj, verb, obj, role_s, role_v, cleanup

def code(s, v, subj, verb, role_s, role_v, mask_verb=False):
    parts = [bind(role_s, subj[s])]
    if not mask_verb:
        parts.append(bind(role_v, verb[v]))
    c = bundle_analog(parts); return c / np.linalg.norm(c)

def run(seed=0, random_target=False, mask_verb=False, checkpoints=(0.25, 1.0)):
    rng, subj, verb, obj, role_s, role_v, cleanup = setup(seed)
    v2o = np.arange(N_OBJ)                                  # verb v selects object v
    pairs = [(s, v) for s in range(N_SUBJ) for v in range(N_VERB)]
    rng.shuffle(pairs)
    te = pairs[:16]; tr = pairs[16:]
    # per-sentence random target map (only used by the no-rule control)
    rand_obj = {p: int(rng.integers(N_OBJ)) for p in pairs}
    def target_idx(s, v):
        return rand_obj[(s, v)] if random_target else v2o[v]
    net = SubstrateReservoir(D, D, D=D, seed=seed, ridge=1e-2)
    net.features = lambda x: np.asarray(x, float)
    net.P = np.eye(D) / 1e-2; net.Wout = np.zeros((D, D)); net.D = D

    def heldout_acc():
        ok = 0
        for (s, v) in te:
            c = code(s, v, subj, verb, role_s, role_v, mask_verb)
            name, _ = cleanup.cleanup(net.predict(c))
            if int(name[3:]) == target_idx(s, v): ok += 1
        return ok / len(te)

    accs = {}; cps = sorted(set(int(round(f*len(tr))) for f in checkpoints))
    for i, (s, v) in enumerate(tr, 1):
        c = code(s, v, subj, verb, role_s, role_v, mask_verb)
        net.learn_online(c, obj[target_idx(s, v)])
        if i in cps: accs[i] = heldout_acc()
    return accs

if __name__ == "__main__":
    print("=== BET-132: micro-language next-word, corrected control ===", flush=True)
    accs = run(); k = sorted(accs); early, full = accs[k[0]], accs[k[-1]]
    rnd = run(random_target=True); rnd_full = rnd[sorted(rnd)[-1]]
    sonly = run(mask_verb=True); sonly_full = sonly[sorted(sonly)[-1]]
    print(f"  held-out acc @25% / @100% : {early:.3f} / {full:.3f}", flush=True)
    print(f"  no-rule (random target)   : {rnd_full:.3f}", flush=True)
    print(f"  subject-only (verb masked): {sonly_full:.3f}", flush=True)
    T132a = full >= 0.85; T132b = (full-early) >= 0.15; T132c = rnd_full < 0.40; T132d = sonly_full < 0.40
    passed = T132a and T132b and T132c and T132d
    print("\n--- VERDICT ---", flush=True)
    print(f"T132a held-out >=0.85    : {T132a} ({full:.3f})", flush=True)
    print(f"T132b online gain >=0.15 : {T132b} ({full-early:.3f})", flush=True)
    print(f"T132c no-rule <0.40      : {T132c} ({rnd_full:.3f})", flush=True)
    print(f"T132d verb-needed <0.40  : {T132d} ({sonly_full:.3f})", flush=True)
    print(f"\nBET-132: {'PASS - substrate generates correct written next word for unseen sentences; depends on a real regularity and on the verb; online; no transformer' if passed else 'NULL/partial'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-132'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps(
        {"early":early,"full":full,"random":rnd_full,"subj_only":sonly_full,"passed":passed}, indent=2))
    print("DONE", flush=True)

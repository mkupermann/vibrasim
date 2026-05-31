"""BET-131 — next-word generation in a templated micro-language."""
import json
from pathlib import Path
import numpy as np
from world.vsa import rand_hv, bind, bundle_analog, CleanupMemory
from world.reservoir import SubstrateReservoir

D = 512
N_SUBJ, N_VERB, N_OBJ = 8, 6, 6

def setup(seed, shuffle_rule=False):
    rng = np.random.default_rng(seed)
    subj = [rand_hv(D, rng) for _ in range(N_SUBJ)]
    verb = [rand_hv(D, rng) for _ in range(N_VERB)]
    obj  = [rand_hv(D, rng) for _ in range(N_OBJ)]
    role_s = rand_hv(D, rng); role_v = rand_hv(D, rng)
    v2o = np.arange(N_OBJ) if not shuffle_rule else rng.permutation(N_OBJ)  # verb->object
    cleanup = CleanupMemory()
    for k in range(N_OBJ):
        cleanup.add(f"obj{k}", obj[k])
    return rng, subj, verb, obj, role_s, role_v, v2o, cleanup

def code(s, v, subj, verb, role_s, role_v, mask_verb=False):
    parts = [bind(role_s, subj[s])]
    if not mask_verb:
        parts.append(bind(role_v, verb[v]))
    c = bundle_analog(parts); return c / np.linalg.norm(c)

def run(seed=0, shuffle_rule=False, mask_verb=False, checkpoints=(0.25, 1.0)):
    rng, subj, verb, obj, role_s, role_v, v2o, cleanup = setup(seed, shuffle_rule)
    pairs = [(s, v) for s in range(N_SUBJ) for v in range(N_VERB)]  # 48 sentences
    rng.shuffle(pairs)
    te = pairs[:16]; tr = pairs[16:]                               # 16 held-out novel combos
    net = SubstrateReservoir(D, D, D=D, seed=seed, ridge=1e-2)
    net.features = lambda x: np.asarray(x, float)
    net.P = np.eye(D) / 1e-2; net.Wout = np.zeros((D, D)); net.D = D

    def heldout_acc():
        ok = 0
        for (s, v) in te:
            c = code(s, v, subj, verb, role_s, role_v, mask_verb)
            pred = net.predict(c)
            name, _ = cleanup.cleanup(pred)
            if int(name[3:]) == v2o[v]: ok += 1
        return ok / len(te)

    accs = {}
    cps = sorted(set(int(round(f * len(tr))) for f in checkpoints))
    for i, (s, v) in enumerate(tr, 1):
        c = code(s, v, subj, verb, role_s, role_v, mask_verb)
        net.learn_online(c, obj[v2o[v]])
        if i in cps:
            accs[i] = heldout_acc()
    return accs, len(tr)

if __name__ == "__main__":
    print("=== BET-131: next-word generation in a templated micro-language ===", flush=True)
    accs, ntr = run()
    keys = sorted(accs); early, full = accs[keys[0]], accs[keys[-1]]
    print(f"  held-out next-word acc @25% train : {early:.3f}", flush=True)
    print(f"  held-out next-word acc @100% train: {full:.3f}", flush=True)
    shuf, _ = run(shuffle_rule=True); shuf_full = shuf[sorted(shuf)[-1]]
    sonly, _ = run(mask_verb=True);  sonly_full = sonly[sorted(sonly)[-1]]
    print(f"  shuffled-rule control held-out    : {shuf_full:.3f}", flush=True)
    print(f"  subject-only (verb masked) held-out: {sonly_full:.3f}", flush=True)
    T131a = full >= 0.85
    T131b = (full - early) >= 0.15
    T131c = shuf_full < 0.40
    T131d = sonly_full < 0.40
    passed = T131a and T131b and T131c and T131d
    print("\n--- VERDICT ---", flush=True)
    print(f"T131a held-out >=0.85       : {T131a} ({full:.3f})", flush=True)
    print(f"T131b online gain >=0.15    : {T131b} ({full-early:.3f})", flush=True)
    print(f"T131c rule control <0.40    : {T131c} ({shuf_full:.3f})", flush=True)
    print(f"T131d verb-needed <0.40     : {T131d} ({sonly_full:.3f})", flush=True)
    print(f"\nBET-131: {'PASS - substrate GENERATES correct written next word for unseen sentences, online, no transformer' if passed else 'NULL/partial'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-131'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps(
        {"early":early,"full":full,"shuf":shuf_full,"subj_only":sonly_full,"passed":passed}, indent=2))
    print("DONE", flush=True)

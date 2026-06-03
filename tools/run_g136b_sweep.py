"""G136b — give the EQMOD-2 stack its BEST shot on real text: sweep context K and dim D vs bigram.
If even the best config ~ bigram, the bigram-level ceiling is solid (fair test, no physics)."""
import numpy as np
from collections import defaultdict, Counter
from world.vsa import rand_hv, bind, bundle_analog
from world.reservoir import SubstrateReservoir

TEXT = (
    "the cat sat on the mat . the dog sat on the log . the cat ran to the dog . "
    "the dog ran to the cat . the cat saw the dog on the mat . the dog saw the cat on the log . "
    "a cat and a dog sat on the mat . a dog and a cat ran to the log . the cat sat and the dog ran . "
    "the dog sat and the cat ran . the cat saw a log . the dog saw a mat . the cat ran on the log . "
    "the dog ran on the mat ."
).split()


def eq_acc(K, D, seed=1):
    vocab = sorted(set(TEXT)); V = len(vocab); vi = {w: i for i, w in enumerate(vocab)}
    rng = np.random.default_rng(seed)
    HV = {w: rand_hv(D, rng) for w in vocab}; POS = [rand_hv(D, rng) for _ in range(K)]
    S = [([TEXT[t - K + j] for j in range(K)], TEXT[t]) for t in range(K, len(TEXT))]
    n = len(S); ntr = int(0.75 * n)
    res = SubstrateReservoir(in_dim=D, out_dim=V, D=D, seed=seed, ridge=1e-1)
    chv = lambda ctx: bundle_analog([bind(POS[j], HV[w]) for j, w in enumerate(ctx)])
    for ctx, nxt in S[:ntr]:
        y = np.zeros(V); y[vi[nxt]] = 1.0; res.learn_online(chv(ctx), y)
    return sum(1 for ctx, nxt in S[ntr:] if int(np.argmax(res.predict(chv(ctx)))) == vi[nxt]) / max(1, n - ntr)


def bigram_acc(K=1):
    vocab = sorted(set(TEXT))
    S = [([TEXT[t - max(K,1) + j] for j in range(max(K,1))], TEXT[t]) for t in range(max(K,1), len(TEXT))]
    n = len(S); ntr = int(0.75 * n)
    big = defaultdict(Counter); uni = Counter()
    for ctx, nxt in S[:ntr]:
        big[ctx[-1]][nxt] += 1; uni[nxt] += 1
    pred = lambda ctx: (big[ctx[-1]].most_common(1)[0][0] if big[ctx[-1]] else uni.most_common(1)[0][0])
    return sum(1 for ctx, nxt in S[ntr:] if pred(ctx) == nxt) / max(1, n - ntr)


if __name__ == "__main__":
    print("=== G136b: best-shot sweep (EQMOD-2 stack) vs bigram on real text ===", flush=True)
    bg = bigram_acc()
    print(f"  bigram baseline = {bg:.2f}", flush=True)
    best = 0.0; bestcfg = None
    for K in [2, 3, 4]:
        for D in [600, 1500, 3000]:
            a = np.mean([eq_acc(K, D, seed=s) for s in (1, 2, 3)])
            print(f"  K={K} D={D}: stack acc = {a:.2f}", flush=True)
            if a > best:
                best, bestcfg = a, (K, D)
    print("\n--- VERDICT ---", flush=True)
    print(f"  best stack config {bestcfg} acc = {best:.2f} vs bigram {bg:.2f}", flush=True)
    if best >= bg + 0.10:
        print("G136b: PASS - best config beats bigram (the stack captures real structure given enough dim/context)", flush=True)
    else:
        print("G136b: NULL(ceiling confirmed) - even the best config ~ bigram; the no-LLM stack is bigram-level on real text", flush=True)
    print("DONE", flush=True)

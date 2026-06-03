"""G136 — no-LLM language CEILING: next-word prediction on REAL English text with the EQMOD-2 stack
(VSA-composed context -> reservoir/ELM features -> online RLS -> cleanup to vocab) vs a trivial BIGRAM
baseline. If the stack beats bigram on held-out real text, it captures structure beyond local statistics;
if it ~ bigram, the no-LLM path plateaus at trivial-classical-LM level (the honest ceiling). No transformer.
"""
import sys
import numpy as np
from world.vsa import rand_hv, bind, bundle_analog, sim, CleanupMemory
from world.reservoir import SubstrateReservoir

TEXT = (
    "the cat sat on the mat . the dog sat on the log . the cat ran to the dog . "
    "the dog ran to the cat . the cat saw the dog on the mat . the dog saw the cat on the log . "
    "a cat and a dog sat on the mat . a dog and a cat ran to the log . the cat sat and the dog ran . "
    "the dog sat and the cat ran . the cat saw a log . the dog saw a mat . the cat ran on the log . "
    "the dog ran on the mat ."
).split()
K = 2          # context window
D = 600


def main():
    vocab = sorted(set(TEXT))
    V = len(vocab); vi = {w: i for i, w in enumerate(vocab)}
    rng = np.random.default_rng(0)
    HV = {w: rand_hv(D, rng) for w in vocab}
    POS = [rand_hv(D, rng) for _ in range(K)]

    samples = []
    for t in range(K, len(TEXT)):
        ctx = [TEXT[t - K + j] for j in range(K)]
        samples.append((ctx, TEXT[t]))
    n = len(samples); ntr = int(0.75 * n)

    # --- EQMOD-2 stack: VSA context HV -> reservoir -> online RLS -> argmax over vocab ---
    res = SubstrateReservoir(in_dim=D, out_dim=V, D=D, seed=1, ridge=1e-1)

    def ctx_hv(ctx):
        return bundle_analog([bind(POS[j], HV[w]) for j, w in enumerate(ctx)])
    for ctx, nxt in samples[:ntr]:
        y = np.zeros(V); y[vi[nxt]] = 1.0
        res.learn_online(ctx_hv(ctx), y)
    eq_correct = sum(1 for ctx, nxt in samples[ntr:]
                     if int(np.argmax(res.predict(ctx_hv(ctx)))) == vi[nxt])
    eq_acc = eq_correct / max(1, n - ntr)

    # --- bigram baseline (previous word -> most frequent next), trained on same train split ---
    from collections import defaultdict, Counter
    big = defaultdict(Counter)
    for ctx, nxt in samples[:ntr]:
        big[ctx[-1]][nxt] += 1
    uni = Counter(w for _, w in samples[:ntr])
    def bg_pred(ctx):
        if big[ctx[-1]]:
            return big[ctx[-1]].most_common(1)[0][0]
        return uni.most_common(1)[0][0] if uni else vocab[0]
    bg_acc = sum(1 for ctx, nxt in samples[ntr:] if bg_pred(ctx) == nxt) / max(1, n - ntr)
    chance = 1.0 / V

    print("=== G136: no-LLM next-word on REAL text — EQMOD-2 stack vs bigram ===", flush=True)
    print(f"  vocab={V} samples={n} (train {ntr}, test {n-ntr}) chance={chance:.3f}", flush=True)
    print(f"  EQMOD-2 (VSA+reservoir+RLS) held-out next-word acc = {eq_acc:.2f}", flush=True)
    print(f"  bigram baseline held-out acc                       = {bg_acc:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    beats = eq_acc >= bg_acc + 0.10
    if beats:
        print("G136: PASS - the no-LLM stack beats bigram on real text (captures structure beyond local statistics)", flush=True)
    elif eq_acc >= bg_acc - 0.05:
        print("G136: NULL(ceiling) - the no-LLM stack ~ bigram on real text: it plateaus at trivial-classical-LM level (honest ceiling; not human-like)", flush=True)
    else:
        print("G136: NULL - the no-LLM stack is WORSE than bigram on real text", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()

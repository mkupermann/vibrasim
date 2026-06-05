"""JEP-327 — perceive a written WORD from pixels, then reason about it from the durable store. No transformer.
Pre-registered bars in docs/amendments/jep327_word_perception_reasoning.md.
"""
import json, tempfile, os, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from teach_gui import render_letter                  # scale-normalized glyph renderer
from world.active_learner import ActiveLearner
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery

VOCAB = ["dog", "cat", "bird", "fish", "poodle", "salmon"]
FACTS = [("dog", "isa", "mammal"), ("cat", "isa", "mammal"), ("bird", "isa", "animal"),
         ("fish", "isa", "animal"), ("poodle", "isa", "dog"), ("salmon", "isa", "fish"),
         ("mammal", "isa", "animal")]
GT_MAMMAL = {"dog", "cat", "poodle"}                  # is-a mammal (poodle via dog)


def edit_distance(a, b):
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, cb in enumerate(b, 1):
            prev, dp[j] = dp[j], min(dp[j] + 1, dp[j - 1] + 1, prev + (ca != cb))
    return dp[-1]


def cleanup(raw, lexicon):
    return min(lexicon, key=lambda w: (edit_distance(raw, w), w))


def teach_alphabet(al, seed):
    rng = np.random.default_rng(seed)
    for ch in set("".join(VOCAB).upper()):
        for _ in range(5):
            al.teach("write", ch, render_letter(ch, rng).ravel())


def recognize_word(al, word, rng):
    raw = ""
    for ch in word.upper():
        g = render_letter(ch, rng)
        raw += (al.guess("write", g.ravel())[0] or "?")
    return raw.lower()


def run_seed(seed):
    al = ActiveLearner(tau=0.12); teach_alphabet(al, seed)
    mem = SubstrateMemory(D=4096, tau=0.12, directed=True)
    for (a, r, b) in FACTS:
        mem.add_fact(a, r, b)
    d = tempfile.mkdtemp(prefix=f"word_{seed}_"); mem.save(d)
    m = SubstrateMemory.load(d); bq = BrainQuery(m, seed=seed)

    rng = np.random.default_rng(seed + 100)
    raw_ok = clean_ok = reason_ok = 0
    for word in VOCAB:
        for _ in range(4):
            raw = recognize_word(al, word, rng)
            clean = cleanup(raw, VOCAB)
            raw_ok += (raw == word)
            clean_ok += (clean == word)
            # perceive -> reason: is the perceived word a mammal?
            said_mammal = bq.is_a(clean, "mammal")
            reason_ok += (said_mammal == (word in GT_MAMMAL))
    n = len(VOCAB) * 4
    return {"raw_acc": round(raw_ok / n, 3), "word_acc": round(clean_ok / n, 3),
            "reason_acc": round(reason_ok / n, 3)}


if __name__ == "__main__":
    print("=== JEP-327: perceive a WORD -> reason from the durable store ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: raw letter-join={R[s]['raw_acc']} | word (after cleanup)={R[s]['word_acc']} | "
              f"perceive->reason={R[s]['reason_acc']}", flush=True)
    J327a = all(R[s]['word_acc'] >= 0.90 for s in seeds)
    J327b = all(R[s]['reason_acc'] >= 0.90 for s in seeds)
    passed = J327a and J327b
    print("\n--- VERDICT ---", flush=True)
    print(f"J327a word recognition after cleanup (>=.90): {J327a}", flush=True)
    print(f"J327b perceive->reason matches truth (>=.90) : {J327b}", flush=True)
    verdict = ("PASS - a written word is perceived from pixels, recognized, and reasoned about from the durable "
               "store end to end") if passed else "NULL/partial"
    print(f"\nJEP-327: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP327"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J327a": J327a, "J327b": J327b, "passed": passed}, default=str))
    print("DONE", flush=True)

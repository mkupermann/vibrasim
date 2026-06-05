"""JEP-328 — lexicon cleanup recovers noisy words. Sweep glyph noise; raw vs cleaned word accuracy. No transformer.
Pre-registered bars in docs/amendments/jep328_noisy_word_cleanup.md.
"""
import json, os, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from teach_gui import render_letter
from world.active_learner import ActiveLearner

VOCAB = ["dog", "cat", "bird", "fish", "poodle", "salmon", "horse", "eagle"]


def edit_distance(a, b):
    dp = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, dp[0] = dp[0], i
        for j, cb in enumerate(b, 1):
            prev, dp[j] = dp[j], min(dp[j] + 1, dp[j - 1] + 1, prev + (ca != cb))
    return dp[-1]


def cleanup(raw, lex):
    return min(lex, key=lambda w: (edit_distance(raw, w), w))


def teach_alphabet(al, seed):
    rng = np.random.default_rng(seed)
    for ch in set("".join(VOCAB).upper()):
        for _ in range(6):
            al.teach("write", ch, render_letter(ch, rng).ravel())


def recog_word(al, word, sigma, rng):
    raw = ""
    for ch in word.upper():
        g = render_letter(ch, rng) + rng.normal(0, sigma, (28, 28))
        raw += (al.guess("write", np.clip(g, 0, 1).ravel())[0] or "?")
    return raw.lower()


def run_seed(seed, sigmas):
    al = ActiveLearner(tau=0.12); teach_alphabet(al, seed)
    rng = np.random.default_rng(seed + 100)
    out = {}
    for sg in sigmas:
        raw_ok = clean_ok = 0
        for word in VOCAB:
            for _ in range(5):
                raw = recog_word(al, word, sg, rng)
                raw_ok += (raw == word); clean_ok += (cleanup(raw, VOCAB) == word)
        n = len(VOCAB) * 5
        out[sg] = (round(raw_ok / n, 3), round(clean_ok / n, 3))
    return out


if __name__ == "__main__":
    print("=== JEP-328: lexicon cleanup recovers noisy words ===", flush=True)
    seeds = [0, 7]; sigmas = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
    R = {s: run_seed(s, sigmas) for s in seeds}
    for s in seeds:
        for sg in sigmas:
            raw, cln = R[s][sg]
            print(f"  seed {s} sigma={sg}: raw={raw} cleaned={cln}", flush=True)

    # J328a: exists sigma with raw<0.70 and cleaned>=0.90 (both seeds)
    def has_window(s):
        return any(R[s][sg][0] < 0.70 and R[s][sg][1] >= 0.90 for sg in sigmas)
    J328a = all(has_window(s) for s in seeds)
    # J328b: sigma where cleaned first <0.90
    sstar = {s: next((sg for sg in sigmas if R[s][sg][1] < 0.90), f">{sigmas[-1]}") for s in seeds}
    print(f"\n  cleanup-helps window exists: {J328a} | cleaned<0.90 first at sigma={sstar}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    print(f"J328a cleanup demonstrably recovers noisy words: {J328a}", flush=True)
    verdict = ("PASS - there is a noise regime where raw recognition fails but edit-distance cleanup recovers the "
               "word; the cure's capacity is characterized") if J328a else "NULL/partial - see curves"
    print(f"\nJEP-328: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP328"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": {str(s): {str(k): v for k, v in R[s].items()} for s in seeds},
                                                  "J328a": J328a, "sstar": {str(k): str(v) for k, v in sstar.items()},
                                                  "passed": J328a}, default=str))
    print("DONE", flush=True)

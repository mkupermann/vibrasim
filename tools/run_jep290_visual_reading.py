"""JEP-290 — visual READING: see a written WORD -> recognize its letters -> compose -> UNDERSTAND it (per Michael:
"words after letters"). The developmental bridge from grounded letters (JEP-287) to the prose engine (the base).

The engine SEES a word rendered as a row of letter cells, recognizes each letter with its grounded letter
recognizer, assembles the string, cleans up to the nearest KNOWN word (edit distance over a small vocabulary), then
REASONS about it via what it READ. No transformer, no pretrained model.

Pre-registered bars in docs/amendments/jep290_visual_reading.md.
"""
import json, string
from pathlib import Path
import numpy as np

from world.active_learner import ActiveLearner
from world.understanding import UnderstandingEngine
from tools.run_jep287_active_letter_learning import render_letter, SIZE

LETTERS = string.ascii_uppercase
VOCAB = ["DOG", "CAT", "POODLE", "MAMMAL", "ANIMAL", "BIRD", "ROBIN", "FISH"]


def edit_distance(a, b):
    m, n = len(a), len(b)
    dp = list(range(n + 1))
    for i in range(1, m + 1):
        prev, dp[0] = dp[0], i
        for j in range(1, n + 1):
            cur = dp[j]
            dp[j] = min(dp[j] + 1, dp[j - 1] + 1, prev + (a[i - 1] != b[j - 1]))
            prev = cur
    return dp[n]


def render_word(word, rng):
    """A word as a row of centred letter cells (fixed-width -> trivial segmentation)."""
    return [render_letter(ch, rng).reshape(SIZE, SIZE) for ch in word]


def run_seed(seed):
    rng = np.random.default_rng(seed)
    # the engine has LEARNED its letters (grounded) and READ a taxonomy
    al = ActiveLearner(tau=0.12)
    for ch in LETTERS:
        for _ in range(25):
            al.teach("sight", ch, render_letter(ch, rng).ravel())
    eng = UnderstandingEngine(seed=seed)
    eng.read("A poodle is a dog. A dog is a mammal. A mammal is an animal. A robin is a bird. A bird is an animal.")

    def read_word(cells):
        raw = "".join(al.guess("sight", c.ravel())[0] for c in cells)        # recognize each letter
        return min(VOCAB, key=lambda w: edit_distance(raw, w)), raw          # cleanup to nearest known word

    raw_ok = clean_ok = tot = 0
    demo = None
    for word in VOCAB:
        for _ in range(8):
            tot += 1
            cells = render_word(word, rng)
            cleaned, raw = read_word(cells)
            raw_ok += (raw == word)
            clean_ok += (cleaned == word)
            if demo is None:
                demo = (word, raw, cleaned)

    # READING -> UNDERSTANDING: read 'POODLE' and 'ROBIN' from pixels, then reason
    q = {}
    for word, (concept, c) in [("POODLE", ("poodle", "animal")), ("ROBIN", ("robin", "animal"))]:
        cleaned, _ = read_word(render_word(word, rng))
        q[word] = (cleaned == word and eng.is_a(cleaned.lower(), c))          # read the word AND reason about it
    read_then_reason = all(q.values())

    return {"raw_word_acc": round(raw_ok / tot, 3), "cleaned_word_acc": round(clean_ok / tot, 3),
            "read_then_reason": bool(read_then_reason), "demo": demo}


if __name__ == "__main__":
    print("=== JEP-290: visual reading (see word -> recognize letters -> compose -> understand) ===", flush=True)
    seeds = [42, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]; w, raw, cl = r["demo"]
        print(f"  seed {s}: raw-letter-string word acc={r['raw_word_acc']} | cleaned-to-vocab word acc="
              f"{r['cleaned_word_acc']} | read+reason={r['read_then_reason']} | demo: saw '{w}' -> read '{raw}' "
              f"-> '{cl}'", flush=True)

    J290a = all(R[s]['cleaned_word_acc'] >= 0.90 for s in seeds)
    J290b = all(R[s]['cleaned_word_acc'] >= R[s]['raw_word_acc'] for s in seeds)    # cleanup helps (or ties)
    J290c = all(R[s]['read_then_reason'] for s in seeds)
    passed = J290a and J290c

    print("\n--- VERDICT ---", flush=True)
    print(f"J290a reads words (cleaned >=0.90)      : {J290a}", flush=True)
    print(f"J290b vocab cleanup helps               : {J290b}", flush=True)
    print(f"J290c READ a word from pixels THEN reason: {J290c}", flush=True)
    verdict = ("PASS - the engine READS written words from pixels (letters -> word) and UNDERSTANDS them via read "
               "prose -- the developmental letters->words->understanding bridge") if passed else "NULL/partial"
    print(f"\nJEP-290: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP290"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps(
        {"rows": {str(s): R[s] for s in seeds}, "J290a": J290a, "J290b": J290b, "J290c": J290c, "passed": passed},
        indent=2, default=str))
    print("DONE", flush=True)

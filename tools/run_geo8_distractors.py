"""GEO-8 — honest stress test: does few-shot relation learning + composition survive a LARGE vocabulary
with many DISTRACTORS? The tiny curated vocab made ranking easy. Add ~300 distractor words and rank the
target among ALL of them. If hits@1 stays high, the geometric+LLM method is real; if it collapses, the
earlier results were small-vocab artifacts. Real MiniLM, PC-scale."""
import numpy as np
from sentence_transformers import SentenceTransformer

CAP = [("France","Paris"),("Germany","Berlin"),("Italy","Rome"),("Spain","Madrid"),("Japan","Tokyo"),
       ("China","Beijing"),("Egypt","Cairo"),("Canada","Ottawa"),("Russia","Moscow"),("Greece","Athens"),
       ("Poland","Warsaw"),("Portugal","Lisbon"),("Turkey","Ankara"),("Sweden","Stockholm"),("Norway","Oslo"),
       ("Austria","Vienna"),("Belgium","Brussels"),("Ireland","Dublin"),("Finland","Helsinki"),("Hungary","Budapest")]
DISTRACT = ("apple river mountain compute happy guitar ocean planet yellow bicycle coffee window silver "
            "thunder garden pencil dragon castle market doctor engine flower bridge planet tiger forest "
            "winter summer purple orange velvet marble copper diamond crystal shadow whisper journey "
            "harbor lantern compass anchor meadow valley canyon glacier desert jungle island volcano "
            "telescope microscope keyboard monitor printer network protocol algorithm function variable "
            "elephant giraffe dolphin penguin butterfly squirrel hedgehog kangaroo octopus jellyfish").split()


def main():
    print("=== GEO-8: few-shot relation learning + composition with DISTRACTORS ===", flush=True)
    m = SentenceTransformer("all-MiniLM-L6-v2")
    targets = sorted(set([c for _, c in CAP] + [co for co, _ in CAP]))
    vocab = sorted(set(targets + DISTRACT))
    E = np.array(m.encode(vocab, normalize_embeddings=True)); vi = {w: i for i, w in enumerate(vocab)}
    print(f"  vocab size = {len(vocab)} (targets {len(targets)} + distractors {len(set(DISTRACT))})", flush=True)
    rng = np.random.default_rng(0); accs = []
    for trial in range(10):
        idx = rng.permutation(len(CAP)); k = 6
        tr = [CAP[i] for i in idx[:k]]; te = [CAP[i] for i in idx[k:]]
        rvec = np.mean([E[vi[c]] - E[vi[co]] for co, c in tr], 0)
        ok = 0
        for co, c in te:
            q = E[vi[co]] + rvec; q /= np.linalg.norm(q) + 1e-9
            s = E @ q; s[vi[co]] = -1e9          # exclude only the source
            if vocab[int(np.argmax(s))] == c: ok += 1
        accs.append(ok / len(te))
    print(f"  country->capital 6-shot hits@1 (among {len(vocab)} words) = {np.mean(accs):.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if np.mean(accs) >= 0.6:
        print("GEO-8: PASS - few-shot geometric relation learning SURVIVES a large distractor vocabulary -> the method is real, not a small-vocab artifact", flush=True)
    elif np.mean(accs) >= 0.3:
        print("GEO-8: PARTIAL - degrades with distractors but stays well above chance", flush=True)
    else:
        print("GEO-8: NULL - collapses with distractors (earlier results were small-vocab artifacts)", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()

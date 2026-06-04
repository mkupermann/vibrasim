"""GEO-6 — the LEARNING half: few-shot learning of a NEW relation as a geometric transform in LLM space,
generalizing to NOVEL pairs (= learning + understanding). Given k example pairs of a relation (e.g.
country->capital), LEARN the relation vector (mean offset) OR a small linear map W (h@W ~ t), then apply to
HELD-OUT sources and rank the true target. Tests whether the geometric+LLM substrate LEARNS relations from
few examples and UNDERSTANDS (generalizes). Real MiniLM embeddings, PC-scale."""
import numpy as np
from sentence_transformers import SentenceTransformer

RELATIONS = {
  "capital": [("France","Paris"),("Germany","Berlin"),("Italy","Rome"),("Spain","Madrid"),
              ("Japan","Tokyo"),("China","Beijing"),("Egypt","Cairo"),("Canada","Ottawa"),
              ("Russia","Moscow"),("Brazil","Brasilia"),("Greece","Athens"),("Poland","Warsaw")],
  "plural": [("cat","cats"),("dog","dogs"),("house","houses"),("car","cars"),("tree","trees"),
             ("book","books"),("city","cities"),("box","boxes"),("child","children"),("man","men")],
  "past":  [("walk","walked"),("play","played"),("jump","jumped"),("call","called"),("open","opened"),
            ("run","ran"),("go","went"),("eat","ate"),("see","saw"),("take","took")],
}


def main():
    print("=== GEO-6: few-shot geometric relation LEARNING in LLM space ===", flush=True)
    m = SentenceTransformer("all-MiniLM-L6-v2")
    for name, pairs in RELATIONS.items():
        words = sorted(set(w for p in pairs for w in p))
        E = np.array(m.encode(words, normalize_embeddings=True)); vi = {w: i for i, w in enumerate(words)}
        srcs = [a for a, b in pairs]; tgts = [b for a, b in pairs]
        accs_off, accs_map = [], []
        rng = np.random.default_rng(0)
        for trial in range(8):
            idx = rng.permutation(len(pairs)); k = 4
            tr = [pairs[i] for i in idx[:k]]; te = [pairs[i] for i in idx[k:]]
            # method A: mean offset (learn relation as a translation from k examples)
            rvec = np.mean([E[vi[b]] - E[vi[a]] for a, b in tr], 0)
            # method B: small ridge linear map h@W ~ t (learn a transformation)
            Htr = np.array([E[vi[a]] for a, b in tr]); Ttr = np.array([E[vi[b]] for a, b in tr])
            W = np.linalg.solve(Htr.T @ Htr + 1.0 * np.eye(E.shape[1]), Htr.T @ Ttr)
            def rank1(q, true):
                sims = E @ (q / (np.linalg.norm(q) + 1e-9)); sims[vi[true_src]] = -1e9
                return words[int(np.argmax(sims))] == true
            ok_off = ok_map = 0
            for a, b in te:
                true_src = a
                qo = E[vi[a]] + rvec; qm = E[vi[a]] @ W
                if rank1(qo, b): ok_off += 1
                if rank1(qm, b): ok_map += 1
            accs_off.append(ok_off / len(te)); accs_map.append(ok_map / len(te))
        print(f"  {name:8s}: 4-shot offset hits@1 = {np.mean(accs_off):.2f} | linear-map hits@1 = {np.mean(accs_map):.2f}", flush=True)
    print("\n  (held-out pairs; learns the relation from 4 examples, applies to unseen sources)", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()

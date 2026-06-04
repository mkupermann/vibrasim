"""GEO-7 — COMPOSITIONAL understanding on LLM embeddings: learn TWO relations few-shot, then COMPOSE them
for a multi-hop inference never trained as a composite. E.g. learn country->capital and country->language;
then given a CAPITAL infer the LANGUAGE via capital -> (inverse capital) -> country -> language. Tests
whether learned geometric relations COMPOSE on real semantics = understanding. Real MiniLM, PC-scale."""
import numpy as np
from sentence_transformers import SentenceTransformer

# (country, capital, language)
DATA = [("France","Paris","French"),("Germany","Berlin","German"),("Italy","Rome","Italian"),
        ("Spain","Madrid","Spanish"),("Japan","Tokyo","Japanese"),("China","Beijing","Chinese"),
        ("Russia","Moscow","Russian"),("Greece","Athens","Greek"),("Poland","Warsaw","Polish"),
        ("Portugal","Lisbon","Portuguese"),("Turkey","Ankara","Turkish"),("Sweden","Stockholm","Swedish")]


def main():
    print("=== GEO-7: compose learned relations (capital,language) on LLM embeddings ===", flush=True)
    m = SentenceTransformer("all-MiniLM-L6-v2")
    words = sorted(set(w for row in DATA for w in row))
    E = np.array(m.encode(words, normalize_embeddings=True)); vi = {w: i for i, w in enumerate(words)}
    rng = np.random.default_rng(0)
    direct_acc, comp_acc = [], []
    for trial in range(10):
        idx = rng.permutation(len(DATA)); k = 6
        tr = [DATA[i] for i in idx[:k]]; te = [DATA[i] for i in idx[k:]]
        r_cap = np.mean([E[vi[cap]] - E[vi[co]] for co, cap, la in tr], 0)   # country->capital
        r_lan = np.mean([E[vi[la]] - E[vi[co]] for co, cap, la in tr], 0)    # country->language
        def rank1(q, true, ex):
            s = E @ (q / (np.linalg.norm(q) + 1e-9)); 
            for e in ex: s[vi[e]] = -1e9
            return words[int(np.argmax(s))] == true
        for co, cap, la in te:
            # DIRECT (if we had country->language and the country): country + r_lan
            direct_acc.append(rank1(E[vi[co]] + r_lan, la, [co, cap]))
            # COMPOSE: from CAPITAL, recover country (capital - r_cap), then +r_lan -> language. Never trained composite.
            q = (E[vi[cap]] - r_cap) + r_lan
            comp_acc.append(rank1(q, la, [co, cap]))
    print(f"  direct  (country + r_language)            hits@1 = {np.mean(direct_acc):.2f}", flush=True)
    print(f"  COMPOSE (capital - r_capital + r_language) hits@1 = {np.mean(comp_acc):.2f}  <- multi-hop, never trained", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if np.mean(comp_acc) >= 0.5:
        print("GEO-7: PASS - learned geometric relations COMPOSE on real LLM semantics: from a capital, infer the language via composition (never trained). Compositional understanding on real meaning.", flush=True)
    elif np.mean(comp_acc) >= 0.3:
        print("GEO-7: PARTIAL - composition above chance but < 0.5", flush=True)
    else:
        print("GEO-7: NULL - composition of learned relations does not hold on LLM embeddings", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()

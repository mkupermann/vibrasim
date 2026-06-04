"""GEO-10 — integration capstone: a small learned knowledge base answers MULTI-HOP compositional questions
by geometry. Learn relations (works_at: person->company; hq_in: company->city; lang_of: city->language)
few-shot, then answer 2-hop and 3-hop held-out queries by COMPOSING learned relation vectors. Measures
whether geometric composition supports relational QA / reasoning. Real MiniLM, PC-scale."""
import numpy as np
from sentence_transformers import SentenceTransformer

# chains: person -> company -> city -> language  (synthetic but embeddable real words)
PEOPLE = ["Alice","Bob","Carol","David","Eva","Frank","Grace","Henry","Iris","Jack"]
COMPANY = ["Google","Toyota","Siemens","Nokia","Ericsson","Samsung","Ferrari","Spotify","Philips","Nestle"]
CITY    = ["California","Tokyo","Munich","Helsinki","Stockholm","Seoul","Maranello","Stockholm","Amsterdam","Vevey"]
LANG    = ["English","Japanese","German","Finnish","Swedish","Korean","Italian","Swedish","Dutch","French"]
# person i works at company i, hq in city i, language lang i


def main():
    print("=== GEO-10: multi-hop relational QA via geometric composition ===", flush=True)
    m = SentenceTransformer("all-MiniLM-L6-v2")
    allw = sorted(set(PEOPLE + COMPANY + CITY + LANG))
    E = np.array(m.encode(allw, normalize_embeddings=True)); vi = {w: i for i, w in enumerate(allw)}
    n = len(PEOPLE); rng = np.random.default_rng(0)
    acc2, acc3 = [], []
    for trial in range(12):
        idx = rng.permutation(n); k = 6; tr, te = idx[:k], idx[k:]
        r_work = np.mean([E[vi[COMPANY[i]]] - E[vi[PEOPLE[i]]] for i in tr], 0)   # person->company
        r_hq   = np.mean([E[vi[CITY[i]]]    - E[vi[COMPANY[i]]] for i in tr], 0)  # company->city
        r_lang = np.mean([E[vi[LANG[i]]]    - E[vi[CITY[i]]]    for i in tr], 0)  # city->language
        def rank1(q, true, ex):
            s = E @ (q/(np.linalg.norm(q)+1e-9))
            for e in ex: s[vi[e]] = -1e9
            return allw[int(np.argmax(s))] == true
        for i in te:
            # 2-hop: which city is person i's company HQ in?  person + work + hq -> city
            q2 = E[vi[PEOPLE[i]]] + r_work + r_hq
            acc2.append(rank1(q2, CITY[i], [PEOPLE[i]]))
            # 3-hop: what language at the city of person i's company?  person + work + hq + lang -> language
            q3 = E[vi[PEOPLE[i]]] + r_work + r_hq + r_lang
            acc3.append(rank1(q3, LANG[i], [PEOPLE[i]]))
    print(f"  2-hop QA (person->company->city) hits@1 = {np.mean(acc2):.2f}", flush=True)
    print(f"  3-hop QA (->language)            hits@1 = {np.mean(acc3):.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if np.mean(acc2) >= 0.5 and np.mean(acc3) >= 0.4:
        print("GEO-10: PASS - geometric composition answers MULTI-HOP relational questions on a learned KB (2- and 3-hop, held-out). End-to-end learning+understanding via geometry on the PC.", flush=True)
    elif np.mean(acc2) >= 0.4:
        print("GEO-10: PARTIAL - 2-hop works, 3-hop degrades (error accumulates over hops)", flush=True)
    else:
        print("GEO-10: NULL - multi-hop relational QA does not hold", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()

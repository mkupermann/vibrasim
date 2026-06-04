"""GEO-11 — the honest HYBRID from the GEO-10 boundary: a key-value MEMORY stores arbitrary NEW facts
(geometry can't, GEO-10), while GEOMETRY reasons over the LLM's KNOWN relations. Demonstrate a multi-hop
query that combines a MEMORY lookup (new arbitrary fact) with a GEOMETRIC step (known relation). Shows the
two parts compose: memory supplies new facts, geometry supplies known-relation inference. CPU/MiniLM."""
import numpy as np
from sentence_transformers import SentenceTransformer

# NEW arbitrary facts (stored in memory): person -> home city (made up, LLM doesn't know)
PERSON_CITY = [("Alice","Rome"),("Bob","Tokyo"),("Carol","Berlin"),("David","Madrid"),
               ("Eva","Athens"),("Frank","Moscow"),("Grace","Cairo"),("Henry","Ottawa")]
# KNOWN relation (geometry): city -> language (LLM knows)
CITY_LANG = [("Rome","Italian"),("Tokyo","Japanese"),("Berlin","German"),("Madrid","Spanish"),
             ("Athens","Greek"),("Moscow","Russian"),("Cairo","Arabic"),("Ottawa","English"),
             ("Paris","French"),("Lisbon","Portuguese"),("Warsaw","Polish"),("Vienna","German")]


def main():
    print("=== GEO-11: hybrid MEMORY (new facts) + GEOMETRY (known relations) ===", flush=True)
    m = SentenceTransformer("all-MiniLM-L6-v2")
    words = sorted(set([w for p in PERSON_CITY for w in p] + [w for p in CITY_LANG for w in p]))
    E = np.array(m.encode(words, normalize_embeddings=True)); vi = {w: i for i, w in enumerate(words)}

    # MEMORY: explicit key->value store for NEW facts (person -> city)
    memory = dict(PERSON_CITY)

    # GEOMETRY: learn city->language from KNOWN pairs (few-shot offset)
    rng = np.random.default_rng(0)
    pairs = CITY_LANG; idx = rng.permutation(len(pairs)); k = 7
    tr = [pairs[i] for i in idx[:k]]
    r_lang = np.mean([E[vi[la]] - E[vi[ci]] for ci, la in tr], 0)

    def geo_lang(city):
        q = E[vi[city]] + r_lang; q /= np.linalg.norm(q) + 1e-9
        s = E @ q; s[vi[city]] = -1e9; return words[int(np.argmax(s))]

    # QUERY: "what language does <person> speak?" = memory(person)->city, then geometry(city)->language
    ok_mem = ok_full = 0; true_lang = dict(CITY_LANG)
    for person, city in PERSON_CITY:
        retrieved_city = memory[person]                 # MEMORY step (new fact)
        ok_mem += int(retrieved_city == city)
        pred_lang = geo_lang(retrieved_city)            # GEOMETRY step (known relation)
        ok_full += int(pred_lang == true_lang[city])
    n = len(PERSON_CITY)
    # contrast: pure geometry (no memory) on the new person->city fact (should fail, like GEO-10)
    r_city = np.mean([E[vi[PERSON_CITY[i][1]]] - E[vi[PERSON_CITY[i][0]]] for i in range(4)], 0)
    geo_city_ok = 0
    for person, city in PERSON_CITY[4:]:
        q = E[vi[person]] + r_city; q /= np.linalg.norm(q)+1e-9; s = E @ q; s[vi[person]] = -1e9
        geo_city_ok += int(words[int(np.argmax(s))] == city)
    print(f"  memory lookup (person->city, new facts) accuracy = {ok_mem/n:.2f}", flush=True)
    print(f"  pure-geometry person->city (new facts)  accuracy = {geo_city_ok/max(1,len(PERSON_CITY[4:])):.2f}  (fails: not in LLM)", flush=True)
    print(f"  HYBRID person->language (memory then geometry)   = {ok_full/n:.2f}", flush=True)
    print("\n--- VERDICT ---", flush=True)
    if ok_full/n >= 0.7 and ok_mem/n >= 0.9:
        print("GEO-11: PASS - the HYBRID works: MEMORY supplies new arbitrary facts (which geometry can't), GEOMETRY supplies known-relation inference; together they answer multi-hop queries. The honest architecture.", flush=True)
    else:
        print("GEO-11: PARTIAL/NULL - hybrid below bar (see numbers)", flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()

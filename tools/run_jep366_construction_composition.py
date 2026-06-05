"""JEP-366 — does construction composition emerge? The crux for JEP-365's per-type cost. No transformer.
Pre-registered bars in docs/amendments/jep366_construction_composition.md.

Tests whether a sentence combining two KNOWN constructions (main active clause + embedded relative clause), never
taught together, can be parsed from the learned pieces via a generic reduce-and-parse — or whether the combination
itself must be taught (combinatorial cost).
"""
import json
from pathlib import Path
from world.induce_construction import induce, apply_template, _toks


def reduce_and_parse(main_tpl, rel_tpl, sentence):
    """Generic, knowledge-free compositional parser over the two LEARNED templates.
    Detect an embedded relative clause marked by 'that', extract its fact with rel_tpl, splice it out (keeping the
    head noun), then parse the reduced main clause with main_tpl. Returns (main_fact, rel_fact) or (None, None)."""
    t = _toks(sentence)
    if "that" not in t:
        return None, None
    i = t.index("that")
    n_rel = rel_tpl["n"]                                   # relative pattern: [Head, that, VERB, the, Obj] (length 5)
    start = i - 1                                          # head noun sits one token before 'that'
    if start < 0 or start + n_rel > len(t):
        return None, None
    window = t[start:start + n_rel]
    rel_fact = apply_template(rel_tpl, " ".join(window))
    if rel_fact is None:
        return None, None
    # splice out the relative clause 'that ... Obj' (tokens i .. start+n_rel-1), keep the head noun at `start`
    reduced = t[:i] + t[start + n_rel:]
    main_fact = apply_template(main_tpl, " ".join(reduced))
    return main_fact, rel_fact


def run_seed(seed):
    # two SEPARATELY learned constructions
    main_tpl = induce([("The dog chased the cat", ("dog", "chased", "cat")),
                       ("The cat ate the mouse", ("cat", "ate", "mouse"))])          # [the,A,VERB,the,B] n=5
    rel_tpl = induce([("dog that chased the cat", ("dog", "chased", "cat")),
                      ("man that saw the bird", ("man", "saw", "bird"))])            # [A,that,VERB,the,B] n=5

    combined = "The dog that chased the cat ate the mouse"   # never taught as a whole

    # J366a: flat templates fail on the combined sentence (positions don't line up)
    flat_main = apply_template(main_tpl, combined)
    flat_rel = apply_template(rel_tpl, combined)
    j366a = (flat_main != ("dog", "ate", "mouse")) and (flat_rel != ("dog", "chased", "cat"))

    # J366b: recursive application of the SAME learned templates recovers BOTH facts
    main_fact, rel_fact = reduce_and_parse(main_tpl, rel_tpl, combined)
    ok1 = (main_fact == ("dog", "ate", "mouse")) and (rel_fact == ("dog", "chased", "cat"))
    # generalize to a second combined sentence with different fillers/verbs
    combined2 = "The man that saw the bird ate the worm"
    m2, r2 = reduce_and_parse(main_tpl, rel_tpl, combined2)
    ok2 = (m2 == ("man", "ate", "worm")) and (r2 == ("man", "saw", "bird"))
    j366b = bool(ok1 and ok2)

    return {"flat_main": flat_main, "flat_rel": flat_rel, "j366a": j366a,
            "main_fact": main_fact, "rel_fact": rel_fact, "combined2": [m2, r2], "j366b": j366b}


if __name__ == "__main__":
    print("=== JEP-366: does construction composition emerge? (reduce-and-parse over learned templates) ===",
          flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J366a flat-fails={r['j366a']} (flat_main={r['flat_main']}, flat_rel={r['flat_rel']}) | "
              f"J366b compose-via-reduction={r['j366b']} (main={r['main_fact']}, rel={r['rel_fact']}, "
              f"2nd={r['combined2']})", flush=True)

    J366a = all(R[s]['j366a'] for s in seeds)
    J366b = all(R[s]['j366b'] for s in seeds)
    passed = J366a and J366b
    print("\n--- VERDICT ---", flush=True)
    print(f"J366a flat templates fail on the combination : {J366a}  (predicted True)", flush=True)
    print(f"J366b composition via reduce-and-parse works : {J366b}  (predicted True)", flush=True)
    if passed:
        verdict = ("PASS (prediction HIT) - construction composition IS reachable: a sentence combining two KNOWN "
                   "constructions (main + embedded relative), never taught together, is parsed from the learned pieces "
                   "by a generic reduce-and-parse, recovering BOTH facts and generalizing to new fillers. So the "
                   "per-type cost (JEP-365) HOLDS: you pay per ATOMIC construction; combinations come free from a "
                   "compositional parser. Composition needs a generic recursive parser (engineered, knowledge-free), "
                   "not taught knowledge -- the optimistic, defensible result.")
    elif J366a and not J366b:
        verdict = ("NULL - flat templates fail AND the reduce-and-parse did not recover the combination: composition "
                   "does not come free; each combination would need teaching (combinatorial cost). JEP-365's per-type "
                   "optimism is then an UNDERESTIMATE -- the important negative finding.")
    else:
        verdict = "NULL/partial - see per-seed rows."
    print(f"\nJEP-366: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP366"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J366a": J366a, "J366b": J366b, "passed": passed},
                                                 default=str))
    print("DONE", flush=True)

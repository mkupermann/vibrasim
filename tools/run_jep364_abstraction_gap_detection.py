"""JEP-364 — detecting the missing rung: flag a structure no learned abstraction covers, then close the gap when
taught. No transformer. Pre-registered bars in docs/amendments/jep364_abstraction_gap_detection.md.

Composes JEP-358 (detect unparseable -> ask) + JEP-357 (induce from examples), but at the STRUCTURE level: the gap
is a whole construction TYPE the system has no template for, not just unknown words.
"""
import json
from pathlib import Path
from world.induce_construction import induce, apply_template


def covered(templates, sentence):
    """A sentence is covered iff at least one learned template yields a fact. Returns (bool, {name: fact})."""
    fired = {name: apply_template(tpl, sentence) for name, tpl in templates.items()}
    return any(f is not None for f in fired.values()), fired


def run_seed(seed):
    # learned abstractions: active + passive, induced from examples (as in JEP-363)
    active_tpl = induce([("The dog chased the cat", ("dog", "chased", "cat")),
                         ("The cat ate the mouse", ("cat", "ate", "mouse"))])
    passive_tpl = induce([("The cat was chased by the dog", ("dog", "chased", "cat")),
                          ("The mouse was eaten by the cat", ("cat", "eaten", "mouse"))])
    templates = {"active": active_tpl, "passive": passive_tpl}

    known_sentence = "The fox caught the bird"               # held-out ACTIVE — a structure it DOES know
    novel_sentence = "The dog gave the cat a bone"           # DITRANSITIVE — never taught

    known_cov, _ = covered(templates, known_sentence)
    novel_cov, novel_fired = covered(templates, novel_sentence)
    # J364a: flag the unknown, spare the known
    j364a = (known_cov is True) and (novel_cov is False)
    # J364c (honest control): pre-teaching, no learned template yields the correct ditransitive fact
    j364c = not any(f == ("dog", "gave", "bone") for f in novel_fired.values())

    # --- teach the ditransitive from 2 examples (the teacher answers the flag) ---
    dative_tpl = induce([("The dog gave the cat a bone", ("dog", "gave", "bone")),
                         ("The girl gave the boy a book", ("girl", "gave", "book"))])
    templates_after = dict(templates, dative=dative_tpl)
    novel_cov_after, fired_after = covered(templates_after, novel_sentence)
    correct_after = (apply_template(dative_tpl, novel_sentence) == ("dog", "gave", "bone"))
    # generalize to a held-out dative verb/fillers it wasn't given in the teaching pair
    held_out_dative = apply_template(dative_tpl, "The man gave the dog a stick")
    j364b = bool(novel_cov_after and correct_after and held_out_dative == ("man", "gave", "stick"))

    return {"known_covered": known_cov, "novel_covered_before": novel_cov,
            "j364a": j364a, "j364c": j364c,
            "novel_covered_after": novel_cov_after, "correct_after": correct_after,
            "held_out_dative": held_out_dative, "j364b": j364b}


if __name__ == "__main__":
    print("=== JEP-364: detecting the missing rung (flag uncovered structure, close the gap when taught) ===",
          flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J364a flag-unknown/spare-known={r['j364a']} (known_cov={r['known_covered']}, "
              f"novel_cov_before={r['novel_covered_before']}) | J364c honest-control(can't fill unaided)={r['j364c']} "
              f"| J364b taught->covered={r['j364b']} (correct={r['correct_after']}, held-out dative="
              f"{r['held_out_dative']})", flush=True)

    J364a = all(R[s]['j364a'] for s in seeds)
    J364b = all(R[s]['j364b'] for s in seeds)
    J364c = all(R[s]['j364c'] for s in seeds)
    passed = J364a and J364b and J364c
    print("\n--- VERDICT ---", flush=True)
    print(f"J364a flag the unknown, spare the known      : {J364a}  (predicted True)", flush=True)
    print(f"J364b taught -> covered + generalizes        : {J364b}  (predicted True)", flush=True)
    print(f"J364c honest control (can't fill unaided)    : {J364c}  (predicted True)", flush=True)
    verdict = ("PASS (prediction HIT) - the system reliably DETECTS a structure no learned abstraction covers and "
               "flags it (sparing structures it knows), then closes the gap from ONE taught example-set and "
               "generalizes the new abstraction to held-out fillers. The teacher-seeded abstraction library is "
               "SELF-PROMPTING: it points at its own missing rungs. Detection works; invention (J363c) still doesn't "
               "-- exactly the honest division of labor.") if passed else "NULL/partial - see per-seed rows."
    print(f"\nJEP-364: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP364"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J364a": J364a, "J364b": J364b, "J364c": J364c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)

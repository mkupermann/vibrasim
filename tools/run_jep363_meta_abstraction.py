"""JEP-363 — can it learn to abstract ALONE? (Michael's meta-abstraction question). No transformer.
Pre-registered bars in docs/amendments/jep363_meta_abstraction.md.

Three layers, tested separately:
  a) a taught abstraction (a slot in a construction) generalizes to held-out fillers.
  b) abstractions are LEARNED from examples (induced) and compose to the same relation.
  c) the strong claim: after learning active/passive, does it invent a NEW abstraction type
     (the never-taught ditransitive) on its own?  (predicted NULL.)
"""
import json, tempfile
from pathlib import Path
from world.induce_construction import induce, apply_template
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery


def run_seed(seed):
    # --- J363a: induce the PASSIVE abstraction from 2 verbs; apply to a HELD-OUT verb ---
    passive_examples = [
        ("The cat was chased by the dog", ("dog", "chased", "cat")),
        ("The mouse was eaten by the cat", ("cat", "eaten", "mouse")),
    ]
    passive_tpl = induce(passive_examples)
    held_out_passive = "The bird was caught by the fox"          # 'caught','bird','fox' never seen
    a_fact = apply_template(passive_tpl, held_out_passive)
    j363a = (a_fact == ("fox", "caught", "bird"))

    # --- J363b: independently induce the ACTIVE abstraction too; both LEARNED from examples, both compose ---
    active_examples = [
        ("The dog chased the cat", ("dog", "chased", "cat")),
        ("The cat ate the mouse", ("cat", "ate", "mouse")),
    ]
    active_tpl = induce(active_examples)
    held_out_active = "The fox caught the bird"                  # held-out verb in ACTIVE form
    b_fact = apply_template(active_tpl, held_out_active)
    # store whatever the learned templates extract, then query the relation back as a passive question
    m = SubstrateMemory(D=4096, directed=True)
    if b_fact:
        m.add_fact(*b_fact)
    bq = BrainQuery(m, seed=seed)
    passive_query_ok = bq.ask("what was the bird caught by?") == ["fox"]
    j363b = bool(b_fact == ("fox", "caught", "bird") and passive_query_ok)

    # --- J363c (the strong claim): a NEVER-TAUGHT construction type — the ditransitive/dative ---
    # "The dog gave the cat a bone" -> ideally (dog, gave, bone) + a recipient (cat). No template was induced for it.
    novel_structure = "The dog gave the cat a bone"
    learned_templates = {"passive": passive_tpl, "active": active_tpl}
    fired = {name: apply_template(tpl, novel_structure) for name, tpl in learned_templates.items()}
    # meta-abstraction would mean SOME learned template correctly yields the dative's core fact (dog, gave, bone)
    correct_dative = any(f == ("dog", "gave", "bone") for f in fired.values())
    j363c_emerged = bool(correct_dative)                          # predicted False (no meta-abstraction)

    return {"a_fact": a_fact, "j363a": j363a,
            "b_fact": b_fact, "passive_query_ok": passive_query_ok, "j363b": j363b,
            "novel_fired": {k: (list(v) if v else None) for k, v in fired.items()},
            "j363c_emerged": j363c_emerged}


if __name__ == "__main__":
    print("=== JEP-363: can it learn to abstract ALONE? (taught vs learned vs invented) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J363a taught-abstraction-generalizes={r['j363a']} (held-out passive -> {r['a_fact']}) | "
              f"J363b learned+composes={r['j363b']} (active->{r['b_fact']}, passive-query={r['passive_query_ok']}) | "
              f"J363c new-abstraction-emerged={r['j363c_emerged']} (learned templates on novel structure: "
              f"{r['novel_fired']})", flush=True)

    J363a = all(R[s]['j363a'] for s in seeds)
    J363b = all(R[s]['j363b'] for s in seeds)
    J363c_emerged = any(R[s]['j363c_emerged'] for s in seeds)     # did meta-abstraction emerge anywhere?
    print("\n--- VERDICT ---", flush=True)
    print(f"J363a taught abstraction generalizes to held-out fillers : {J363a}  (predicted True)", flush=True)
    print(f"J363b abstraction learned from examples + composes        : {J363b}  (predicted True)", flush=True)
    print(f"J363c NEW abstraction type emerged ALONE (untaught)       : {J363c_emerged}  (predicted False)", flush=True)

    # The prediction: a and b True, c NOT emerged. That pattern = honest answer to Michael.
    matches_prediction = J363a and J363b and (not J363c_emerged)
    if matches_prediction:
        verdict = ("PASS (prediction HIT) - abstractions are TEACHABLE and LEARNABLE-from-examples, and a learned "
                   "abstraction generalizes to all fillers (big leverage: teach once, cover all instances). But the "
                   "system does NOT abstract ALONE: a never-taught construction type (the ditransitive) produced no "
                   "correct structure from any learned template. It climbs the ladder of abstractions you build; it "
                   "does not invent new rungs. The honest meta-abstraction ceiling under the no-LLM rule.")
    elif J363c_emerged:
        verdict = ("SURPRISE - a learned template correctly parsed the never-taught ditransitive structure: evidence "
                   "FOR emergent meta-abstraction. Investigate before trusting (likely a slot-count coincidence).")
    else:
        verdict = "NULL/partial - see per-seed rows (a taught/learned abstraction did not generalize as predicted)."
    print(f"\nJEP-363: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP363"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J363a": J363a, "J363b": J363b,
                                                  "J363c_emerged": J363c_emerged,
                                                  "matches_prediction": matches_prediction}, default=str))
    print("DONE", flush=True)

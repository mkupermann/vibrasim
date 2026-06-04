"""
demo_geometric.py — one runnable showcase of the EQMOD-3 geometric reasoning system (GEO-1..51).

Run:  python tools/demo_geometric.py          # core (no LLM generator)
      python tools/demo_geometric.py --gen     # also show grounded generation (downloads a 0.5B model)

Showcases, on a coherent mini company KB, the whole stack:
  unified auto-dispatch (factoid/count/temporal/join/comparison), grounded abstention, contradiction
  detection, typo-robust entity resolution, updatability, and (optional) grounded generation.
All on CPU. See docs/GEOMETRIC_ANSWER.md for what it is, its boundaries, and the evidence.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from unified_reasoner import UnifiedReasoner


def line(t): print("\n" + "=" * 4 + " " + t + " " + "=" * 4, flush=True)


def main():
    use_gen = "--gen" in sys.argv
    print("EQMOD-3 geometric reasoning system — showcase\n", flush=True)
    u = UnifiedReasoner(abstain_tau=0.30)
    people = [("Alice", "Analytics"), ("Bob", "Platform"), ("Carol", "Design"),
              ("David", "Analytics"), ("Eve", "Platform"), ("Frank", "Product")]
    for p, t in people:
        u.add_person(p, t)
    for t, c in {"Analytics": "Boston", "Platform": "Denver", "Design": "Austin", "Product": "Seattle"}.items():
        u.add_team_city(t, c)
    u.add_time_fact("Alice", 2020, "Analytics"); u.add_time_fact("Alice", 2023, "Platform")
    u.r.fact_meta  # ensure built

    line("Auto-dispatch: one agent routes + answers mixed queries")
    for q in ["Which team is Carol on?", "What city does Bob live in?",
              "How many people work in Boston?", "Which team was Alice on in 2021?",
              "Who is on the same team as David?"]:
        res = u.answer(q)
        print(f"  Q: {q}\n     -> [{res['intent']}] {res['answer']}", flush=True)

    line("Grounded abstention: knows what it doesn't know")
    r = u.r
    print(f"  'Where does Alice work?'        -> {r.ask('Which team is Alice on?')['text']}", flush=True)
    out = r.ask("What is the capital of France?")
    print(f"  'capital of France?' (off-topic)-> grounded={out['grounded']} ('{out['text']}')", flush=True)

    line("Contradiction detection (same-subject fact, symbolic object compare)")
    def contradicts(subject, new_object):
        for j, mm in enumerate(r.fact_meta):
            if mm.get("subject") == subject and mm.get("kind") == "person" and mm.get("object") not in (None, new_object):
                return j
        return None
    hit = contradicts("Alice", "Design")
    msg = f"conflict at fact #{hit}: '{r.fact_texts[hit]}'" if hit is not None else "no conflict"
    print(f"  new 'Alice on Design' vs stored -> {msg}", flush=True)

    line("Typo-robust entity resolution")
    print(f"  resolve 'Alce' -> {r.resolve_entity('Alce', candidates=[p for p,_ in people])}", flush=True)
    print(f"  resolve 'Carl' -> {r.resolve_entity('Carl', candidates=[p for p,_ in people])}", flush=True)

    if use_gen:
        line("Grounded generation (0.5B LLM, follows store, abstains, faithful)")
        from grounded_qa import GroundedQA
        qa = GroundedQA(generate=True, abstain_tau=0.30)
        qa.add_fact("The capital of France is Lyon.", focus_value="France", subject="France", object="Lyon")
        print(f"  'capital of France?' (store says Lyon) -> {qa.answer('What is the capital of France?', focus='France')['answer']}", flush=True)
        print(f"  'capital of Atlantis?' (not in store)  -> {qa.answer('What is the capital of Atlantis?', focus='Atlantis')['answer']}", flush=True)

    print("\nDone. Cross-lingual: build the reasoner with", flush=True)
    print("  GeometricReasoner(model_name='paraphrase-multilingual-MiniLM-L12-v2') for German<->English.", flush=True)


if __name__ == "__main__":
    main()

"""JEP-340 — talk-to-it conversation loop: memory grows live as it learns, answers from what it knows, durable
across sessions. Headless scripted conversation. No transformer.
Pre-registered bars in docs/amendments/jep340_conversation.md.
"""
import json, tempfile, importlib
from pathlib import Path
from world.conversation import Conversation


# a scripted human-to-human dialogue: teach, ask (incl. multi-hop across separately-taught facts), teach more, ask
SCRIPT = [
    ("A poodle is a dog.", "learn"),
    ("A dog is a mammal.", "learn"),
    ("A mammal is an animal.", "learn"),
    ("Is a poodle an animal?", "Yes."),                 # multi-hop across 3 separately-taught facts
    ("A dog can bark.", "learn"),
    ("Can a poodle bark?", "Yes."),                      # inherited property, taught mid-conversation
    ("Smoking causes cancer.", "learn"),
    ("What causes cancer?", "smoking."),
    ("Is a poodle a fish?", "No."),
]


def run_seed(seed):
    d = tempfile.mkdtemp(prefix=f"talk_{seed}_")
    conv = Conversation(brain_dir=d, seed=seed)
    grew_each_teach = []; answers_ok = []; n_prev = conv.n_facts
    for (line, expect) in SCRIPT:
        resp = conv.say(line)
        if expect == "learn":
            grew_each_teach.append(conv.n_facts > n_prev)   # memory strictly grew on a teach
        else:
            answers_ok.append(resp.strip().lower() == expect.lower())
        n_prev = conv.n_facts
    conv.save()
    n_after_session1 = conv.n_facts

    # NEW SESSION: reload the durable brain, continue the conversation
    conv2 = Conversation(brain_dir=d, seed=seed)
    persisted = (conv2.n_facts == n_after_session1)
    # ask about something taught last session
    a1 = (conv2.say("Is a poodle a mammal?").strip().lower() == "yes.")
    # teach something new this session, memory grows again
    before = conv2.n_facts
    conv2.say("A salmon is a fish.")
    grew_session2 = conv2.n_facts > before
    a2 = (conv2.say("Is a salmon a fish?").strip().lower() == "yes.")

    return {"all_teaches_grew": all(grew_each_teach), "answer_acc": round(sum(answers_ok) / len(answers_ok), 3),
            "persisted_across_session": bool(persisted), "prior_session_recall": bool(a1),
            "grew_session2": bool(grew_session2), "new_fact_answered": bool(a2), "n_facts": n_after_session1}


if __name__ == "__main__":
    print("=== JEP-340: talk-to-it conversation (memory grows live, durable) ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: answers={r['answer_acc']} | every teach grew memory={r['all_teaches_grew']} "
              f"({r['n_facts']} facts) | persisted={r['persisted_across_session']} prior-recall="
              f"{r['prior_session_recall']} | grew next session={r['grew_session2']} answered new="
              f"{r['new_fact_answered']}", flush=True)
    try:
        import world.conversation, tools.talk; importlib.reload(tools.talk); tool_ok = True
    except Exception as ex:
        tool_ok = False; print("  import:", ex, flush=True)

    J340a = all(R[s]['answer_acc'] >= 0.95 and R[s]['prior_session_recall'] and R[s]['new_fact_answered'] for s in seeds)
    J340b = all(R[s]['all_teaches_grew'] and R[s]['persisted_across_session'] and R[s]['grew_session2'] for s in seeds)
    J340c = tool_ok
    passed = J340a and J340b and J340c
    print("\n--- VERDICT ---", flush=True)
    print(f"J340a learn-then-answer in dialogue + across sessions (>=.95): {J340a}", flush=True)
    print(f"J340b memory grows live every teach + persists                : {J340b}", flush=True)
    print(f"J340c conversation tool imports                               : {J340c}", flush=True)
    verdict = ("PASS - you can talk to it: statements teach (the durable memory grows live), questions are answered "
               "from what it knows, and the memory persists and keeps growing across sessions") if passed else "NULL/partial"
    print(f"\nJEP-340: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP340"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "J340a": J340a, "J340b": J340b, "J340c": J340c,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)

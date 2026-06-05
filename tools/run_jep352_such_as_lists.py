"""JEP-352 — 'such as' list -> is-a extraction. No transformer.
Pre-registered bars in docs/amendments/jep352_such_as_lists.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation
from world.brain_query import BrainQuery


def run_seed(seed):
    c = Conversation(brain_dir=tempfile.mkdtemp(prefix=f"such_{seed}_"), seed=seed)
    c._learn_one("Mammals such as dogs and cats are warm-blooded.")
    c._learn_one("Pets such as dogs, cats, and birds are common.")
    bq = BrainQuery(c.sm, seed=seed)
    checks = {
        "dog_mammal": bq.is_a("dog", "mammal") is True,
        "cat_mammal": bq.is_a("cat", "mammal") is True,
        "dog_pet": bq.is_a("dog", "pet") is True,
        "cat_pet": bq.is_a("cat", "pet") is True,
        "bird_pet": bq.is_a("bird", "pet") is True,
    }
    return {"acc": round(sum(checks.values()) / len(checks), 3), "checks": {k: bool(v) for k, v in checks.items()}}


def regression(repo):
    outs = {}
    for name in ["run_jep347_realistic_prose_coverage", "run_jep349_more_prose_forms", "run_jep350_realistic_article_endtoend"]:
        r = subprocess.run([sys.executable, f"tools/{name}.py"], capture_output=True, text=True,
                           env={**os.environ, "PYTHONPATH": repo})
        num = name.split("jep")[1][:3]
        outs[num] = f"JEP-{num}: PASS" in r.stdout
    g = subprocess.run([sys.executable, "-m", "pytest", "tests/test_conversation.py", "-q"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    outs["gate"] = "passed" in g.stdout and "failed" not in g.stdout
    return outs


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-352: 'such as' list -> is-a extraction ===", flush=True)
    seeds = [0, 7]; R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        print(f"  seed {s}: acc={R[s]['acc']} | {R[s]['checks']}", flush=True)
    reg = regression(repo)
    print(f"  regression: {reg}", flush=True)
    J352a = all(R[s]['acc'] >= 1.0 for s in seeds)
    J352b = all(reg.values())
    passed = J352a and J352b
    print("\n--- VERDICT ---", flush=True)
    print(f"J352a such-as extraction (Oxford comma incl): {J352a}", flush=True)
    print(f"J352b no regression                          : {J352b}", flush=True)
    verdict = ("PASS - 'such as' lists extract is-a facts (incl Oxford comma), no regression") if passed else "NULL/partial"
    print(f"\nJEP-352: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP352"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "reg": reg, "J352a": J352a, "J352b": J352b,
                                                  "passed": passed}, default=str))
    print("DONE", flush=True)

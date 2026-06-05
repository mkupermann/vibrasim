"""JEP-425 — energy clouds (Michael's model): affective VALENCE (bright/dark) + experience STRENGTHENING (Hebbian).
Established concepts (affect/somatic-marker; Hebb 1949), named as such — NOT new science. No transformer.
Pre-registered bars in docs/amendments/jep425_energy_clouds.md.
"""
import json, tempfile, subprocess, sys, os
from pathlib import Path
from world.conversation import Conversation


def run_seed(seed):
    brain = tempfile.mkdtemp(prefix=f"j425_{seed}_")
    c = Conversation(brain_dir=brain, seed=seed)
    c.read_text("A hero is good. A hero is brave. A villain is evil. A villain is cruel. A saint is kind.")
    # J425a: valence (bright/dark cloud)
    hero_good = "yes" in c.say("is a hero good?").strip().lower()
    villain_good = "yes" not in c.say("is a villain good?").strip().lower()
    villain_bad = "yes" in c.say("is a villain bad?").strip().lower()
    hero_energy = "bright" in c.say("what is the energy of a hero?").strip().lower()
    villain_energy = "dark" in c.say("what is the energy of a villain?").strip().lower()
    j425a = all([hero_good, villain_good, villain_bad, hero_energy, villain_energy])

    # J425b: experience strengthens the connection (Hebbian)
    for _ in range(5):
        c.read_text("Michael likes coffee.")   # SVO -> extra-routed -> strengthens on re-experience
    strengthened = c.sm.strength.get(("michael", "likes", "coffee"), 0)
    j425b = strengthened >= 5

    # J425c: valence persists across save/load
    c.save()
    reloaded = Conversation(brain_dir=brain, seed=seed)
    persists = "yes" in reloaded.say("is a hero good?").strip().lower()
    j425c = persists
    return {"j425a": bool(j425a), "hero_good": hero_good, "villain_bad": villain_bad, "hero_energy": hero_energy,
            "strength": strengthened, "j425b": bool(j425b), "persists": bool(persists), "j425c": bool(j425c)}


def suite(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "not slow", "tests/test_conversation.py"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": repo})
    last = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    return ("failed" not in r.stdout and "error" not in r.stdout.lower().split("warnings")[0]), last


if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("=== JEP-425: energy clouds (valence + experience strengthening) ===", flush=True)
    seeds = [0, 7]
    R = {s: run_seed(s) for s in seeds}
    for s in seeds:
        r = R[s]
        print(f"  seed {s}: J425a valence={r['j425a']} (hero-good={r['hero_good']},villain-bad={r['villain_bad']},"
              f"energy={r['hero_energy']}) | J425b strengthen={r['j425b']} (strength={r['strength']}) | "
              f"persists={r['persists']} (J425c={r['j425c']})", flush=True)
    gate_ok, line = suite(repo)
    print(f"  conversation suite: {gate_ok} ({line})", flush=True)
    J425a = all(R[s]['j425a'] for s in seeds)
    J425b = all(R[s]['j425b'] for s in seeds)
    J425c = all(R[s]['j425c'] for s in seeds) and gate_ok
    passed = J425a and J425b and J425c
    print("\n--- VERDICT ---", flush=True)
    print(f"J425a valence (bright/dark cloud)   : {J425a}", flush=True)
    print(f"J425b experience strengthens (Hebb) : {J425b}", flush=True)
    print(f"J425c persists + suite              : {J425c}", flush=True)
    verdict = ("PASS - a first build of Michael's energy-cloud model: each concept carries an affective VALENCE (hero "
               "-> bright/positive, villain -> dark/negative), queryable; and repeated experience STRENGTHENS the "
               "connection (Hebbian count). Established concepts (affect/somatic-marker; Hebb 1949) -- NOT new science "
               "-- but a concrete, brain-like extension on the substrate's distributed energy clouds. Persists, suite "
               "green.") if passed else "NULL/partial - see rows (a bar missed; report, do not retune)."
    print(f"\nJEP-425: {verdict}", flush=True)
    out = Path.home() / ".eqmod" / "bet" / "JEP425"; out.mkdir(parents=True, exist_ok=True)
    (out / "result.json").write_text(json.dumps({"rows": R, "gate": gate_ok, "J425a": J425a, "J425b": J425b,
                                                  "J425c": J425c, "passed": passed}, default=str))
    print("DONE", flush=True)

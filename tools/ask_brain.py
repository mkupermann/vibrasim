"""ask_brain — ask the durable substrate brain questions from the command line.

Usage:
  .venv\\Scripts\\python.exe tools\\ask_brain.py "is a poodle an animal?"
  .venv\\Scripts\\python.exe tools\\ask_brain.py --dir <brain_folder> "what causes cancer?"
With no question, runs an interactive prompt. Loads the persisted brain (default ~/.eqmod/brain/teach_gui).
No transformer, no pretrained model.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from world.substrate_memory import SubstrateMemory
from world.brain_query import BrainQuery

DEFAULT = os.path.join(os.path.expanduser("~"), ".eqmod", "brain", "teach_gui")


def main(argv):
    brain_dir = DEFAULT
    qs = []
    i = 0
    while i < len(argv):
        if argv[i] == "--dir":
            brain_dir = argv[i + 1]; i += 2
        else:
            qs.append(argv[i]); i += 1
    if not os.path.exists(os.path.join(brain_dir, "meta.json")):
        print(f"No brain found at {brain_dir}. Teach one first (tools/teach_gui.py) or pass --dir.")
        return
    bq = BrainQuery(SubstrateMemory.load(brain_dir))
    if qs:
        for q in qs:
            print(f"Q: {q}\nA: {bq.ask(q)}")
        return
    print("Ask the brain (blank line to quit):")
    while True:
        try:
            q = input("> ").strip()
        except EOFError:
            break
        if not q:
            break
        print(bq.ask(q))


if __name__ == "__main__":
    main(sys.argv[1:])

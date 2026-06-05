"""talk — have a conversation with the substrate. It learns from your statements (the durable memory GROWS) and
answers your questions, all over the persistent VSA store. No transformer, no pretrained model.

Run:  .venv\\Scripts\\python.exe tools\\talk.py            (uses ~/.eqmod/brain/talk, persists across sessions)
      .venv\\Scripts\\python.exe tools\\talk.py --dir <folder>

Examples to type:
  A poodle is a dog.        -> Got it - I learned ... facts.
  A dog is a mammal.
  Is a poodle a mammal?     -> Yes.
  A dog can bark.
  Can a poodle bark?        -> Yes.
Type 'quit' (or empty line) to save and exit.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from world.conversation import Conversation


def main(argv):
    brain_dir = None
    if "--dir" in argv:
        brain_dir = argv[argv.index("--dir") + 1]
    conv = Conversation(brain_dir=brain_dir)
    print(f"Talking to the substrate (it knows {conv.n_facts} facts so far). "
          f"Say things to teach it; ask questions. Blank line or 'quit' to save & exit.")
    while True:
        try:
            line = input("you> ").strip()
        except EOFError:
            break
        if not line or line.lower() in ("quit", "exit", "bye"):
            break
        print("it > " + conv.say(line))
    conv.save()
    print(f"(saved — it now durably knows {conv.n_facts} facts)")


if __name__ == "__main__":
    main(sys.argv[1:])

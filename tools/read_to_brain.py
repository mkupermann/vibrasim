"""read_to_brain — feed a text file (or pasted text) into the durable substrate brain. It reads the document,
learns every parseable sentence, and the memory GROWS and PERSISTS — so over days you can keep reading more into the
same brain and then discuss it (tools/talk.py). No transformer, no pretrained model.

Run:  .venv\\Scripts\\python.exe tools\\read_to_brain.py path\\to\\text.txt
      .venv\\Scripts\\python.exe tools\\read_to_brain.py --dir <brainfolder> path\\to\\text.txt
Then talk about it:  .venv\\Scripts\\python.exe tools\\talk.py --dir <brainfolder>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from world.conversation import Conversation


def main(argv):
    brain_dir = None
    paths = []
    i = 0
    while i < len(argv):
        if argv[i] == "--dir":
            brain_dir = argv[i + 1]; i += 2
        else:
            paths.append(argv[i]); i += 1
    if not paths:
        print("usage: read_to_brain.py [--dir <folder>] <text-file> [more files...]")
        return
    conv = Conversation(brain_dir=brain_dir)
    print(f"Reading into the brain (it knew {conv.n_facts} facts before)...")
    for p in paths:
        try:
            text = open(p, encoding="utf-8", errors="ignore").read()
        except OSError as ex:
            print(f"  (could not read {p}: {ex})"); continue
        r = conv.read_text(text)
        print(f"  {p}: read {r['sentences']} sentences -> learned {r['facts_learned']} new facts "
              f"(now {r['total_facts']} facts, {r['concepts']} concepts).")
    conv.save()
    g = conv.gaps()
    if g:
        print("After reading, a few things aren't clear to me yet: " +
              ", ".join(f"what is a {c}?" for c in g[:6]))
    print(f"(saved — the brain now durably knows {conv.n_facts} facts. Talk about it with tools/talk.py)")


if __name__ == "__main__":
    main(sys.argv[1:])

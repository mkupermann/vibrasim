"""Interactive CLI for the substrate knowledge system (NO LLM, NO transformer).

Usage:
  python -m tools.ask                      # demo corpus, then ask questions
  python -m tools.ask path\\to\\source.txt  # ingest one or more text files first

Commands inside the prompt:
  :learn N     mark passage #N (from the last answer's shortlist) as the correct one
  :read FILE   ingest another text file into the knowledge base
  :facts       show how many passages are known
  :quit        exit
"""
import sys
from pathlib import Path
from world.knowledge import KnowledgeBase

DEMO = """
The Earth orbits the Sun once every 365.25 days. The Moon orbits the Earth and causes
the ocean tides. Water boils at 100 degrees Celsius at sea level. Photosynthesis lets
plants convert sunlight into chemical energy. Gravity pulls objects toward the centre
of the Earth. Penicillin was the first antibiotic, discovered by Alexander Fleming.
DNA carries the genetic instructions for living organisms. Earthquakes are caused by
the sudden movement of tectonic plates. Vaccines train the immune system to fight
specific diseases. The internet connects computers around the world to share data.
"""


def main(argv):
    kb = KnowledgeBase()
    files = [a for a in argv if not a.startswith(":")]
    if files:
        for f in files:
            txt = Path(f).read_text(encoding="utf-8", errors="replace")
            n = kb.ingest(txt)
            print(f"ingested {n} passages from {f}")
    else:
        kb.ingest(DEMO)
        print(f"ingested demo corpus ({len(kb.passages)} passages). Ask me something.")

    last = []
    while True:
        try:
            q = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q:
            continue
        if q in (":quit", ":q", "exit"):
            break
        if q == ":facts":
            print(f"{len(kb.passages)} passages known")
            continue
        if q.startswith(":read "):
            f = q[6:].strip()
            try:
                n = kb.ingest(Path(f).read_text(encoding="utf-8", errors="replace"))
                print(f"ingested {n} passages from {f}")
            except OSError as e:
                print(f"could not read {f}: {e}")
            continue
        if q.startswith(":learn "):
            try:
                n = int(q.split()[1])
                if last:
                    kb.learn(last_query, n)
                    print(f"learned: question -> passage #{n}")
            except (ValueError, IndexError):
                print("usage: :learn N")
            continue
        last = kb.query(q, k=3)
        last_query = q
        if not last:
            print("(no knowledge yet — ingest a source first)")
            continue
        print(f"A: {last[0][1]}")
        if len(last) > 1:
            print("  other candidates:")
            for i, txt, sc in last:
                print(f"   [{i}] ({sc:+.2f}) {txt}")


if __name__ == "__main__":
    main(sys.argv[1:])

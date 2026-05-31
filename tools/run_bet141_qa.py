"""BET-141 — source ingestion + written QA + online learning (Versuchsreihe 1)."""
import json
from pathlib import Path
import numpy as np
from world.knowledge import KnowledgeBase

CORPUS = """
The Earth orbits the Sun once every 365.25 days.
The Moon orbits the Earth and causes the ocean tides.
Water boils at 100 degrees Celsius at sea level pressure.
Water freezes into ice at 0 degrees Celsius.
The human heart pumps blood through the circulatory system.
The lungs take in oxygen and release carbon dioxide when we breathe.
Photosynthesis lets plants convert sunlight into chemical energy.
Chlorophyll gives plants their green colour and absorbs light.
The Great Wall of China was built to defend against northern invasions.
The Pyramids of Giza were constructed as tombs for Egyptian pharaohs.
Mount Everest is the highest mountain above sea level on Earth.
The Pacific is the largest and deepest of the world's oceans.
The Amazon is the largest tropical rainforest on the planet.
The Nile is one of the longest rivers and flows through Egypt.
Light travels at about 300 thousand kilometres per second in a vacuum.
Sound travels much slower than light and needs a medium to move.
Gravity is the force that pulls objects toward the centre of the Earth.
Electricity is the flow of electric charge through a conductor.
A triangle has three sides and its angles add up to 180 degrees.
A circle is the set of points at an equal distance from a centre.
The French Revolution began in 1789 and overthrew the monarchy.
World War Two ended in 1945 after several years of global conflict.
Penicillin was the first antibiotic and was discovered by Alexander Fleming.
DNA carries the genetic instructions for living organisms.
The brain controls the body and is the centre of the nervous system.
Bees collect nectar from flowers and produce honey in their hives.
Spiders spin webs from silk to catch insects for food.
Volcanoes erupt when molten rock rises through the Earth's crust.
Earthquakes are caused by the sudden movement of tectonic plates.
Rain forms when water vapour in clouds condenses and falls.
The Sahara is the largest hot desert located in northern Africa.
Antarctica is the coldest continent and is covered in thick ice.
Iron rusts when it reacts with oxygen and water over time.
Salt dissolves easily in water to form a clear solution.
The speed of a car is measured in kilometres per hour.
A computer stores information using binary digits called bits.
The internet connects computers around the world to share data.
Vaccines train the immune system to fight specific diseases.
Trees absorb carbon dioxide and release oxygen into the air.
The stomach digests food using strong acids and enzymes.
"""

# (paraphrased question, index of the answer sentence in CORPUS order)
QA = [
    ("How long does the Earth take to go around the Sun?", 0),
    ("What causes the tides in the ocean?", 1),
    ("At what temperature does water start to boil?", 2),
    ("When does water turn into ice?", 3),
    ("What organ moves blood around the body?", 4),
    ("How do plants turn sunlight into energy?", 6),
    ("Why are plants green?", 7),
    ("Which mountain is the tallest on Earth?", 10),
    ("What is the biggest ocean?", 11),
    ("How fast does light move in empty space?", 14),
    ("What force pulls things down to the ground?", 16),
    ("When did the French Revolution start?", 20),
    ("Who discovered the first antibiotic?", 22),
    ("What molecule holds genetic information?", 23),
    ("How do bees make honey?", 25),
    ("What makes earthquakes happen?", 28),
    ("Where is the largest hot desert?", 30),
    ("Why does iron rust?", 32),
    ("How does a computer store data?", 35),
    ("What do vaccines do to the immune system?", 37),
]

if __name__ == "__main__":
    print("=== BET-141: ingest sources + written QA + online learning ===", flush=True)
    kb = KnowledgeBase(dim=4096)
    kb.ingest(CORPUS)
    print(f"  ingested {len(kb.passages)} passages", flush=True)

    def evaluate(items):
        t1 = t3 = 0
        for q, ans in items:
            res = kb.query(q, k=3)
            idxs = [i for i, _, _ in res]
            if idxs and idxs[0] == ans: t1 += 1
            if ans in idxs: t3 += 1
        return t1/len(items), t3/len(items)

    top1, top3 = evaluate(QA)
    print(f"  top-1 accuracy: {top1:.3f}", flush=True)
    print(f"  top-3 accuracy: {top3:.3f}", flush=True)

    # online learning: feedback on first 10, measure their top-1 before/after
    feed = QA[:10]; held = QA[10:]
    pre_t1, _ = evaluate(feed)
    for q, ans in feed:
        kb.learn(q, ans)
    post_t1, _ = evaluate(feed)
    held_t1, _ = evaluate(held)
    print(f"  fed-back top-1 before/after feedback: {pre_t1:.3f} -> {post_t1:.3f}", flush=True)
    print(f"  held-out top-1 (unchanged set): {held_t1:.3f}", flush=True)

    # show a couple of sample answers
    for q, _ in QA[:3]:
        print(f"   Q: {q}\n   A: {kb.answer(q)}", flush=True)

    T141a = top1 >= 0.70
    T141b = top3 >= 0.85
    T141c = top1 > 0.20
    T141d = post_t1 >= 0.90
    passed = T141a and T141b and T141c and T141d
    print("\n--- VERDICT ---", flush=True)
    print(f"T141a top-1 >=0.70 : {T141a} ({top1:.3f})", flush=True)
    print(f"T141b top-3 >=0.85 : {T141b} ({top3:.3f})", flush=True)
    print(f"T141c beats chance : {T141c} ({top1:.3f} vs ~0.025)", flush=True)
    print(f"T141d feedback>=0.90: {T141d} ({post_t1:.3f})", flush=True)
    print(f"\nBET-141: {'PASS - substrate retrieval system answers written questions from sources and learns online' if passed else 'NULL/partial'}", flush=True)
    out = Path.home()/'.eqmod'/'bet'/'BET-141'; out.mkdir(parents=True, exist_ok=True)
    (out/'result.json').write_text(json.dumps(
        {"top1":top1,"top3":top3,"post_t1":post_t1,"held_t1":held_t1,"passed":passed}, indent=2))
    print("DONE", flush=True)

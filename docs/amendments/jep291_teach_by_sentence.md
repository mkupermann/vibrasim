# JEP-291 — teaching by SENTENCE (per Michael: "later when it can understand more I answer with sentences")

Pre-registered 2026-06-05 (BEFORE the run). The teacher's answer becomes a full SENTENCE that does two jobs: NAMES
the perceived thing ('This is a dog') -> grounds the percept to that symbol, AND TEACHES facts ('A dog is a mammal')
-> read() into the engine. One sentence binds perception to knowledge. No transformer / no pretrained model.

## Bars (locked pre-run)
| ID | Criterion | Bar |
|----|-----------|-----|
| J291a | sentence GROUNDS the percept | the first clause's noun grounds the image to that symbol (all classes, both seeds) |
| J291b | sentence TEACHES facts | the sentence's facts enter the engine (is_a(shirt,clothing), is_a(sandal,footwear)) |
| J291c | perceive+reason from sentence-teaching | a held-out image is perceived AND reasoned ('is this footwear?') >= 0.85, both seeds |
| J291d | GUI sentence path | tools/teach_gui.py accepts a sentence answer (grounds + reads), self-bootstrapping for direct launch |

## Prediction (locked BEFORE run) [predict-calibrate]
🔮 PASS: parse 'This is a X' -> ground percept as X; read() the whole sentence -> facts; then perceive+reason ~0.9.
The teacher's sentence unifies grounding + knowledge -- Michael's 'answer with sentences'. Established (template
grounding + read() parsing).

## RESULT (2026-06-05): PASS — one sentence both names the percept and teaches its facts
| seed | perceive+reason acc | grounded the percept | taught the facts |
|------|---------------------|----------------------|------------------|
| 42 | 0.965 | True | True |
| 7  | 0.94 | True | True |

- **J291a ✓ / J291b ✓** — 'This is a shirt. A shirt is clothing.' grounds the image to 'shirt' AND teaches
  shirt->clothing; the engine then knows both the NAME of what it sees and a FACT about it, from one sentence.
- **J291c ✓** — perceive a held-out image -> reason 'is this footwear?' at 0.94-0.97, using ONLY what the teacher's
  sentences grounded + taught.
- **J291d ✓** — tools/teach_gui.py now accepts a SENTENCE answer (parses 'This is an A. An A is a letter.' -> grounds
  the percept + reads the facts via an attached UnderstandingEngine) and self-bootstraps sys.path so it launches
  directly: `.venv\Scripts\python.exe tools\teach_gui.py`.

**FINDING (per Michael):** the teaching loop now accepts SENTENCES, not just correct/incorrect -- one sentence binds
PERCEPTION (name the thing) to KNOWLEDGE (facts about it via read()), so the engine perceives a new image and reasons
about it from what you SAID. This connects the slow teacher loop (JEP-287) to the prose engine end-to-end, the
'answer with sentences' level Michael described. predict-calibrate HIT (tally 170/206). Harness
tools/run_jep291_teach_by_sentence.py; GUI tools/teach_gui.py. Established (template grounding + read() parsing +
prototype perception), named; no novelty -- the value is the sentence-driven perceive+learn+reason loop with a teacher.

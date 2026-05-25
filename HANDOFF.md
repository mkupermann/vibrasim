# EQMOD — Mac→Windows Handoff (Session 2026-05-23..25)

Dokument für Claude-on-Windows zum Wiederaufnehmen der Arbeit. Geschrieben
von Claude-on-Mac am Ende der 48h-Autonomous-Session.

---

## Wer du gerade bist

Du bist Claude Code (oder Claude App + Cowork) auf Michael Kupermanns
Windows-11-Rechner mit 64GB RAM und starker GPU. Das Projekt EQMOD wurde
auf einem macOS-Mac-arm64 mit 16GB RAM begonnen. Diese Übergabe transferiert
den Stand zu dir.

**Wichtiger Identitäts-Hinweis:** der User ist Michael Kupermann
(michael@kupermann.com), 30 Jahre Software-Architektur, €1300/Tag,
extrem terse Kommunikation. Nicht-floskelhaft, deutsch beim Duzen.
Push-back bei Trade-offs. Keine Markdown-Dekoration über das strukturell
Notwendige. Reagiert oft mit Einzelbuchstaben "a/b/c". Heavy reasoning
zwischen seinen kurzen Antworten.

Volltext seines globalen Profils in `/Users/mkupermann/.claude/CLAUDE.md`
auf dem Mac. Falls du nicht in dieser Rolle bist (z.B. Cowork-Connector
ohne Profile-Sync), trotzdem den terse-Stil beibehalten.

---

## Was steht (Stand main HEAD `5b3b614`, BET-080 läuft noch)

### Phase A — Brain-faithful Brian2 Substrate-Beweis (DONE)

Pre-LLM, brain-faithful Spiking-Neuronen + STDP via Brian2-Library.
200 Neuronen, 4 von 7 Stufen erreicht:

| Stufe | BET | Verdict | Kernzahl |
|---|---|---|---|
| 1 Binär-Diskrimination EN-vs-WN | 065 | PASS | acc 0.98 |
| 2 Multi-Klasse | 066 | hard-cap | audio-loading infra |
| 3 Temporale Sequenz | 070 | PASS | acc 0.70 |
| 4 Generation (top-down) | 069 | PASS | cos 0.91, KL 0.24 |
| 5 R-STDP / Agency | 067 | NULL | acc 0.43 |
| 6 Closed-Loop Sensorimotor | 071 | NULL | motor selectivity 1.29 |
| 5 R-STDP+critic Frémaux-Gerstner | 072 | NULL | acc 0.52 |
| 7 Hierarchie 2-Layer | 068 | PASS | L2 acc 0.83, KL ampl 10× |

Drei sequentielle NULLs auf demselben Mechanismus (Credit-Assignment)
sind kein retry-bis-PASS, sondern Befund: unsupervised STDP allein
gibt keine class-selective motor-Verdrahtung.

### Phase B — Mac-Skalierung + Cortical-Density (DONE / läuft)

| BET | Was | Verdict | Kernzahl |
|---|---|---|---|
| 073 | cython@1K | NULL informativ | speedup 0.91× (numpy fine at 1K) |
| 074 | 10K sparse 5% | PASS | speedup 2.12× |
| 075 | 100K sparse 0.5% | PASS | 5.4GB peak |
| 076 | 1M sparse 0.003% | PASS | 4.3GB peak — 1M auf Mac möglich |
| 077 | Cortical 25K 4-Layer | NULL by bar | L23 0.94, L5/L6 collapse |
| 077b | + Turrigiano homeostasis | NULL by bar | L23 1.00, L5/L6 collapse |
| 077c | + bounded recurrent | NULL by sat | **L5 0.84, KL ampl 12×, alle 4 layer aktiv** |
| 078 | Checkpoint/Resume | PASS | bit-perfect (0.0 diff) |
| 079 | 4h continuous training | PASS | L5 0.775 → 0.875 (+10%), L6 +17.5% |
| 080 | **12h continuous (läuft)** | h10 zur Schreibzeit, L5 **0.975** | substrate lernt sustained |

Wichtigste empirische Befunde:
- Cortical-density (5000 syn/neuron) limitiert Mac auf ~30K Neuronen
- 1M Neuronen mit degenerate-sparse (30 syn/neuron) möglich, aber nicht brain-faithful
- Substrate **verbessert** sich messbar über continuous training (Phase-B-Hypothese bestätigt)

### Phase C — Multimodal (NICHT gestartet, dokumentiert)

`docs/phase_c_multimodal_plan.md`: Vision + Touch + Reading.
Trigger war BET-080 PASS. **Aktuell pausiert** wegen wichtigerer
User-Direktive (siehe unten).

---

## Aktive User-Direktive (höchste Priorität)

### Ziel: Audio-Dialog mit englischem Grundwortschatz

User wants:
- Substrate versteht englischen Grundwortschatz aus Audio
- Substrate antwortet mit Text (TTS außerhalb des Substrats macht Sprach-Output)
- **Critical**: substrate muss gehörtes "and" mit Symbol "and" verknüpfen
- Realtime nicht relevant
- 3-10 Wörter brain-faithful gelingen → User verspricht Hardware-Upgrade

### Harte Constraint die heute geschärft wurde

User hat klargestellt: **"Labels sind LLM"**. Heißt:

- KEIN human labeling von Audio-Segments (kein "ich höre mir das an und tippe 'and'")
- KEIN forced aligner (auch HMM-GMM nicht — pre-trained ist pre-trained)
- KEIN Whisper / Wav2Vec / Vosk / irgendwas pre-trained
- KEIN externer Segmentierer (Energy-VAD ist auch verdächtig — Segmentierung muss emergent sein)

**Das heißt für BET-081ff:**
- Substrate hört kontinuierlichen ungeschnittenen Audio-Stream
- L23/L5 entwickelt autonom Cluster für wiederkehrende Akustik-Patterns via STDP
- Wort-Detektoren emergieren ohne Label
- Validation: post-hoc Probing (nimm jedes L5-Neuron, schau auf welche Audio-Snippets es maximal feuert)
- Cross-modal Binding später: simultane Audio+visuell-gerenderte-Text-Präsentation
  via Vision-Cortex → STDP koppelt automatisch

### Anti-Direktive aus heutigem Chat

Ich (Claude-on-Mac) hatte zwei Shortcut-Pipelines gebaut:
- `tools/word_segment_extractor.py` — Energy-VAD
- `tools/word_segment_cluster.py` — k-means + listen+label CLI

User hat das als "supervised ML mit Spiking-Lackierung" abgelehnt.
Die Tools sind committed (5b3b614) aber **nicht für BET-081 zu verwenden**.
Sie sind höchstens nützlich für post-hoc PROBING (kontinuierliches
Substrate-Training, dann nachträgliches "Welche Cluster sind für was?").

---

## Was du als Nächstes tust (auf Windows)

### Schritt 0: Hardware-Inventur

Frag User welche GPU. Wenn NVIDIA: `pip install brian2cuda`. Wenn AMD:
brian2cuda geht nicht, dann CuPy + Brian2 numpy oder cython fallback.
64GB RAM ist die Game-Changer — cortical-density 5000 syn/neuron bei
~100K Neuronen wird machbar (vs Mac 30K).

### Schritt 1: Repo-Sync

```powershell
cd C:\Users\<user>\Documents
git clone https://github.com/mkupermann/vibrasim.git EQMOD
cd EQMOD
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt    # falls vorhanden, sonst:
pip install brian2 numpy pytest pyvista  # plus dependencies aus pyproject.toml
```

Nimm Python 3.13 wenn verfügbar (matched Mac), 3.11+ ok.

### Schritt 2: Datentransfer

Vom Mac kommt ein tar/zip-Bundle mit `~/.eqmod/`. Inhalt:
- `training/EN/` — Audio-Files + manifest.json + extracted segments
- `bet/BET-077c/`, `bet/BET-078/`, `bet/BET-079/`, `bet/BET-080/` — Results + Checkpoints
- `autopilot/notify_config.json` — Telegram bot token (**SENSITIVE**, separat handhaben)

Auf Windows entpacken nach `C:\Users\<user>\.eqmod\` (Python `Path.home()`
löst sich plattform-gerecht auf).

**Path-Patch nötig** im manifest.json (Mac-Pfade auf Windows-Pfade):
```powershell
python -c "import json,pathlib; p=pathlib.Path.home()/'.eqmod/training/EN/manifest.json'; m=json.loads(p.read_text()); home_str=str(pathlib.Path.home()).replace('\\','/'); [f.__setitem__('path', f['path'].replace('/Users/mkupermann', home_str)) for s in m['stages'].values() for f in s.get('files',[])]; p.write_text(json.dumps(m, indent=2))"
```

### Schritt 3: Sanity-Check (5-10min)

Re-run einen schnellen passing BET um zu verifizieren dass alles
funktioniert:
```powershell
pytest tests/bet/test_bet_078_checkpoint_resume.py -xvs
```
Erwartung: PASSED in <1min mit `max_w_roundtrip_diff: 0.0`.

Wenn das geht, größerer Sanity:
```powershell
pytest tests/bet/test_bet_065_brian2_snn.py -xvs   # falls Test-File existiert
# alternativ: tests/bet/test_bet_074_brian2_10k_sparse.py — ~30s
```

### Schritt 4: Auf Phase C umschwenken (User-Direktive aktiv)

User will brain-faithful Audio→Text-Binding mit 3-10 Wörtern. Nächster
BET ist **BET-081**, designed als:

- 8K-Neuron Audio-Cortex (4 Layer, cortical-density 5000 syn/neuron — passt
  mit 64GB GPU/CPU)
- Input: **kontinuierlicher** ungeschnittener LibriVox-Stream (Pride and
  Prejudice 82min, später LibriSpeech 1000h)
- STDP läuft kontinuierlich, KEINE Pre-Segmentierung
- Eval-Probing: nach N Stunden Training nimm L5-Neuronen, schau ihre
  preferred audio context (Auto-encoder-style reconstruct from spike pattern,
  oder einfacher: cluster L5-Spike-Pattern dann pro Cluster die durchschnittliche
  audio-feature)
- Bar: mindestens 3 distinkte L5-Cluster die auf verschiedene Akustik-Motive
  reagieren (Probing acc > random by margin)

GPU-relevant: brian2cuda für 10-100× speedup. Bei NVIDIA-RTX-Klasse-GPU
wird Echtzeit-Sim für 8K-Neuronen möglich, was die ganze Geschichte
verändert.

---

## Wichtige Pfade & Files

| Was | Pfad |
|---|---|
| CLAUDE.md (Projekt) | `CLAUDE.md` |
| Logbuch | `LOGBOOK.md` |
| Math summary | `docs/math_summary.md` |
| Mac long-training plan | `docs/mac_long_training_plan.md` |
| Phase C plan | `docs/phase_c_multimodal_plan.md` |
| Cortical substrate code | `world/flux/brian2_cortical.py` |
| Long-training daemon | `world/flux/brian2_cortical_daemon.py` |
| Checkpoint utilities | `world/flux/brian2_checkpoint.py` |
| Phase A Brian2 hierarchical | `world/flux/brian2_hierarchical.py` |
| Tests | `tests/bet/test_bet_*.py` |

---

## Bekannte Bugs & Quirks

1. **F3b-Test silent-pass bug** (CLAUDE.md): `if n_strong_before == 0:
   persistence_fractions.append(1.0)` — Test kann nie failen wenn keine
   strong structures gebildet wurden. Nicht für Phase B/C relevant.

2. **Brian2 v_thresh as state-variable**: in `brian2_cortical.py` ist
   v_thresh per-neuron-state damit Homeostase funktioniert. Mac-Tests
   nutzen das. Windows-Brian2 sollte das gleichermaßen unterstützen.

3. **Audio manifest absolute paths**: alle Mac-Pfade `/Users/mkupermann/...`
   müssen auf Windows umgeschrieben werden (Patch oben).

4. **Telegram bot token**: `notify_config.json` enthält Bot-Token.
   Bei Übertragung sicherstellen dass nicht in Public Repo landet.
   `.gitignore` deckt `*.json` in `~/.eqmod/autopilot/` ab.

5. **BET-080 Daemon Resume**: wenn auf Windows die BET-080 Checkpoints
   liegen (`~/.eqmod/bet/BET-080/checkpoints/`), wird `run_long_training`
   beim nächsten Start automatisch vom letzten Checkpoint resumen.
   Falls fresh start gewünscht: vorher die checkpoint*.pkl löschen.

---

## Pre-registered Discipline

CLAUDE.md verlangt:
- Acceptance criteria PRE-registered bevor Daten erhoben werden
- Post-hoc Threshold-Tuning ist Protokoll-Verletzung
- NULL ist valider Verdict, kein "Retry bis PASS"
- Negative Controls (matched-wallclock, no-engram) müssen FAIL für trained
- Time-Budget hybrid: realistic + hard 2× ceiling
- Reusable mechanisms surface als `docs/patterns/`-Markdown

Drei sequenzielle NULLs (BET-067/071/072) auf credit-assignment sind ein
sauberer Befund, kein Failure-to-retry. Wenn auf Windows R-STDP nochmal
versucht wird, BAR vorher schreiben.

---

## Skill-Mapping (was on Mac aktiv war)

Profil-Skills von `~/.claude/skills/`:
- `michael-writing-style` — terse, direkt, deutsch beim Duzen
- `human-voice-drafting` — externe Publikationen vermeiden AI-tells
- `using-superpowers` — Skills aktiv invocieren

Auf Windows entsprechend einrichten falls Cowork/Claude-App diese kennt.

---

## Was du NICHT tust ohne Rücksprache

- Festplatten löschen, Branches force-pushen, große Refactors
- LLM/Transformer/Wav2Vec/Whisper irgendwo einbauen
- Pre-trained Embeddings nutzen (auch nicht "nur zur Validierung")
- Labels von Hand vergeben (User hat das heute explizit verboten)
- Post-hoc Threshold-Tuning (auch bei NULL nicht)
- BET-080 Checkpoints löschen ohne Confirm

---

## Letzter Status-Snapshot (Schreibzeit dieses Dokuments)

- Wallzeit: 2026-05-25, ~12:00 Mac-Zeit
- BET-080 läuft auf Mac PID 60540, h10/12, L5 acc 0.975
- main HEAD: `5b3b614` ("tools: word-segment extractor...")
- 11 commits diese Session
- Telegram-Bot funktional, Tokens in notify_config.json
- 4848 audio-segments extracted (für SHORTCUT-pipeline die user verworfen hat — siehe oben)

---

## Eröffnungs-Prompt für deine erste Antwort

Wenn du auf Windows hochfährst, der User wahrscheinlich nur "Hallo" oder
"Status?" tippt. Deine erste Antwort sollte sein:

> Übertragen vom Mac. Stand: Phase A done (4/7 Stufen), Phase B partial
> (BET-077c L5 0.84 KL ampl 12×, BET-079 4h PASS, BET-080 12h läuft auf
> Mac, h10/12, L5 0.975). User-Direktive: brain-faithful Audio→Text-
> Binding 3-10 englische Wörter, KEINE Labels (=LLM), keine pre-trained
> Modelle, kein externer Segmentierer. 3-10 Wörter PASS → Hardware-
> Upgrade vereinbart.
>
> Welche GPU? Brauche das für brian2cuda-Entscheidung. Dann starte ich
> BET-081 setup.

Dann pause für Hardware-Antwort.

---

Ende Handoff. Viel Erfolg auf 64GB+GPU. Mac steht als Backup. Push bei
sustained substrate-Updates regelmäßig auf main, damit Mac-Backup
synced bleibt.

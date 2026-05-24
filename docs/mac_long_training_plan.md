# Mac Long-Training Plan — Brain-faithful auf normaler Hardware

## Die ehrliche Ausgangslage

| | Größenordnung |
|---|---|
| Menschliches Gehirn | ~86 × 10^9 Neuronen |
| Cortex allein | ~16 × 10^9 Neuronen |
| Brian2 numpy Mac M1 Pro real-time | ~10^4–10^5 Neuronen |
| Brian2 C++ standalone Mac M1 Pro real-time | ~10^5–10^6 Neuronen |
| Phase A Substrat (BET-068) | 200 Neuronen |
| **Abstand zu Gehirn** | **4–7 Größenordnungen** |

12-jähriger Mensch ist nicht erreichbar auf Solo-Mac. Das muss vorweg
ehrlich gesagt werden. Aber: ein **unbeispielsweise langes brain-faithful
Substrat-Experiment**, das mehr lernt als jede Phase-A-Iteration und
empirisch zeigt, wo der Mac-Boden liegt — das ist erreichbar.

## Was Mac realistisch leisten kann

- Brian2 C++ Standalone, sparse Connectivity (1–5%), event-driven:
  10^5–10^6 LIF-Neuronen mit STDP, 24/7 über Monate.
- Continuous audio corpus streaming (LibriSpeech 1000h, Common Voice 8000h,
  öffentliche Hörbuch-Archive für Kontinuität).
- Sleep-Wake Zyklen: 8h Awake-Lernen, 8h Sleep-Replay (synthetische
  Trainings-Generation aus konsolidierten Patterns).
- Checkpoint/Resume: alle 30 Minuten gepickelter Substrate-State auf Disk.
  Pause/Resume verlustfrei.
- 12 Monate Wall-Clock = 12 Monate Substrate-Erfahrung wenn real-time,
  oder bis zu 10 Jahre subjektive Substrate-Zeit bei 10× Time-Acceleration
  (Brian2 läuft schneller als Real-Time wenn Hardware ausreicht).

## Die Brücke: was zwischen Phase A und "Kind-Niveau" liegt

| Stufe | Neurons | Trainingsdauer | Verlässliches Ergebnis |
|---|---|---|---|
| Phase A done | 200 | Minuten | binary, hierarchisch, generation, temporal |
| Mac mid-term | 10^4 | Wochen | rudimentäre Phonem-Cluster, einfache Sequenzen |
| Mac long-term | 10^5–10^6 | Monate-Jahre | Wort-Token-Cluster, einfache Bigramm-Statistik? |
| Brain scale | 10^9 | Jahre | Kind-Sprache |
| **Mac kann nicht** | 10^9 Neuronen | nicht skalierbar | volle Semantik, Theory-of-Mind, Komposition |

## Architektur-Plan (Mac M1 Pro, 16GB RAM)

### Substrate
- 10^4 hidden LIF + 2500 inhibitory (1:4 E:I) für Start
- 4 hierarchische Layer (cortical column analog): L1 (sensory), L2/3 (local),
  L4 (input), L5 (output) — pro Layer ~2500 Neuronen
- Sparse 5% Connectivity within layer, 10% feedforward, 2% top-down
- STDP überall + R-STDP (Frémaux-Gerstner BET-072 Ergebnis abwarten) auf
  L5→Motor Pathway

### Eingabe-Stream
- LibriSpeech corpus stream (Disk → MFCC features → Poisson rates)
- Continuous reading: nie abgeschlossen, immer mehr Audio verfügbar
- Curriculum: Audio-Bandbreite startet niedrig (nur f0 + Lautstärke),
  steigt über Monate auf volles Spektrum

### Sleep/Replay
- 14h continuous awake (audio streaming + STDP active)
- 4h sleep replay (substrate spielt mit max-activated Patterns ohne externes
  Audio, lokale Inhibition lockerer → "Träume" generieren synthetisches
  Training)
- 6h checkpoint + eval + idle (Mac thermische Erholung)

### Eval-Tape (täglich automatisch)
- Held-out audio chunks aus separater split
- Phonem-Cluster Reinheit (silhouette score über Substrate-Patterns)
- Hierarchische Discrimination (KL L1 vs L2 vs L3 vs L4)
- Generation cosine (top-down vs bottom-up)
- Telegram-Bericht jeden Tag 23:00 — "Mac-Substrate Day N"

### Infrastruktur
- `world/flux/long_runner.py` — Brian2 C++ standalone Daemon
- `~/.eqmod/long_run/checkpoints/` — gepickelte states, max 7 Tage
- launchd plist `com.eqmod.long_runner.plist` — auto-restart on crash
- `tools/long_run_eval.py` — täglicher cron eval-Bericht
- `tools/long_run_status.py` — Live-Status Dashboard

### Stopp-Kriterien (pre-registered)
- Hard cap: 12 Monate Wall-Clock
- Soft check alle 30 Tage:
  - Substrate-Spike-Aktivität nicht zusammengebrochen (>10% baseline)
  - Synapsen-Verteilung nicht degeneriert (std > 0.1)
  - Eval-Metrics monoton ODER verbessert verglichen mit Monat zuvor
- Plateau-Erkennung: wenn alle eval-Metrics 3 Monate flach → Diagnose-Fenster,
  ggf. curriculum-Switch, sonst FAILED post-mortem

## Was Phase B mit Mac NICHT macht

- Embodied robot (Mac kann kein Real-World-Embodiment)
- Visual cortex (Audio-only — sonst sprengt Compute)
- Multi-language (single English corpus)
- Real-time speech response (eval ist offline)
- Theory-of-Mind / komposit. Semantik (architektur-Limit, nicht Compute)

## Was Phase B mit Mac MACHT (Anspruch)

Empirische Antwort auf: "Was lernt ein brain-faithful Spiking-Substrate
mit 10^4–10^5 Neuronen, 5% sparse connectivity, R-STDP, Sleep-Replay,
auf 1000h+ kontinuierlichem Audio über 12 Monate?"

Ehrliche Hypothese: irgendwo zwischen "robuste Phonem-Cluster" und
"rudimentäre Wort-Boundary-Detection". KEIN bedeutungsvolles Verstehen,
KEINE Komposition, KEINE Antwort-Generation in Sprache.

Aber: das wäre die längste je-durchgeführte brain-faithful Audio-Lern-
Studie auf Consumer-Hardware. Publishable. Empirisch hart begründbar
als "Mac-Floor" — was geht und was nicht.

Phase B ist nicht: Kind-Niveau erreichen.
Phase B ist: empirisch die Grenze finden zwischen Algorithmik (Phase A
gemacht) und Skalierung (Phase C 10^9 Neuronen $30-50M GPU-Cluster).

## Sequenz

1. BET-072 R-STDP critic-actor (in flight)
2. BET-073 4-Layer hierarchical (10^4 Neuronen baseline)
3. BET-074 LibriSpeech 1h continuous Lauf (Infra-Test)
4. Infrastructure: Daemon, checkpoint, launchd, eval cron
5. Curriculum design (welche Audio-Bandbreite-Erweiterung wann)
6. 30-Tage soft start (Sandbox)
7. 12-Monate Lauf mit monatlichem eval-Schnitt

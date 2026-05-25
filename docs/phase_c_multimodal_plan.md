# Phase C — Multimodal Brain-faithful Substrate

Status: design, nicht implementiert. Trigger: BET-080 PASS.

## Ziel-Hypothese

Pre-LLM brain-faithful Substrate erweitern um Vision + Touch + visuelles
Lesen. Cross-modale Korrelations-STDP soll automatisch lernen, dass
zeitgleiche Stimuli aus verschiedenen Modalitäten zusammen gehören —
keine externen Labels, kein supervised cross-modal binding.

Erfolgs-Kriterium (Phase C als Ganzes):
Substrat zeigt mindestens **eine** cross-modale Generalisierung — z.B.
WN-Audio + WN-Visual (Snow-Noise) bildet einen anderen Cluster als
EN-Audio + Apfel-Bild, OHNE dass das System je explizit gesagt
bekommen hat welche Modalitäten zusammen gehören.

---

## Architektur

```
                    Cross-Modal-Cortex
                    (L23/L5, 8000 neurons)
                ╱        ↑       ╲
              ╱          │         ╲
   Audio-Cortex   Visual-Cortex   Tactile-Cortex
   (4×1250)      (4×2000)         (4×1000)
   = 5000        = 8000           = 4000
       ↑              ↑                ↑
   Mic-Stream    Webcam-Stream    Touch-Stream
   (16Hz/Tick)   (30Hz/Frame)     (event-driven)

         ↘             ↑               ↗
                Motor/Output Layer
                (L5, 2000 neurons)
```

**Neuronen-Total:** ~27K Excitatory + ~7K Inhibitory = **34K Neuronen**
**Synapsen-Budget:** ~30M (passt auf Mac 16GB wie BET-077c)

Jeder Sensor-Cortex hat dieselbe 4-Layer-Struktur wie BET-077c:
- L4 input
- L23 local processing
- L5 output
- L6 feedback

Cross-Modal-Cortex empfängt L5-Output aller drei Sensor-Cortices,
projiziert L6-Feedback zurück an alle L4-Input-Layer (top-down
attention).

---

## Sensoren-Pipeline (Mac Hardware)

### Vision (Webcam)
- Quelle: `AVFoundation` Mac Webcam, 30 fps, RGB → grayscale
- Downsample: 640×480 → 64×64 = 4096 pixels
- Feature: pixel intensity → Poisson-Rate $[0, 100]$ Hz
- Input-Neuronen: 4096 (eins pro Pixel)
- Frame-Rate: 30 Hz → ein Substrate-Update alle 33ms (3-4 sim-Chunks bei 10ms-Auflösung)
- Latenz: ca. 50ms Webcam-Bild-Akquisition

### Audio (Mikrofon)
- Quelle: `AVFoundation` Mac Mic, 16kHz mono
- Existing pipeline (Phase B): 16 samples/tick → 10 FFT features → 10 Poisson neurons
- Erweitern: Mel-Skala 32 bands → 32 Poisson neurons
- Update-Rate: 100 Hz wie Phase B

### Tactile (Trackpad)
- Quelle: `MultitouchSupport.framework` private API ODER USB-Drucksensor (FSR-402, ~15€)
- Spatial: 16×9 = 144 touch-points OR 8 pressure-channels (USB)
- Feature: pressure/proximity → spike-event bei Threshold-Überschreitung
- Event-driven: kein fixed sample rate

### Heterogene Zeit-Skalen
Brian2 unterstützt mehrere Clocks. Audio läuft bei 1ms, Vision bei 33ms,
Touch event-driven. Cross-Modal-Cortex läuft bei langsamster Clock (33ms).
Trade-off: visuelle Reaktionszeit limitiert audiotaktilen Response.

---

## Cross-Modal STDP

Standard STDP funktioniert ohne Modifikation für cross-modal: wenn
Audio-Neuron $a$ und Visual-Neuron $v$ innerhalb $\tau_{STDP} = 20$ ms
beide feuern UND ihre Output-Synapsen zur selben Cross-Modal-Neuron $c$
beide aktiv sind, verstärkt sich beides via Hebbian Plastizität.

Notwendig zusätzlich:
- Cross-modal Synapsen mit eigenem $w_{\max} = 0.5$ (verhindert dass
  eine Modalität dominiert)
- Cross-modal-Cortex Inhibitory-Pool mit verstärktem $p_{IE} = 0.5$
  (Stabilität trotz multipler Inputs)
- Homeostatic threshold drift PRO Neuron (wie BET-077c)

---

## Reading-Pfad (durch Vision-Cortex)

Kein eigener Text-Encoder. Stattdessen:

1. Text wird **gerendert** als Bild (PIL: schwarz Text auf weißem Grund,
   Schriftgröße 24, monospace)
2. Bild via Webcam-Loop in Vision-Cortex (oder direkt programmgesteuert)
3. Substrat lernt Buchstaben-Formen via STDP im Visual-L23
4. Buchstaben-Cluster im L5
5. Wort-Cluster im Cross-Modal-Cortex (wenn gleichzeitig gesprochenes
   Wort via Audio-Pfad eingeht)
6. Bedeutung emergiert via Audio-Visual-Korrelation über Tausende
   Beispielen

**Realistische Hypothese:** nach mehreren Wochen sustained training
kann Substrat einzelne Buchstaben unterscheiden (visuelle Cluster) und
gehört-gesprochene Wörter mit ihren visuellen Schriftformen
assoziieren. **Echtes Verstehen oder semantische Generalisierung
unrealistisch** auf Mac-Skala.

---

## Memory-Budget Phase C

| Component | Neuronen | Synapsen pro | Synapsen total | Memory |
|---|---|---|---|---|
| Audio-Cortex (4 layer + I) | 5K | 1500 avg | 7.5M | 600 MB |
| Visual-Cortex (4 layer + I) | 8K | 1500 avg | 12M | 960 MB |
| Tactile-Cortex (4 layer + I) | 4K | 1500 avg | 6M | 480 MB |
| Cross-Modal | 8K | 1500 avg | 12M | 960 MB |
| Cross-Modal Synapsen (audio→cm, vision→cm, tactile→cm) | — | — | 5M | 400 MB |
| Motor/Output | 2K | 500 avg | 1M | 80 MB |
| Brian2 overhead + buffers | — | — | — | ~2 GB |
| **Total** | **27K** | — | **43.5M** | **~5.5 GB** |

Mac 16GB nutzbar ≈ 14GB → passt mit ~8GB Headroom. Längere Runs ohne
SpikeMonitor-Buffer (record=False) wie BET-077c.

---

## Realtime-Schätzung

BET-076 1M Neuronen sparse: ~500× slower than realtime.
BET-077c 25K cortical: ~100× slower.
Phase C 27K cortical-multimodal: ~120-150× slower.

→ 1h Substrate-Erfahrung = 120-150h Wallzeit = 5-6 Tage.
→ Für jede Stunde Substrat-Erfahrung muss Mac 5-6 Tage continuous laufen.

Realistischer Trainings-Zyklus:
- 1 Woche Wallzeit = ~1 Stunde Substrat-Erfahrung
- 1 Monat Wallzeit = ~4 Stunden Substrat-Erfahrung
- 12 Monate Wallzeit = ~50 Stunden Substrat-Erfahrung

Das ist sehr wenig. Brain bekommt 24/7 Sensorik für Jahre. Substrat
auf Mac bekommt ~Stunden in einem Jahr. Erwartungs-Realität:
**rudimentäre cross-modale Cluster, KEIN reichhaltiges Verstehen**.

---

## Pre-registered BETs

| BET | Was | Pre-registered Bar |
|---|---|---|
| 081 | Vision-only substrate (8K Neuronen) auf MNIST-äquivalent | L5 acc > 0.6 auf 10-Klassen-Digits |
| 082 | Tactile-only substrate (4K) auf 3-pattern Touch | Discrimination acc > 0.7 |
| 083 | Audio+Vision parallel (ohne cross-modal Verdrahtung) | Beide Cortices lernen unabhängig, keine Inferferenz |
| 084 | Cross-modal STDP (Audio+Vision gekoppelt zu Cross-Modal-Cortex) | Cross-Modal-Cluster zeigt KL > 0.05 zwischen "Audio0+Vision0" und "Audio1+Vision1" Konditionen |
| 085 | Reading-Pipeline: 5 Buchstaben (a, b, c, d, e) gerendert + gesprochen | Substrat kann nach Training visuell präsentiertes "a" mit gehörtem "a" assoziieren (cross-modal prototype-cosine > 0.5) |
| 086 | 1-Wort Vokabular: "Apfel" visuell + auditiv | Substrat lernt Audio-Visual-Bindung in <1 Woche Wallzeit |
| 087 | 7-Tag continuous multimodal training | Substrat-Metriken monoton oder verbesserd über 7 Tage |

Jeder BET kann NULL ergeben — Phase C ist offene Forschung, nicht
garantierter Erfolg. NULL bei BET-085+ (Reading) ist erwarteter Ausgang
und liefert wichtige Daten zu Grenzen brain-faithful Multimodal-
Substrate auf Mac-Hardware.

---

## Risiken & Bekannte Schwierigkeiten

1. **Cross-modal Binding Problem**: STDP allein reicht möglicherweise
   nicht für stabile cross-modale Repräsentationen. Frontal-cortex-
   ähnliche "Pointer"-Strukturen wären biologisch notwendig — die
   können wir nicht engineeren ohne wieder zum LLM-Pfad zu rutschen.

2. **Temporal Alignment**: visuelles Bild + gesprochenes Wort müssen
   innerhalb $\tau_{STDP} = 20$ ms koinzidieren — das ist sehr kurz.
   Real-world Sprache + Bild hat Verzögerungen von 100-500ms.
   Mögliche Lösung: längere $\tau_{STDP}$ für cross-modal Synapsen
   (50-200ms), reflektiert biologische cross-modal trace integration.

3. **Reading-Pipeline ist symbolisch verlockend**: die Versuchung
   Buchstaben direkt zu encoden statt visuell zu rendern wäre
   praktisch, aber bricht das pre-LLM-Prinzip. Bleiben bei visuellem
   Pfad — auch wenn langsamer.

4. **Mac thermisches Limit**: 7-Tage continuous Brian2 + multimodal
   Sensors → CPU dauerhaft 70-90°C. Fans laufen permanent. Stromrechnung
   ~50€/Monat. Hardware-Verschleiß messbar nach 12 Monaten.

5. **Webcam-Auflösung**: 64×64 ist Mindestmaß für Letter-Recognition.
   Visual-Cortex von 8K Neuronen kann ~10-20 visuelle Templates lernen.
   Reichhaltiges Vokabular (~100+ Wörter) braucht 50K+ Visual-Cortex,
   überschreitet Memory-Budget.

---

## Implementierungs-Sequenz (wenn BET-080 PASS)

1. **Woche 1-2**: Webcam-Integration + Visual-Cortex (BET-081)
2. **Woche 3**: Trackpad/Touch-Integration (BET-082)
3. **Woche 4**: Audio + Vision parallel (BET-083)
4. **Monat 2**: Cross-modal STDP (BET-084)
5. **Monat 3-4**: Reading-Pipeline Setup (BET-085, 086)
6. **Monat 5-12**: Sustained multimodal training (BET-087)
7. **Monat 12**: Phase-C-Bilanz, Entscheidung über Phase D

---

## Was Phase C NICHT versuchen wird

- LLM-style Tokenisierung von Text
- Pre-trained Visual Encoder (ResNet, ViT, DINO)
- Pre-trained Audio Encoder (Wav2Vec, Whisper)
- Backprop / Gradient Descent irgendwo
- Symbolische Reading-Pipeline
- Robot embodiment (physische Bewegung)
- Multi-task fine-tuning
- Reward-shaped multimodal RL

Alles davon würde die "brain-faithful, pre-LLM" Constraint brechen.

---

## Was Phase C verspricht (ehrliche Erwartungs-Bilanz)

| Optimistisch | Pessimistisch |
|---|---|
| Cross-modal cluster zwischen 3-5 Modalitäts-Paare | Cross-modal cluster bricht zusammen, jede Modalität bleibt isoliert |
| Visuelle Letter-Discrimination 80%+ | Visuelle Letter-Discrimination 30% (chance-level für 10 Klassen) |
| Audio-Visual Word-Binding für 5-10 Wörter | Word-Binding scheitert, nur Pattern-Korrelation messbar |
| Tactile-Audio-Visual triple coincidence | Tactile Pfad zu spärlich für sinnvolle Beiträge |
| Substrate "erinnert" sich an gesehene Patterns nach Tagen | Substrate vergisst nach Stunden ohne Replay |

Wahrscheinlichkeit pessimistisch > optimistisch. Aber **selbst NULL
liefert Daten**: was geht NICHT auf Mac-Skala mit brain-faithful
Primitiven. Diese empirische Grenze ist publishable und für die
Skalierungs-Frage (Phase D mit GPU-Cluster) wertvoll.

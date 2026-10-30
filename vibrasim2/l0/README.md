# L0 — kontinuierliches Erfahrungslernen, Kandidat K1

Kern und Prüfer zu [G176](../../docs/amendments/G176_l0_continuous_experience_learning.md).
Der technische Stand ist geprüft. Der erste vollständige Lauf ist mit **NULL**
abgeschlossen: deutliche Verbesserung, absolute Mindestleistung verfehlt.
[Ergebnisbericht](../../docs/l0/AI_EXPERIMENT.md). Eine neue mathematische Methode
oder allgemeines Lernen ist damit nicht belegt.

## Komponenten

- `core.py`: kontinuierliche Handlungsvorschläge, eigene Erfahrungen, zeitlich
  abklingendes Feedback, FIFO-Grenze, unverändernde Prüfung und JSON-Neustart.
- `evaluation.py`: getrennte Sollfunktionen, Datenaufteilung, fünf Kontroll-/
  Referenzvarianten, Rohdaten, Neustartvergleich und getrennte Ergebnisurteile.
- `benchmark.py`: Ressourcenmessung mit zufälligem, nicht zielabhängigem Feedback.

Kein LLM, vortrainiertes Modell, Kamera-, Mikrofon- oder Lautsprecherzugriff.
Der erste Eingang ist ein einzelner Messwert in [0,1]; das ist noch keine
allgemeine Wahrnehmung. Die Integration in historische Substratmodule ist offen.

## Kern verwenden

Im Repository mit der vorhandenen Python-3.13-Umgebung:

```python
from vibrasim2.l0.core import Learner, frequency

learner = Learner(seed=42)
attempt = learner.attempt(context=0.4, now=0.0)
print(attempt.id, attempt.action, frequency(attempt.action))
learner.feedback(attempt.id, reward=1.0, now=1.0)
learner.save("l0-state.json")
restored = Learner.load("l0-state.json")
actions = restored.evaluate([0.1, 0.4, 0.9], seed=43)
```

`frequency` berechnet nur eine Frequenz. Es wird kein Ton ausgegeben.
`now` ist eine monotone Uhr in Sekunden; mehrere Versuche dürfen denselben
Zeitpunkt haben. Ohne Bewertung `expire(now)` aufrufen. Neutral ist `reward=0`,
negative Bewertung `reward=-1`. Für jede ID wird höchstens ein Feedback akzeptiert.
Offene Versuche werden beim Laden mit Warnung verworfen; Erfahrung, nächste ID
und Trainingszufall bleiben erhalten. Der Kern wird von einem Thread bedient.

## Technisch prüfen

```powershell
.\.venv\Scripts\python.exe -B -m pytest tests/vibrasim2/test_l0_core.py tests/vibrasim2/test_l0_evaluation.py tests/vibrasim2/test_l0_benchmark.py tests/vibrasim2/test_p3.py -q -p no:cacheprovider --basetemp "$env:TEMP\vibrasim-l0-check"
.\.venv\Scripts\python.exe -B tools/test_safety.py
```

Eine erneute Ressourcenmessung benötigt einen neuen Ergebnisdateinamen:

```powershell
.\.venv\Scripts\python.exe -B -m vibrasim2.l0.benchmark --output docs/validation/l0-resource-new.json
```

Die Messung hat 120 Sekunden Zeitgrenze, 2 GiB Grenze für den maximalen residenten
Prozessspeicher und 100 MiB für den gespeicherten Zustand. Prüfungen erfolgen
zwischen Arbeitsschritten; das ist kein vom Betriebssystem erzwungenes Prozesslimit.
Der Bericht wird nicht überschrieben. Windows ist geprüft; Linux/macOS noch nicht.

## Eingefrorener Forschungslauf

`run_repetition(seed, directory, guard=...)` implementiert die komplette A/B-
Abfolge eines Seeds, schreibt Daten, alle Trainingsereignisse, Prüfhandlungen,
Bewertungen und Zustände. Neue Ausgabeverzeichnisse sind verpflichtend.
`summarize(rows, ...)` bewertet die 30 Wiederholungen numerisch.

`run.py` ergänzt gemäß [G177](../../docs/amendments/G177_l0_frozen_run.md) den
verbindlichen Launcher: exklusives Manifest, Code-/Protokoll-/Umgebungshashes,
feste Seeds und Budgets, Ressourcenwächter, exakte Reproduktion sämtlicher
Wiederholungen und Abgleich des Urteils mit den gehashten Rohdateien.
Der autorisierte einmalige Lauf liegt unter
`archive/run-logs/l0/2026-09-16-observed-001`.

Nach Abschluss lässt er sich ohne erneutes Training prüfen:

```powershell
.\.venv\Scripts\python.exe -B -m vibrasim2.l0.run assess archive/run-logs/l0/2026-09-16-observed-001
.\.venv\Scripts\python.exe -B tools/l0_independent_audit.py archive/run-logs/l0/2026-09-16-observed-001
```

Die unabhängige Nachrechnung prüft Bewertungen, Feedback-Zuordnung, Datenaufteilung
und Statistik ohne Import des Lernkerns oder Prüfers. Die exakte Reproduktion
verwendet dagegen bewusst dieselbe eingefrorene Implementierung. Beides ist
keine unabhängige Replikation auf anderen Aufgaben oder einer anderen Maschine.
Keine Schwellen nach Ergebnissen ändern und keine erfolgreichen Seeds auswählen.

[Technischer Prüfbericht](../../docs/validation/l0-20260916.md)

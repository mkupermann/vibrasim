# Gemeinsame Methodik (Vibrasim & Cortex HDC)
*Wissenschaftliche Standards für reproduzierbare Experimente und Benchmarks in Forschung und Business.*

---

## 🎯 Prinzipien

### 1. Pre-Registered Goals
**Alle Benchmarks haben vorab festgelegte Ziele, die nicht nachträglich angepasst werden.**

*Begründung:* Verhindert "P-Hacking" (Anpassung der Hypothesen an die Daten) und sichert die wissenschaftliche Integrität. Für Unternehmen bedeutet dies klare, verbindliche Erwartungen an die Performance.

| Projekt       | Metrik               | Zielwert       | Ergebnis      | Status   | Datum       | Notizen |
|---------------|----------------------|-----------------|---------------|----------|-------------|---------|
| Cortex HDC    | Latenz (10K Einträge) | ≤50 ms          | 3,8 ms         | ✅ PASS   | 2026-07-28 | 37× schneller nach Optimierung |
| Cortex HDC    | Speicher (10K Einträge) | ≤15 MB          | 20,2 MB        | ❌ FAIL   | 2026-07-28 | Base64-Overhead + Entry-Text |
| Cortex HDC    | Recall@5             | ≥70 %           | 72,7 %         | ✅ PASS   | 2026-07-28 | Gegen multilingual-e5-small (70 %) |
| Cortex HDC    | Indexierung (1M Einträge) | ≤30 Min.        | 31,6 Min.      | ❌ FAIL   | 2026-07-28 | Linearer Scan → HD-NSW-Index geplant |
| Vibrasim      | Marker 1: `len(self_model) ≥ 2` | ≥2 | [Wert] | [Status] | [Datum] | [Notizen] |
| Vibrasim      | Marker 2: `workspace_winner > 0` | >0 | [Wert] | [Status] | [Datum] | [Notizen] |

**Regeln:**
1. Ziele werden **vor** dem Experiment/Benchmark definiert.
2. Ziele dürfen **nicht nachträglich** angepasst werden, auch wenn Ergebnisse unerwartet sind.
3. **NULL/FAIL**-Ergebnisse werden dokumentiert und analysiert.

---

### 2. Negative Controls
**Jeder Benchmark enthält Kontrollgruppen, um False Positives zu erkennen.**

*Begründung:* Bewegt, dass das System nicht nur zufällig funktioniert, sondern robust gegen Noise ist. Für Unternehmen ist dies ein Nachweis der Zuverlässigkeit.

| Projekt       | Benchmark          | Kontrollgruppe                     | Erwartetes Ergebnis | Tatsächliches Ergebnis |
|---------------|--------------------|------------------------------------|--------------------|----------------------|
| Cortex HDC    | Recall@5           | 96 Off-Topic-Abfragen (z. B. "Kuchenrezepte", "Fußballtabellen", "Quantenfeldtheorie") | ≤8 % False Positives | 8 % (bei Schwellenwert 0,55) |
| Vibrasim      | Marker-Protokoll   | Läufe ohne trainierte Engramme     | Marker feuern **nicht** | [Wert] |

**Regeln:**
1. Kontrollgruppen müssen **identisch** zu den Testgruppen sein, außer der untersuchten Variable.
2. Ergebnisse der Kontrollgruppe werden **immer** dokumentiert.
3. Falls die Kontrollgruppe unerwartet **positiv** abschneidet, wird das Experiment **nicht gewertet** und überarbeitet.

---

### 3. Reproduzierbarkeit
**Alle Experimente sind reproduzierbar durch:**
- Feste Seeds (`seed=42`).
- Skript-basierte Ausführung (keine manuellen Schritte).
- Dokumentierte Umgebungen (Docker, `requirements.txt`, Python-Version).

*Begründung:* Ermöglicht Peer-Review in der Forschung und Auditierbarkeit im Business.

#### Beispiele

**Cortex HDC:**
```bash
# Benchmark reproduzieren
python scripts/generate_figures.py --seed 42

# Alle Messwerte werden in figures/measurements.json gespeichert
```

**Vibrasim:**
```bash
# Experiment reproduzieren
python -m world run --config renders/calibration_session3.toml --seed 42

# Kalibrierte Konfigurationen sind in renders/ gespeichert
```

**Anforderungen an Reproduzierbarkeit:**
1. **Fester Seed**: Jedes Experiment nutzt `seed=42` (oder einen dokumentierten Wert).
2. **Skript-basiert**: Keine manuellen Schritte – alles muss über die Kommandozeile ausführbar sein.
3. **Dokumentierte Umgebung**:
   - Python-Version (z. B. 3.11 für Cortex HDC, 3.13 für Vibrasim).
   - Abhängigkeiten (`requirements.txt` oder `pyproject.toml`).
   - Docker-Container (falls verfügbar).
4. **Dokumentierte Konfigurationen**: Alle Parameter in TOML/JSON-Dateien (keine Hardcodes).

---

### 4. Honest Reporting
**FAILs und NULL-Ergebnisse werden dokumentiert – nicht vertuscht.**

*Begründung:* Wissenschaftliche Integrität (Forschung) und Vertrauen bei Kunden/Investoren (Business).

| Projekt       | FAIL               | Zielwert       | Ergebnis      | Ursache | Lösung | Status |
|---------------|--------------------|-----------------|---------------|---------|--------|--------|
| Cortex HDC    | Speicher (10K Einträge) | ≤15 MB          | 20,2 MB        | Base64-Overhead (33 %) + Entry-Text (~3,5 MB) | Binary Sidecar oder SQLite | ⏳ Offen |
| Cortex HDC    | Indexierung (1M Einträge) | ≤30 Min.        | 31,6 Min.      | Linearer Scan in Python | HD-NSW-Index implementieren | ⏳ Offen |

**Regeln:**
1. **Alle Ergebnisse** (auch FAILs/NULLs) werden dokumentiert.
2. **Ursachenanalyse** wird durchgeführt und dokumentiert.
3. **Lösungsvorschläge** werden transparent kommuniziert.
4. **Ziele werden nicht nachträglich gesenkt**, um ein PASS zu erzielen.

---

## 🔬 Anwendung in der Forschung

### Warum diese Methodik?
- **Reproduzierbarkeit**: Experimente können von anderen Forschern **1:1 nachvollzogen** werden.
- **Transparenz**: Alle Entscheidungen (Ziele, Kontrollen, Anpassungen) sind **dokumentiert**.
- **Glaubwürdigkeit**: Ehrliche Berichterstattung über FAILs erhöht das Vertrauen in die Ergebnisse.

### Beispiel: Vibrasim
- **Pre-Registered Goals**: 5 Marker in `docs/marker_protocol.md` (z. B. `len(self_model) ≥ 2`).
- **Negative Controls**: Läufe ohne Engramme zeigen, dass Marker **nicht** feuern.
- **Reproduzierbarkeit**: Alle Experimente nutzen `rng_seed=42` und kalibrierte TOMLs.
- **Honest Reporting**: G19 (Predictive Babble) → **FAIL** (0/8 Marker), dokumentiert in `LOGBOOK.md`.

### Beispiel: Cortex HDC
- **Pre-Registered Goals**: Latenz (≤50 ms), Speicher (≤15 MB), Recall@5 (≥70 %).
- **Negative Controls**: Off-Topic-Abfragen (8 % False Positives bei Schwellenwert 0,55).
- **Reproduzierbarkeit**: `scripts/generate_figures.py --seed 42`.
- **Honest Reporting**: Speicherbedarf (20,2 MB) → **FAIL** (Ziel: ≤15 MB), dokumentiert im README.

---

## 🏢 Anwendung im Business

### Warum diese Methodik?
- **Vertrauen bei Kunden**: Pre-registered Goals zeigen, dass die Ziele **vor** der Implementierung definiert wurden.
- **Compliance**: Reproduzierbarkeit und Dokumentation erfüllen Anforderungen an **ISO 27001**, **DSGVO** oder interne Audits.
- **Transparenz**: Negative Controls und Honest Reporting beweisen, dass das System **robust** und **ehrlich** ist.

### Beispiel: Cortex HDC für Unternehmen
| Anforderung               | Umsetzung in Cortex HDC | Nutzen für Kunden |
|---------------------------|--------------------------|------------------|
| **Datensouveränität**     | 100 % offline, keine Cloud | Keine DPA-Verhandlungen nötig |
| **Performance-Nachweis**   | Pre-registered Benchmarks (Latenz, Recall) | Klare Erwartungen |
| **Robustheit**            | Negative Controls (Off-Topic-Abfragen) | Nachweis der Zuverlässigkeit |
| **Auditierbarkeit**       | Reproduzierbare Experimente (`seed=42`) | Compliance-konform |
| **Ehrlichkeit**           | Honest Reporting (FAILs dokumentiert) | Vertrauen in die Lösung |

---

## 📋 Checkliste für neue Experimente/Benchmarks

### Vor dem Experiment
- [ ] **Ziel definieren** (Metrik, Zielwert, Beschreibung).
- [ ] **Ziel in `METHODOLOGY.md` oder `BENCHMARK_PROTOCOL.md` eintragen.**
- [ ] **Negative Control definieren** (was ist die Kontrollgruppe?).
- [ ] **Seed festlegen** (Standard: `seed=42`).
- [ ] **Konfiguration dokumentieren** (TOML/JSON-Datei).

### Während des Experiments
- [ ] **Skript-basiert ausführen** (keine manuellen Schritte).
- [ ] **Alle Parameter dokumentieren** (Umgebung, Abhängigkeiten, etc.).

### Nach dem Experiment
- [ ] **Ergebnisse dokumentieren** (auch FAILs/NULLs).
- [ ] **Ursachenanalyse** durchführen (falls FAIL/NULL).
- [ ] **Lösungsvorschlag** dokumentieren (falls nötig).
- [ ] **Negative Controls prüfen** (Haben sie wie erwartet abgeschnitten?).

---

## 🔗 Verwandte Dokumente
- [Vibrasim: marker_protocol.md](./marker_protocol.md) (Marker-Protokoll)
- [Vibrasim: LOGBOOK.md](../LOGBOOK.md) (Forschungs-Tagebuch)
- [Cortex HDC: BENCHMARK_PROTOCOL.md](https://github.com/mkupermann/JuiceHDC/blob/main/docs/BENCHMARK_PROTOCOL.md) (spezifische Benchmark-Regeln)
- [Cortex HDC: LOGBOOK.md](https://github.com/mkupermann/JuiceHDC/blob/main/LOGBOOK.md) (Entwicklungsprotokoll)

---

## 📝 Versionshistorie
| Version | Datum       | Änderungen | Autor |
|---------|-------------|-----------|-------|
| 1.0     | 2026-07-28  | Erste Version | Michael Kupermann |
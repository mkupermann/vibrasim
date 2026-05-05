# Welt der Schwingungen — Spezifikation

Diese Datei beschreibt eine simulierte Welt, deren einzige Grundsubstanz Schwingungen sind. Aus diesen Schwingungen entstehen durch klare Naturgesetze hierarchisch aufgebaute Strukturen — Elektronen, Atome, Moleküle und höhere Ebenen. Langfristiges Ziel ist es, auf dieser Grundlage gehirnartige Strukturen zu bauen.

Die Spezifikation ist als Übergabedokument für eine Implementierung gedacht. Sie ist vollständig und umsetzbar.

---

## Teil 1 — Die Verfassung der Welt

### Der Raum

Der Raum ist zweidimensional und konzeptionell unendlich. In der Implementierung wird er als endliche Fläche dargestellt (z.B. 1000 × 1000 Einheiten), aber mit periodischen Randbedingungen — Schwingungen, die einen Rand verlassen, kommen am gegenüberliegenden Rand wieder herein. Damit verhält sich der endliche Raum lokal wie ein unendlicher.

Der Raum ist leer und ohne intrinsische Geographie. Er ist Bühne, nicht Inhalt.

### Die Schwingungen

Die elementaren Bewohner der Welt sind Schwingungen. Jede Schwingung hat folgende Eigenschaften:

- **Frequenz** (kontinuierlich, jeder positive Wert möglich)
- **Polarität** (binär: gerade oder ungerade — unabhängig von der Frequenz)
- **Position** im 2D-Raum (kontinuierliche Koordinaten)
- **Geschwindigkeit** (Richtung und Tempo der geradlinigen Bewegung)

Polarität ist eine eigene Eigenschaft, nicht aus der Frequenz abgeleitet. Eine Schwingung mit 600 Hz kann sowohl gerade als auch ungerade sein, je nach ihrer zugeordneten Polarität.

### Bewegung

Freie Schwingungen ziehen geradlinig durch den Raum mit konstanter Geschwindigkeit. Sie ändern weder Frequenz noch Polarität noch Richtung von alleine. Bewegung ist ihr natürlicher Zustand.

### Erste Bindung — Entstehung von Elektronen

Wenn zwei Schwingungen aufeinandertreffen, kann ein Elektron entstehen. Drei Bedingungen müssen gleichzeitig erfüllt sein:

1. **Räumliche Nähe**: Der Abstand zwischen den beiden Schwingungen ist kleiner als die kritische Distanz `r_1`.
2. **Polaritätsunterschied**: Eine Schwingung ist gerade, die andere ungerade.
3. **8%-Frequenzregel**: Die Frequenzen unterscheiden sich um genau 8 % (mit kleiner Toleranz, etwa ±0,5 %, um numerischen Rauschen Rechnung zu tragen).

Bei erfüllten Bedingungen entsteht ein **Elektron** an der Bindungsstelle:

- Die Frequenzen der zwei Bestandteile addieren sich. Das Elektron hat als Frequenz `f1 + f2`.
- Das Elektron ist ortsfest. Es bleibt an der Stelle, an der die Bindung passierte.
- Innen schwingen die zwei ursprünglichen Schwingungen weiter — der Knoten ist außen ruhig, innen lebendig.
- Polarität: Da das Elektron aus 2 Bestandteilen besteht, ist seine Polarität **gerade** (Variante 3 — Parität durch Größe).

### Atombildung — stufenweise Stabilisierung

Atome entstehen aus mehreren Elektronen. Der Prozess ist stufenweise:

**Stufe 1 — Elektronenpaar (2 Elektronen):**
- Zwei Elektronen binden, wenn sie räumlich unter `r_2` zueinander stehen, ihre Polaritäten passen (gerade trifft auf ungerade), die 8%-Frequenzregel erfüllt ist und sie in derselben Frequenzgrößenordnung liegen.
- Polarität des Paars: ungerade (3 Bestandteile insgesamt, da das Paar zwei Elektronen mit je 2 Schwingungen enthält... — siehe Anmerkung unten zur Paritätszählung).
- **Status: temporär.** Wenn nichts Weiteres passiert, kann das Paar nach einer charakteristischen Zerfallszeit wieder in zwei Elektronen zerfallen.

**Stufe 2 — Triade (3 Elektronen):**
- Ein drittes Elektron schließt sich an, wenn die Bedingungen erfüllt sind.
- **Status: ziemlich stabil**, aber nicht permanent. Die Zerfallszeit ist deutlich länger als bei Paaren.

**Stufe 3 — Atom (4 Elektronen):**
- Beim vierten Elektron rastet das Atom ein.
- **Status: unzerstörbar.** Das Atom kann nicht mehr in einzelne Elektronen zerfallen.
- Es ist ab diesem Moment ein permanenter Bestandteil der Welt.

### Anmerkung zur Paritätszählung

Bei Variante 3 (Parität durch Größe) zählt die Anzahl der gebundenen Schwingungen, nicht der gebundenen Elektronen. Da jedes Elektron 2 Schwingungen enthält:

- Elektron = 2 Schwingungen → gerade Polarität
- Elektronenpaar = 4 Schwingungen → gerade Polarität
- Triade = 6 Schwingungen → gerade Polarität
- Atom = 8 Schwingungen → gerade Polarität

Da bei dieser Zählung alle gebundenen Strukturen aus geraden Anzahlen bestehen, gibt es ein Problem mit der Bindungsregel "gerade trifft auf ungerade".

**Lösung:** Die Polarität wird auf der Ebene der Elektronen gezählt, nicht auf der Ebene der Schwingungen.
- Elektron = 1 Bestandteil-Element → ungerade
- Paar = 2 Elektronen → gerade
- Triade = 3 Elektronen → ungerade
- Atom = 4 Elektronen → gerade

Mit dieser Zählung können sich Strukturen abwechselnd verbinden, und die Welt bleibt produktiv.

### Höhere Hierarchien — Moleküle und darüber

Atome verbinden sich nach analogen Regeln zu Molekülen. Allgemein gilt für die Bindung zwischen Knoten:

1. **Räumliche Nähe**: Der Abstand ist kleiner als die für die Hierarchieebene geltende Distanzschwelle.
2. **Polaritätsunterschied**: Gerade trifft auf ungerade (auf Knotenebene gezählt).
3. **8%-Frequenzregel**: Die Frequenzen unterscheiden sich um genau 8 %.
4. **Gleiche Frequenzgrößenordnung**: Beide Knoten liegen im gleichen logarithmischen Frequenzbereich (z.B. 1.000–9.999 Hz oder 10.000–99.999 Hz).

Die Frequenzgrößenordnung ist wie folgt definiert:
- Größenordnung n = floor(log10(Frequenz))
- Knoten der Größenordnung n verbinden sich nur mit anderen Knoten der Größenordnung n.

### Skalentrennung durch Abstoßung

Knoten verschiedener Größenordnungen tun nicht nichts — sie stoßen sich gegenseitig ab, sobald ihr Frequenzverhältnis 1000 oder mehr beträgt.

Die Abstoßungskraft wird modelliert als:

```
F = -k * (Frequenzverhältnis - 1000) / Distanz²    wenn Verhältnis > 1000
F = 0                                              sonst
```

Diese Abstoßung sortiert die Welt räumlich: kleine Strukturen leben in einer Region, mittlere in einer anderen, große in einer dritten.

---

## Teil 2 — Implementierungsarchitektur

### Datenstrukturen

```python
class Schwingung:
    position: tuple[float, float]
    geschwindigkeit: tuple[float, float]
    frequenz: float
    polaritaet: bool  # True = gerade, False = ungerade
    
class Knoten:
    position: tuple[float, float]
    frequenz: float
    polaritaet: bool  # bestimmt durch Anzahl der Bestandteile
    bestandteile: list  # Liste der enthaltenen Schwingungen oder Knoten
    hierarchie_ebene: int  # 1=Elektron, 2=Paar, 3=Triade, 4=Atom, ...
    stabilitaet: float  # 0..1, bei Atomen 1.0 (unzerstörbar)
    erzeugungs_zeit: float
    
class Welt:
    schwingungen: list[Schwingung]
    knoten: list[Knoten]
    raum_groesse: tuple[float, float]
    parameter: WeltParameter
```

### Hauptschleife

```python
def schritt(welt, dt):
    # 1. Bewegung der freien Schwingungen
    bewege_schwingungen(welt, dt)
    
    # 2. Anwendung der Skalen-Abstoßung auf alle Knoten
    wende_abstossung_an(welt, dt)
    
    # 3. Suche nach Bindungspartnern (Schwingung-Schwingung → Elektron)
    finde_neue_elektronen(welt)
    
    # 4. Suche nach Bindungspartnern auf höheren Ebenen
    finde_hoehere_bindungen(welt)
    
    # 5. Zerfall instabiler Strukturen prüfen
    pruefe_zerfall(welt, dt)
    
    # 6. Aktualisierung der inneren Dynamik aller Knoten
    aktualisiere_innere_dynamik(welt, dt)
```

### Performance

Für Echtzeitfähigkeit:

- **Numba** (`@njit`) für die heißen Schleifen — Bewegungsupdate, Distanzberechnung, Bindungssuche.
- **Räumliche Indexstruktur** (Spatial Hashing oder K-D-Baum) für effiziente Nachbarschaftssuche. Naive O(n²)-Vergleiche werden bei mehr als 1.000 Schwingungen zu langsam.
- **NumPy-Arrays** für Positionen, Geschwindigkeiten, Frequenzen — nicht Python-Listen.

Zielperformance: 60 Bilder/Sekunde mit 1.000 Schwingungen, 30 Bilder/Sekunde mit 10.000.

---

## Teil 3 — Visualisierung

### Bibliothek

**Pygame** als erste Wahl. Reines Python, einfaches Setup, ausreichend für die Größenordnungen, die wir anvisieren.

Falls später nötig: Wechsel zu **Pyglet/Arcade** (OpenGL-basiert, skaliert besser) oder **Pygame mit GPU-Beschleunigung über moderngl**.

### Darstellung

**Freie Schwingungen** als kleine Punkte (Radius 2–3 Pixel):
- Gerade Polarität: Blau (`#4A90E2`)
- Ungerade Polarität: Rot (`#E74C3C`)
- Größe leicht variierend mit Frequenz (logarithmisch skaliert)

**Elektronen** als ortsfeste Punkte mit leichtem Schein:
- Farbe: Gelb-Orange (`#F39C12`)
- Größe etwa 5 Pixel mit weichem Glow
- Pulsiert leicht (innere Aktivität visualisiert)

**Elektronenpaare** als zwei verbundene Elektronen mit dünner Linie:
- Linienfarbe: Hellgrau, transparent (`#CCCCCC` mit alpha=0.5)
- Visualisiert die instabile Verbindung

**Triaden** als drei verbundene Elektronen:
- Linien dichter, weniger transparent
- Andeutung eines Dreiecks

**Atome** als unmissverständliche Strukturen:
- Vier Elektronen mit dicken, durchgezogenen Verbindungslinien
- Heller Aura/Glow um das Ganze
- Farbe: Weiß (`#FFFFFF`) mit warmem Schein
- Sind die "Sterne" der Welt

**Bindungen höherer Ordnung** (Moleküle und darüber):
- Verbindungen werden mit zunehmender Hierarchieebene visuell prominenter
- Eigenfarben für verschiedene Größenordnungen

### Statistiken

Eine Info-Leiste am oberen Bildschirmrand zeigt:
- Anzahl freier Schwingungen
- Anzahl Elektronen
- Anzahl Paare / Triaden / Atome
- Anzahl Moleküle (wenn vorhanden)
- Aktuelle Simulationszeit
- Aktuelle FPS

Optional: ein kleines Frequenz-Histogramm in der Ecke.

### Steuerung

| Taste / Aktion | Funktion |
|---|---|
| Leertaste | Pause / Weiter |
| Pfeil hoch / runter | Geschwindigkeit erhöhen / verlangsamen |
| Mausrad | Zoom |
| Maus ziehen | Schwenken |
| Linksklick | Neue Schwingung an Mausposition einfügen |
| R | Reset |
| S | Speichern (Zustand auf Disk) |
| L | Laden |
| Esc | Beenden |

---

## Teil 4 — Anfangskonfiguration

Empfohlene Werte für den ersten Start. Diese werden nach den ersten Beobachtungen kalibriert.

```python
ANFANGS_KONFIGURATION = {
    'anzahl_schwingungen': 1000,
    'frequenz_min': 100.0,           # Hz
    'frequenz_max': 10000.0,         # Hz
    'frequenz_verteilung': 'log',    # logarithmisch verteilt
    'raum_groesse': (1000.0, 1000.0),
    'geschwindigkeit_min': 10.0,     # Einheiten/Sekunde
    'geschwindigkeit_max': 50.0,
    'r_1': 5.0,                      # Distanz für Schwingung-Schwingung-Bindung
    'r_2': 10.0,                     # Distanz für Elektron-Elektron-Bindung
    'frequenz_toleranz': 0.005,      # 0.5% Toleranz für 8%-Regel
    'paar_zerfallszeit': 5.0,        # Sekunden
    'triade_zerfallszeit': 30.0,     # Sekunden
    'abstossung_konstante': 100.0,   # k in der Abstoßungsformel
    'polaritaet_verteilung': 0.5,    # 50% gerade, 50% ungerade
}
```

---

## Teil 5 — Erste Erwartungen und Kalibrierung

Beim ersten Start wirst du wahrscheinlich Probleme sehen:

- **Wenn keine Elektronen entstehen**: r_1 ist zu klein oder die 8%-Regel ist zu eng. Erhöhe r_1 oder die Frequenztoleranz.
- **Wenn zu viele Elektronen entstehen**: Reduziere r_1.
- **Wenn nie Atome entstehen**: Die Lebenszeit der Paare/Triaden ist zu kurz, oder die Dichte der Elektronen ist zu gering. Verlängere die Zerfallszeiten oder erhöhe die Anfangs-Schwingungszahl.
- **Wenn alles zu großen Klumpen verschmilzt**: Die Abstoßung ist zu schwach. Erhöhe die Abstoßungskonstante.

Plan zwei bis drei Stunden Kalibrierung ein, bevor die Welt produktiv wird.

---

## Teil 6 — Spätere Erweiterungen

Diese Spezifikation deckt nur die unteren Ebenen der Welt ab. Spätere Erweiterungen werden enthalten:

- **Moleküle** (mehrere Atome verbunden)
- **Membranen und Zellen-artige Strukturen**
- **Neuronen-Cluster** (aus Atomen und Molekülen aufgebaute funktionale Einheiten)
- **Synaptische Verbindungen** (Hebbsche Plastizität)
- **Aktivitätsmuster und Synchronisation**
- **Aufmerksamkeitsmechanismen**
- **Lern- und Gedächtnisstrukturen**

Das langfristige Ziel ist, gehirnartige Strukturen aus dieser Welt heraus zu entwickeln. Siehe dazu den begleitenden Skill `gehirn-aus-schwingungen`.

---

## Anhang — Implementierungs-Checkliste

Reihenfolge der Umsetzung:

1. **Grundgerüst** — Klassen, Datenstrukturen, leere Welt mit Visualisierungsfenster
2. **Schwingungen** — freie Bewegung, Visualisierung der Punkte
3. **Erste Bindung** — Elektronen entstehen aus Schwingungen
4. **Paare und Triaden** — Vor-Atom-Strukturen mit Zerfall
5. **Atome** — unzerstörbare 4er-Strukturen
6. **Skalen-Abstoßung** — räumliche Sortierung sichtbar machen
7. **Statistiken und Steuerung** — Info-Leiste, Pause, Reset, Speichern
8. **Performance-Optimierung** — Numba, räumliche Indexstruktur

Jeder Schritt sollte funktionierend abgeschlossen sein, bevor der nächste begonnen wird.

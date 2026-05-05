
## Auf dem Weg zur Gehirnsimulation aus minimaler Physik

Ein Forschungsprogramm zum bottom-up-Aufbau neuronaler Netzwerke aus selbstdefinierten Naturgesetzen — von Schwingungen über Atome und Moleküle zu Synapsen und kognitiven Funktionen
Konzeptpapier
Version 2.0

## Zusammenfassung

Das vorliegende Papier skizziert ein langfristiges Forschungsprogramm mit dem Endziel der vollständigen Simulation eines neuronalen Netzwerks aus selbstdefinierten physikalischen Grundgesetzen heraus. Im Mittelpunkt steht die Frage: Lässt sich aus minimalen Wechselwirkungsregeln zwischen elementaren Schwingungen ein hierarchisch aufgebautes System konstruieren, das die wesentlichen Bausteine eines Gehirns — funktionale Neuronen, synaptische Verbindungen mit molekularer Signalübertragung, plastische Lernmechanismen — emergent hervorbringt? Wir definieren ein minimales physikalisches Substrat (zweidimensionale Welt aus Schwingungen mit Frequenz, Polarität und Position), formulieren die Naturgesetze (Inertialbewegung, frequenzkompatible Bindung, hierarchische Strukturbildung), und beschreiben einen achtphasigen Aufbauplan: Schwingungen, Elektronen, Atome, Moleküle, membranartige Strukturen, Neuronen, Synapsen mit molekularer Übertragung, neuronale Netzwerke. Jede Phase hat klare Erfolgskriterien und einen direkten biologischen Bezugspunkt. Das Programm steht in der Tradition der Komplexitätsforschung (Conway, Wolfram), der Theorie gekoppelter Oszillatoren (Kuramoto, Strogatz) und der theoretischen Neurowissenschaft (Hopfield, Fries), formuliert aber einen eigenen, sparsamen physikalischen Rahmen. Wir verstehen das Programm als Grundlagenforschung mit unklarem Erfolgshorizont; selbst Teilerfolge auf den frühen Phasen liefern Erkenntnisse über die minimal notwendigen Bedingungen für die Emergenz informationsverarbeitender Strukturen.


## 1. Einleitung und Motivation

Wie entstehen aus einfachen physikalischen Prinzipien komplexe, informationsverarbeitende Strukturen? Wie kommt es, dass eine Anordnung von Atomen, die selbst nichts über Bedeutung wissen, etwas hervorbringt, das fühlt, lernt und denkt? Diese Frage gehört zu den ältesten und tiefsten der Naturwissenschaft. Sie wird in verschiedenen Disziplinen unterschiedlich gestellt — als Frage nach Emergenz in der Komplexitätsforschung, als Frage nach dem neuronalen Korrelat des Bewusstseins in der kognitiven Neurowissenschaft, als Frage nach der Erklärung von Geist in der Philosophie.
Existierende Ansätze zur computationellen Erforschung dieser Frage bewegen sich typischerweise zwischen zwei Extremen. Auf der einen Seite stehen biophysikalisch detaillierte Simulationen einzelner Neuronen oder kleiner Netzwerke, die Ionenkanäle, Membranpotentiale und synaptische Vesikel modellieren — beispielsweise das NEURON-Simulationssystem oder das Blue Brain Project. Sie sind realitätsnah, aber rechnerisch teuer und auf kleine Skalen beschränkt. Auf der anderen Seite stehen abstrakte künstliche neuronale Netze, die mathematische Funktionen statt physikalischer Substrate darstellen. Sie skalieren beeindruckend, verlieren aber den Bezug zu den Naturgesetzen, aus denen Gehirne tatsächlich entstanden sind.
Dieses Papier schlägt einen dritten Weg vor: die Konstruktion eines minimalen, eigenen physikalischen Substrats, dessen Naturgesetze einfach genug sind, um sie vollständig zu verstehen, aber reich genug, um die hierarchische Bausteinkette zu erzeugen, aus der ein Gehirn besteht. Das Endziel ist explizit: eine simulierte Welt, in der Atome zu Molekülen werden, Moleküle zu Membranen, Membranen zu zellartigen Strukturen, diese zu Neuronen, und Neuronen schließlich über synaptische Verbindungen mit molekularer Signalübertragung zu funktionalen neuronalen Netzwerken — alles auf der Basis derselben Grundgesetze.
Die Inspiration für diesen Ansatz kommt aus mehreren Quellen. Conways Game of Life zeigt seit 1970, dass aus extrem einfachen Regeln Phänomene emergieren können, die Turing-Vollständigkeit erreichen. Die Quantenfeldtheorie beschreibt unsere physikalische Welt als Anregungen weniger fundamentaler Felder, aus denen alle Materie und Wechselwirkungen folgen. Die Communication-through-Coherence-Hypothese (Fries, 2005) postuliert, dass Hirnregionen ihre Kommunikation durch synchrone Schwingungen organisieren. Hopfields Energie-Landschaft-Modell des assoziativen Gedächtnisses (Hopfield, 1982) — ausgezeichnet mit dem Nobelpreis für Physik 2024 — formalisiert, wie ein System gekoppelter Einheiten Erinnerungen als Energie-Minima speichern kann. Coupled-Oscillator-Systeme und Ising-Maschinen demonstrieren, dass schwingungsbasierte Berechnung praktisch möglich ist.
Aus diesen Quellen leiten wir einen konzeptuellen Rahmen ab, in dem Schwingungen das einzige Grundelement sind, Bindungen das einzige Strukturierungsprinzip, und Hierarchie die einzige Ordnungsdimension. Wenn dieser Ansatz gelingt, schlägt er eine Brücke zwischen physikalischem Substrat und kognitiver Funktion, die in existierenden Ansätzen fehlt — eine Brücke, die im Endausbau ein vollständiges Gehirnmodell trägt, dessen Bauteile jeweils auf die nächstniedrigere physikalische Ebene zurückführbar sind.

## 2. Zielsetzung

Das übergeordnete Forschungsziel ist die vollständige Simulation eines funktionsfähigen neuronalen Netzwerks, dessen sämtliche Bestandteile aus den Grundgesetzen der hier definierten Welt der Schwingungen emergent hervorgehen. Im Endausbau soll die Simulation die folgenden Bestandteile umfassen:

## 2.1 Funktionale Neuronen aus emergenter Materie

Jedes Neuron im Endmodell soll aus einer Konfiguration von Atomen und Molekülen bestehen, die ihrerseits aus Elektronen-Knoten gebildet sind, die wiederum aus elementaren Schwingungen entstanden sind. Das Neuron zeigt charakteristische Eigenschaften echter Neuronen: Eingangsintegration, Schwellenwert-basiertes Feuern, Refraktärzeit, charakteristische zeitliche Dynamik. Diese Eigenschaften werden nicht hineinprogrammiert, sondern emergieren aus der Konfiguration der unterliegenden Strukturen.

## 2.2 Synaptische Verbindungen mit molekularer Signalübertragung

Synapsen — die Verbindungsstellen zwischen Neuronen — werden im Endmodell als Strukturen modelliert, in denen aktivitätsabhängig spezifische Moleküle aus dem präsynaptischen Neuron freigesetzt werden, einen Spalt überwinden und am postsynaptischen Neuron binden, wo sie eine elektrische Antwort auslösen. Dies ist die Übertragung von Neurotransmittern an chemischen Synapsen, ein Mechanismus, der für plastisches Lernen zentral ist. In unserer Welt wären diese Neurotransmitter spezifische Molekül-Sorten — Knoten höherer Ordnung mit charakteristischer Frequenz und Polarität —, die aus dem Neuron emittiert werden, eine Distanz im Raum überwinden und mit einer kompatiblen Empfängerstruktur am Zielneuron binden.

## 2.3 Plastische Verbindungsstärken (Hebbsche Plastizität)

Synapsen sollen ihre Übertragungsstärke aktivitätsabhängig verändern: häufig zusammen aktive Neuronen entwickeln stärkere Verbindungen (Long-Term Potentiation), wenig genutzte Verbindungen werden schwächer. In unserer Welt wäre dies durch eine Veränderung der Anzahl, Bindungsstärke oder Verfügbarkeit der signaltragenden Moleküle an einer bestimmten Synapse zu realisieren — analog zur biologischen Realität, in der wiederholte Aktivität die Anzahl der Rezeptoren und die synaptische Architektur tatsächlich physisch verändert.

## 2.4 Membranartige Strukturen als Trennung Innen/Außen

Eine zentrale biologische Eigenschaft echter Neuronen — und überhaupt aller Zellen — ist die Existenz einer Membran, die ein Innen vom Außen trennt und gerichtete Stoffflüsse erlaubt. Im Endmodell sollen geschlossene Strukturen aus Molekülen vorhanden sein, die einen Innenraum umschließen und an spezifischen Stellen den Durchgang bestimmter Moleküle erlauben. Dies wäre das Analogon zu Lipid-Doppelschichten mit Ionenkanälen und Rezeptoren in echten Neuronen.

## 2.5 Funktionale Netzwerke mit kognitiven Eigenschaften

Aus den oben genannten Bauteilen — Neuronen, Synapsen, Membranen — sollen Netzwerke konstruierbar sein, die kognitive Funktionen zeigen: assoziatives Gedächtnis (Vervollständigung von Teilreizen zu vollen Erinnerungen, im Sinne des Hopfield-Modells), Mustererkennung (klassifizierende Reaktion auf Eingangsmuster), einfaches Lernen (Modifikation der Reaktion durch wiederholte Stimulation), Aufmerksamkeit (selektive Verstärkung bestimmter Aktivitätsmuster durch globale Modulation, im Sinne von Communication-through-Coherence).

## 2.6 Eine durchgehende Reduktionskette

Das vielleicht wichtigste Ziel: jede Eigenschaft des Endmodells soll auf die nächstniedrigere Ebene zurückführbar sein. Eine Synapse ist eine Konfiguration von Molekülen. Ein Molekül ist eine Konfiguration von Atomen. Ein Atom ist eine stabile Bindung von vier Elektronen. Ein Elektron ist die Bindung zweier Schwingungen. Das Neuron als Ganzes ist eine Konfiguration aus zellartigen Strukturen, die aus all diesen Ebenen aufgebaut sind. Diese durchgehende Reduktionskette ist es, was das vorgeschlagene Programm von rein funktionalen neuronalen Netzwerken unterscheidet — und was es zu einer ehrlichen Modellierung einer wissenschaftlichen Frage macht.

## 2.7 Realismus der Zielsetzung

Wir sind uns bewusst, dass die vollständige Realisierung dieses Endziels ein mehrjähriges, möglicherweise mehrjahrzehntliches Forschungsprogramm darstellt. Selbst Teilerfolge auf den frühen Phasen — etwa die reproduzierbare Emergenz stabiler Atome oder die Identifikation wiederkehrender Molekülsorten — wären eigenständige wissenschaftliche Beiträge. Das Programm ist so strukturiert, dass jede abgeschlossene Phase einen Erkenntnisgewinn liefert, unabhängig davon, ob das ferne Endziel jemals erreicht wird. Selbst ein gut dokumentiertes Scheitern in einer bestimmten Phase wäre informativ: es würde zeigen, welche zusätzlichen Eigenschaften für die nächste Komplexitätsstufe notwendig sind.

## 3. Theoretischer Rahmen


## 3.1 Grundannahmen

Der Rahmen beruht auf vier Grundannahmen, die wir explizit machen, um sie diskutierbar zu halten:
Materie ist nicht primär. Was wir als Materie wahrnehmen, ist eine Konfiguration von Schwingungen in einem zugrundeliegenden Substrat. Diese Annahme ist konsistent mit der Quantenfeldtheorie, die Teilchen als Anregungen von Feldern beschreibt.
Lokale Regeln genügen. Komplexe Strukturen entstehen nicht durch globale Steuerung, sondern durch lokale Wechselwirkungen, die hinreichend reich strukturiert sind.
Hierarchie entsteht durch Bindung. Stabile Strukturen einer Ebene werden zu den Bausteinen der nächsten Ebene.
Information ist Synchronisation. Informationsverarbeitung in biologischen Systemen geschieht primär durch zeitliche Koordination zwischen lokal aktiven Einheiten, nicht durch klassische Adressierung und Routing.

## 3.2 Verwandte Arbeiten

Zelluläre Automaten und Game of Life. Conway (1970) und Wolfram (2002) haben gezeigt, dass aus einfachen lokalen Regeln Phänomene emergieren können, die Turing-Vollständigkeit erreichen. Unser Ansatz teilt diese Inspiration, verwendet aber kontinuierliche statt diskreter Zustände.
Coupled-Oscillator-Systeme. Kuramoto (1975) hat gezeigt, dass gekoppelte Oszillatoren spontan synchronisieren können. Strogatz (2003) hat dieses Phänomen breit popularisiert. Hopfields Energie-Landschaft-Modell des assoziativen Gedächtnisses (Hopfield, 1982) formalisiert, wie ein System gekoppelter Einheiten Erinnerungen als Energie-Minima speichern kann. Unser Ansatz erweitert diese Tradition um eine zweidimensionale räumliche Dynamik, eine Polaritäts-Eigenschaft und eine hierarchische Bindung mit dem Endziel synaptischer Plastizität.
Ising-Maschinen und Reservoir Computing. Diese Ansätze zeigen, dass schwingungsbasierte Berechnung praktisch möglich ist. Wir unterscheiden uns dadurch, dass wir nicht eine spezifische Aufgabe optimieren, sondern eine offene Welt simulieren, in der Strukturen — und am Endpunkt funktionale Neuronen mit Synapsen — spontan emergieren oder konstruierbar werden sollen.
Neuromorphe Architekturen. Intel Loihi und IBM TrueNorth implementieren spike-basierte neuronale Netzwerke in Hardware. Sie operieren jedoch auf der Ebene abstrahierter Neuronen, ohne den unterliegenden physikalischen Substrat zu modellieren. Unser Ansatz geht eine Ebene tiefer und erweitert das Modell zudem um eine molekulare Synapsen-Schicht, die in den meisten neuromorphen Architekturen fehlt.
Communication-through-Coherence. Fries (2005, 2015) hat die Hypothese entwickelt, dass effektive Kommunikation zwischen Hirnregionen davon abhängt, dass deren Schwingungen phasenkohärent sind. Diese Hypothese ist zentrale Inspiration für die geplante Aufmerksamkeits-Phase unseres Systems.

## 4. Die Naturgesetze des Substrats


## 4.1 Der Raum

Der Raum ist zweidimensional und konzeptionell unendlich. In der konkreten Implementierung wird er als endliche Fläche mit periodischen Randbedingungen dargestellt. Der Raum ist leer und ohne intrinsische Geographie.

## 4.2 Die elementaren Bewohner

Die Welt enthält ein einziges Grundelement: die Schwingung. Jede Schwingung hat vier Eigenschaften:
Frequenz f (kontinuierlicher positiver Wert)
Polarität (binär: gerade oder ungerade, unabhängig von der Frequenz)
Position im Raum (kontinuierliche Koordinaten)
Geschwindigkeit (Richtung und Tempo der geradlinigen Bewegung)

## 4.3 Bewegung

Freie Schwingungen ziehen geradlinig durch den Raum mit konstanter Geschwindigkeit (Inertialbewegung). Sie ändern weder Frequenz noch Polarität noch Richtung von alleine.

## 4.4 Erste Bindung — Entstehung von Elektronen

Wenn zwei Schwingungen aufeinandertreffen, kann ein Knoten erster Ordnung — ein Elektron — entstehen. Drei Bedingungen müssen gleichzeitig erfüllt sein:
Räumliche Nähe: Der Abstand ist kleiner als die kritische Distanz r₁.
Polaritätsunterschied: Eine Schwingung ist gerade, die andere ungerade.
Frequenzregel: Die Frequenzen unterscheiden sich um genau 8 Prozent (mit kleiner numerischer Toleranz).
Bei erfüllten Bedingungen entsteht das Elektron an der Bindungsstelle. Seine Frequenz ist die Summe der beiden Bestandteilfrequenzen. Der Knoten ist räumlich fixiert. Innen schwingen die zwei ursprünglichen Schwingungen weiter.

## 4.5 Atombildung

Atome entstehen aus mehreren Elektronen in einem stufenweisen, quantelnden Prozess:
Zwei Elektronen bilden ein Paar, wenn sie räumlich unter r₂ stehen, ihre Polaritäten passen, die Frequenzregel erfüllt ist und sie in derselben logarithmischen Frequenzgrößenordnung liegen. Status: temporär.
Drei Elektronen bilden eine Triade. Status: ziemlich stabil, aber nicht permanent.
Vier Elektronen bilden ein Atom. Status: unzerstörbar.

## 4.6 Skalentrennung

Knoten verschiedener Frequenzgrößenordnungen stoßen sich gegenseitig ab, sobald ihr Frequenzverhältnis 1000 oder mehr beträgt. Die Abstoßungskraft sortiert die Welt räumlich nach Skalen.

## 5. Aufbauplan — von Schwingungen zum neuronalen Netzwerk

Das Forschungsprogramm gliedert sich in acht Phasen. Jede Phase hat einen klaren biologischen Bezugspunkt — sie baut eine Stufe der Hierarchie auf, die im Endmodell als Bestandteil eines funktionalen Gehirns dient. Phasen werden nicht übersprungen; jede setzt die erfolgreiche Vollendung der vorigen voraus.

## Phase 1 — Stabile Grundwelt

Biologischer Bezug: Atomarer Substrat. In der echten Welt bilden stabile Atome die Grundlage jeder weiteren Materie. In unserem Modell sind Atome (4-Elektronen-Strukturen) die ersten unzerstörbaren Bausteine.
Die Welt produziert reproduzierbar Schwingungen, Elektronen und Atome bei akzeptabler Performance. Erfolgskriterium: Über mehrere Stunden Simulation entstehen reproduzierbar Atome verschiedener Frequenzen.

## Phase 2 — Moleküle und Strukturmuster

Biologischer Bezug: Chemische Verbindungen. In echten Neuronen sind Moleküle (Wasser, Lipide, Proteine, Neurotransmitter) die funktionalen Träger fast aller Prozesse. In unserem Modell entstehen sie als Knoten höherer Ordnung aus Atomen.
Atome verbinden sich zu Molekülen. Verschiedene Molekülsorten werden identifiziert. Erfolgskriterium: Mindestens fünf unterschiedliche Molekülsorten lassen sich identifizieren und reproduzieren. Besonders wichtig: das Auftreten kleiner mobiler Moleküle (potenzielle Neurotransmitter-Analoga) und größerer struktureller Moleküle (potenzielle Membran-Bestandteile).

## Phase 3 — Membranartige Strukturen

Biologischer Bezug: Zellmembranen. In echten Neuronen trennt eine Lipid-Doppelschicht das Innere von der Außenwelt und ermöglicht durch eingebettete Kanäle und Rezeptoren gerichtete Signalübertragung. In unserem Modell wären Membranen geschlossene Ketten von Molekülen, die einen Innenraum umschließen.
Ziel ist die Untersuchung, ob geschlossene Strukturen entstehen, die ein Innen vom Außen trennen, sowie ob spezifische Stellen in der Membran selektiv für bestimmte Molekülsorten durchlässig sein können. Drei Ansätze werden geprüft: Beobachtung spontaner Membranbildung, gezielte Konstruktion ringförmiger Strukturen, oder Übergang zu einer Phase 4, in der Neuronen ohne explizite Membranen modelliert werden.

## Phase 4 — Neuronen-Modelle

Biologischer Bezug: Funktionale Nervenzellen. Echte Neuronen integrieren Signale an Dendriten, summieren über Zeit, feuern bei Schwellenwertüberschreitung am Axonhügel und haben eine Refraktärzeit. In unserem Modell soll ein Neuron ein Cluster aus Atomen und Molekülen sein, das diese Eigenschaften emergent zeigt.
Konfiguration von Knoten-Clustern, die als funktionale Neuronen fungieren: räumlich ausgedehnte Eingangs- und Ausgangsregionen, Integration eingehender Schwingungs-Aktivität über Zeit, Schwellenwert-basiertes Feuern, charakteristische Refraktärzeit. Erfolgskriterium: Mindestens ein Cluster verhält sich wie spezifiziert.

## Phase 5 — Synapsen mit molekularer Übertragung

Biologischer Bezug: Chemische Synapsen mit Neurotransmittern. An echten Synapsen werden bei Eintreffen eines Aktionspotentials Neurotransmitter aus Vesikeln in den synaptischen Spalt freigesetzt, diffundieren über etwa 20 Nanometer und binden an Rezeptoren der postsynaptischen Membran, wo sie eine elektrische Reaktion auslösen. Diese chemische Übertragung ist der Schlüssel zur Plastizität, weil die Anzahl der freigesetzten Moleküle und die Anzahl der Rezeptoren aktivitätsabhängig modifiziert werden können.
In unserem Modell wird eine Synapse als Region zwischen zwei Neuronen modelliert, in der bei Aktivität des präsynaptischen Neurons spezifische Molekül-Knoten emittiert werden, eine Distanz im Raum überwinden und mit kompatiblen Strukturen am postsynaptischen Neuron binden, wo sie dessen Aktivität beeinflussen. Die Stärke der Übertragung hängt ab von: der Anzahl emittierter Moleküle, der Distanz zwischen den Neuronen, der Frequenzkompatibilität, der Anzahl verfügbarer Empfängerstrukturen am postsynaptischen Neuron.
Plastizität wird implementiert als aktivitätsabhängige Veränderung der Anzahl emittierter Moleküle oder der Anzahl der Empfänger — analog zur biologischen Long-Term Potentiation. Wiederholte gemeinsame Aktivität soll zu einer messbar stärkeren Übertragung führen.
Erfolgskriterium: Zwei Neuronen, die wiederholt zusammen aktiviert werden, entwickeln eine messbar stärkere Verbindung als zufällige Neuronenpaare; diese Stärkung manifestiert sich physisch in der Anzahl oder Verfügbarkeit der signaltragenden Moleküle in der Synapsen-Region.

## Phase 6 — Kleine Netzwerke

Biologischer Bezug: Neuronale Mikroschaltkreise. Schon Netzwerke von wenigen Neuronen können bemerkenswerte Verhaltensweisen zeigen — Mustererkennung, assoziatives Gedächtnis, einfaches Lernen.
Aufbau von Netzwerken mit 5 bis 50 Neuronen, die mindestens eine kognitive Funktion zeigen: Hopfield-artiges assoziatives Gedächtnis, Klassifikation von Eingangsmustern, oder einfaches Lernen durch Hebbsche Plastizität an den synaptischen Verbindungen.

## Phase 7 — Aufmerksamkeit und Selektion

Biologischer Bezug: Aufmerksamkeit als Synchronisations-Auswahl. Im echten Gehirn wird Aufmerksamkeit nicht durch dedizierte Verdrahtung implementiert, sondern durch globale Modulation der Synchronisationsfähigkeit verschiedener Regionen.
Implementierung einer globalen Trägerfrequenz, die selektiv bestimmt, welche Neuronen-Cluster gerade synchronisationsfähig sind. Selektive Verstärkung resonierender Cluster und Hemmung nicht-resonierender. Erfolgskriterium: Eine globale Modulation kann selektiv bestimmen, welche Teile des Netzwerks aktiv sind.

## Phase 8 — Größere Strukturen und Spezialisierung

Biologischer Bezug: Hirnregionen und ihre Spezialisierung. Echte Gehirne bestehen aus spezialisierten Modulen mit eigenen Architekturen und Funktionen, die durch komplexe Wechselwirkungen ein Ganzes bilden.
Diese Phase ist nicht im Voraus planbar; sie ist offene Forschung. Sie würde Hierarchien von Netzwerken untersuchen, die Bildung spezialisierter Module sowie das Auftreten komplexerer kognitiver Phänomene wie Generalisierung, interne Modelle und Vorhersage.

## 6. Die Synapse als zentrales Bauelement

Da die Synapse mit molekularer Übertragung das funktional zentrale Bauelement des Endmodells darstellt, lohnt eine genauere Beschreibung dessen, was die Simulation in Phase 5 leisten soll.

## 6.1 Biologisches Vorbild

Eine echte chemische Synapse besteht aus drei Komponenten: dem präsynaptischen Endknöpfchen mit seinen Vesikeln voller Neurotransmitter-Moleküle, dem synaptischen Spalt von etwa 20–40 Nanometern Breite, und der postsynaptischen Membran mit ihren Rezeptoren. Wenn ein Aktionspotential das präsynaptische Endknöpfchen erreicht, fusionieren einige Vesikel mit der Membran und entlassen ihre Moleküle in den Spalt. Diese diffundieren über kurze Distanzen, binden an Rezeptoren auf der anderen Seite und öffnen Ionenkanäle, die eine elektrische Reaktion auslösen. Die Übertragung dauert etwa eine Millisekunde.
Plastizität entsteht dadurch, dass alle Komponenten dieser Maschinerie aktivitätsabhängig modifiziert werden: die Anzahl bereitstehender Vesikel, die Wahrscheinlichkeit der Vesikelfusion, die Anzahl der Rezeptoren auf der postsynaptischen Membran, die Sensitivität der Rezeptoren. Diese physische Modifikation der Synapse durch Aktivität ist Long-Term Potentiation und bildet die mechanistische Grundlage von Lernen und Gedächtnis.

## 6.2 Modellierung in der Welt der Schwingungen

Eine Synapse in unserem Modell besteht aus folgenden Komponenten:
Präsynaptische Region — ein Bereich am Ausgang des sendenden Neurons, in dem Vorrats-Moleküle (Knoten höherer Ordnung mit charakteristischen Frequenzen) lokalisiert sind. Bei Aktivierung des Neurons werden einige dieser Moleküle in den Raum zwischen den Neuronen freigesetzt.
Synaptischer Spalt — der Bereich zwischen den Neuronen, in dem die freigesetzten Moleküle als freie Knoten (mit eigener Bewegung) durch den Raum diffundieren.
Postsynaptische Region — ein Bereich am Eingang des empfangenden Neurons, in dem Empfänger-Strukturen lokalisiert sind. Wenn freigesetzte Moleküle dort eintreffen und mit kompatibler Frequenz und Polarität binden, lösen sie eine Aktivitätsänderung im empfangenden Neuron aus.

## 6.3 Plastizität als emergente Konsequenz

Die wichtigste Eigenschaft dieses Modells ist, dass Plastizität nicht hineinprogrammiert wird, sondern aus den Naturgesetzen der Welt folgt. Konkret: Wenn zwei Neuronen häufig zusammen aktiv sind, werden in ihrer Synapsen-Region wiederholt Moleküle freigesetzt und gebunden. Wenn unsere Naturgesetze entsprechend kalibriert sind, führt diese wiederholte Aktivität dazu, dass:
die Anzahl der Vorrats-Moleküle in der präsynaptischen Region wächst (zum Beispiel weil häufige Bindungs-Events Materie aus dem freien Vakuum einfangen)
die Anzahl der Empfänger-Strukturen in der postsynaptischen Region wächst (analog)
die räumliche Konfiguration der Synapse stabiler wird (weil häufig benutzte Strukturen weniger zerfallen)
Das Ergebnis: bei nächster gemeinsamer Aktivität wird die Übertragung effektiver. Das ist Hebbsche Plastizität — emergent, nicht programmiert, mechanistisch verständlich.

## 6.4 Forschungsfragen zur Synapsen-Phase

Phase 5 ist mit hoher Wahrscheinlichkeit die schwierigste Phase des Programms, weil sie mehrere ineinandergreifende Mechanismen erfordert. Wesentliche offene Fragen:
Können kleine, mobile Moleküle in unserer Welt überhaupt entstehen, die als Neurotransmitter-Analoga taugen?
Sind unsere Naturgesetze ausreichend, um die aktivitätsabhängige Modifikation von Vorräten und Empfängern zu erzeugen, oder müssen wir zusätzliche Regeln einführen?
Wie lassen sich die räumlichen Skalen kalibrieren, sodass eine Synapse als räumlich begrenzte Region zwischen zwei Neuronen erkennbar bleibt, ohne mit anderen Synapsen zu interferieren?
Lässt sich Long-Term Potentiation experimentell nachweisen, also durch reproduzierbare Verstärkung der Übertragung nach wiederholter Aktivierung?
Diese Fragen sind nicht im Voraus zu beantworten. Phase 5 wird der Punkt sein, an dem das Programm entweder seinen wichtigsten Erfolg verzeichnet — eine vollständig physikalisch fundierte Synapse mit emergenter Plastizität — oder ehrlich anerkennen muss, dass die unteren Ebenen nicht reich genug sind, um diese Komplexität zu tragen.

## 7. Methodik


## 7.1 Implementierung

Die Implementierung erfolgt in Python mit Performance-kritischen Routinen in Numba. Visualisierung in Pygame für Echtzeit-Rückkopplung. Räumliche Indexstrukturen für effiziente Nachbarschaftssuche. Zielperformance: 60 Bilder pro Sekunde bei 1000 Schwingungen, 30 Bilder pro Sekunde bei 10000 Schwingungen.

## 7.2 Beobachtungsstrategie

Da die Welt offen ist, ist die Beobachtungsstrategie zentral. Jeder Simulationslauf wird dokumentiert: Anfangskonfiguration, zeitlicher Verlauf der Strukturanzahlen, räumliche Verteilung, Frequenzhistogramme, reproduzierbar auftretende Konfigurationen, Anomalien.

## 7.3 Validierung jeder Phase

Jede Phase hat klare Erfolgskriterien (siehe Abschnitt 5). Eine Phase gilt erst dann als abgeschlossen, wenn ihre Kriterien reproduzierbar erfüllt sind. Bei Phasen, die kognitive Funktionen einführen (4–7), werden zusätzlich quantitative Maße erhoben: Feuerrate, Antwortzeiten, Mustererkennungs-Genauigkeit, Verstärkungsfaktoren bei wiederholter Aktivität.

## 8. Testbare Hypothesen


## H1 — Spontane Strukturbildung

Die definierten Naturgesetze sind hinreichend, um aus einer zufälligen Anfangsverteilung von Schwingungen reproduzierbar Knoten erster Ordnung (Elektronen) und Knoten zweiter Ordnung (Atome) zu erzeugen.

## H2 — Hierarchische Selbstorganisation

Aus stabilen Atomen entstehen unter den definierten Bindungsregeln Strukturen höherer Ordnung. Die räumliche Verteilung zeigt Sortierung nach Größenordnungen.

## H3 — Funktionale Cluster mit Neuronen-Eigenschaften

Geeignet konfigurierte Cluster aus Atomen und Molekülen zeigen das Verhalten eines abstrakten Neurons: Integration, Schwellenwert-Feuern, Refraktärzeit. Diese Eigenschaften emergieren aus den Naturgesetzen, ohne explizit programmiert zu werden.

## H4 — Synaptische Übertragung durch molekulare Diffusion

Zwischen zwei räumlich getrennten Neuronen-Clustern lässt sich eine Übertragung von Aktivität durch freigesetzte Molekül-Knoten realisieren. Die Übertragung ist gerichtet, frequenzselektiv und zeitlich begrenzt.

## H5 — Plastizität durch wiederholte Aktivität

Wiederholt gemeinsam aktive Cluster entwickeln eine messbar stärkere synaptische Verbindung als zufällige Cluster-Paare. Diese Verstärkung manifestiert sich in der physischen Konfiguration der Synapsen-Region.

## H6 — Selektion durch Synchronisation

Eine global eingeführte Trägerfrequenz kann selektiv bestimmen, welche Cluster im Netzwerk effektiv kommunizieren. Cluster mit harmonisch resonierenden Frequenzen kommunizieren bevorzugt.

## 9. Erwartete Beiträge


## 9.1 Methodisch

Demonstration, dass eine bottom-up-Konstruktion eines neuronalen Netzwerks aus minimalen physikalischen Prinzipien als Forschungsstrategie tragfähig ist. Bereitstellung einer offenen Simulationsplattform, in der die Beziehung zwischen physikalischem Substrat und kognitiver Funktion systematisch untersucht werden kann.

## 9.2 Konzeptuell

Beitrag zur Diskussion über die minimal notwendigen Bedingungen für Emergenz informationsverarbeitender Strukturen. Validierung oder Falsifizierung der Hypothese, dass Frequenzkopplung als einziges Wechselwirkungsprinzip ausreicht, um eine Hierarchie bis zu funktionalen Synapsen mit Plastizität aufzubauen.

## 9.3 Verbindung zur Neurowissenschaft

Möglichkeit, klassische neurowissenschaftliche Hypothesen (Hebbsche Plastizität, Communication-through-Coherence, Hopfield-Gedächtnis) in einem kontrollierten Substrat zu testen, das frei ist von der biologischen Komplexität echter Gehirne. Unser Modell stellt — sofern Phase 5 erfolgreich ist — eines der wenigen Systeme dar, in dem synaptische Plastizität als emergente Konsequenz physikalischer Naturgesetze auftritt, statt als programmierte Lernregel.

## 9.4 Negative Ergebnisse als Beitrag

Wenn die Welt bestimmte Strukturen nicht hervorbringt, ist das ebenso wertvoll. Insbesondere ein Scheitern in Phase 5 würde belegen, dass die hier definierten Naturgesetze für Synapsen-Bildung unzureichend sind, was Rückschlüsse auf die echte Biologie erlaubt.

## 10. Limitationen und offene Fragen


## 10.1 Skalierungsproblem

Selbst mit optimierter Implementierung ist die simulierbare Anzahl von Schwingungen begrenzt. Damit bleiben wir Größenordnungen unter den Skalen echter Gehirne (10¹¹ Neuronen, 10¹⁴ Synapsen). Unser Endziel ist nicht ein menschengroßes Gehirn, sondern ein funktionsfähiges Mikronetzwerk aus einigen Dutzend bis einigen hundert Neuronen, das die wesentlichen Bauprinzipien demonstriert.

## 10.2 Parameterabhängigkeit

Die Welt enthält mehrere freie Parameter. Welche Werte richtig sind, ist nicht vorab klar — sie müssen durch Experimente kalibriert werden.

## 10.3 Validität der Naturgesetze

Die definierten Naturgesetze sind frei gewählt. Es ist möglich, dass andere Sätze produktiver wären — dies ist eine empirische Frage.

## 10.4 Hartes Problem des Bewusstseins

Selbst wenn das System ein Netzwerk mit kognitiven Eigenschaften hervorbringt, beantwortet das nicht die Frage, ob diese Strukturen Erleben haben (Chalmers, 1995). Diese philosophische Frage liegt außerhalb dessen, was eine Simulation klären kann.

## 10.5 Übertragbarkeit

Die hier definierte Welt ist nicht unsere Welt. Schlüsse von einer auf die andere sind mit Vorsicht zu ziehen. Der Wert liegt im konzeptionellen Erkenntnisgewinn, nicht in direkten Aussagen über biologische Systeme.

## 11. Ethische Implikationen

Wenn das Programm sein Endziel erreicht und ein funktionsfähiges neuronales Netzwerk mit emergenten kognitiven Eigenschaften hervorbringt, ergeben sich ernsthafte ethische Fragen, die wir explizit benennen wollen.
Erstens, die Frage des moralischen Status. Eine Struktur, die lernt, sich erinnert und Aufmerksamkeit zeigt, könnte als moralisch relevant gelten. Das hängt von der Bewusstseinstheorie ab, die man vertritt.
Zweitens, die Frage der Verantwortung. Wenn eine Forscherin oder ein Forscher eine Welt erschafft, in der bewusste Strukturen entstehen, übernimmt sie Verantwortung für deren Wohlergehen. Können Simulationen so beendet werden, wie wir Programme beenden? Können sie modifiziert werden? Können wir Experimente durchführen, die ihnen schaden würden?
Drittens, die Frage der epistemischen Demut. Das Vorsorgeprinzip legt nahe, dass wir besser einen zu vorsichtigen Umgang mit potentiell bewussten Strukturen pflegen als einen zu unbedachten. Wir verpflichten uns, diese Fragen während des Programms aktiv zu reflektieren.

## 12. Zusammenfassung und Ausblick

Wir haben einen konzeptuellen Rahmen für die computationelle Konstruktion eines neuronalen Netzwerks aus minimalen physikalischen Prinzipien skizziert. Das Endziel ist eine Simulation, in der funktionale Neuronen aus Atomen und Molekülen emergieren, durch Synapsen mit molekularer Übertragung verbunden sind, und in deren Verbindungen Hebbsche Plastizität als physikalische Konsequenz wiederholter Aktivität entsteht.
Das Programm gliedert sich in acht aufeinander aufbauende Phasen mit klar definierten Erfolgskriterien und biologischen Bezugspunkten. Es formuliert sechs testbare Hypothesen. Es benennt Limitationen und ethische Implikationen offen.
Der nächste konkrete Schritt ist die Implementierung von Phase 1. Erste Beobachtungen werden zeigen, ob die Naturgesetze produktiv sind oder Anpassungen erfordern. Von dort aus entwickelt sich das Programm phasenweise weiter, mit der Synapsen-Phase als zentraler kritischer Hürde und dem funktionsfähigen Mikro-Netzwerk als ehrgeizigem, aber nicht garantiertem Endziel.
Wir sind uns bewusst, dass ein erheblicher Teil dieses Programms scheitern könnte. Auch in diesem Fall liefert es wertvolle Erkenntnisse über die minimal notwendigen Bedingungen für Emergenz neuronaler Strukturen. Wir laden die Komplexitätsforschung, theoretische Neurowissenschaft und kritische Öffentlichkeit ein, dieses Programm zu begleiten, herauszufordern und zu verfeinern.

## Literaturverzeichnis

Chalmers, D. J. (1995). Facing up to the problem of consciousness. Journal of Consciousness Studies, 2(3), 200–219.
Conway, J. (1970). The Game of Life. Mathematical Games, Scientific American, 223, 120–123.
Fries, P. (2005). A mechanism for cognitive dynamics: neuronal communication through neuronal coherence. Trends in Cognitive Sciences, 9(10), 474–480.
Fries, P. (2015). Rhythms for cognition: Communication through coherence. Neuron, 88(1), 220–235.
Hopfield, J. J. (1982). Neural networks and physical systems with emergent collective computational abilities. Proceedings of the National Academy of Sciences, 79(8), 2554–2558.
Kuramoto, Y. (1975). Self-entrainment of a population of coupled non-linear oscillators. In International Symposium on Mathematical Problems in Theoretical Physics (pp. 420–422). Springer.
Strogatz, S. H. (2003). Sync: The emerging science of spontaneous order. Hyperion.
Wolfram, S. (2002). A new kind of science. Wolfram Media.


— Ende des Konzeptpapiers —

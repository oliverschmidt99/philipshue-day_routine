# Philips Hue Tageslicht- und Anwesenheitssteuerung

Dieses Projekt ist eine Python-basierte Anwendung zur intelligenten Steuerung von Philips Hue Lampen. Es kombiniert zeitgesteuerte Tageslicht-Simulationen mit einer Anwesenheits- und Helligkeitserkennung, um eine vollautomatische und energieeffiziente Beleuchtung zu realisieren. Die Steuerung und Konfiguration erfolgt bequem über eine Web-Oberfläche.

---

## Features

- **Dynamische Tagesabläufe:** Definiere verschiedene Lichtszenen für Morgen, Tag, Abend und Nacht.
- **Anwesenheitserkennung:** Nutzt Hue Bewegungssensoren, um Lichter bei Bewegung zu aktivieren und nach einer einstellbaren Zeit wieder in den Normalzustand zu versetzen.
- **Intelligente Helligkeitsregelung:** Eine adaptive Fading-Logik passt die Lampenhelligkeit dynamisch an das Umgebungslicht an.
- **Datenanalyse:** Speichert Verlaufsdaten von Sensoren (Helligkeit, Temperatur) in einer lokalen Datenbank und stellt sie in Diagrammen dar.
- **Web-Oberfläche:** Eine moderne und intuitive Oberfläche zur Konfiguration aller Routinen, Szenen und zur Analyse der Daten.
- **Echtzeit-Status:** Live-Ansicht des Systemzustands und der Log-Dateien.

---

## Installation & Start

1.  **Abhängigkeiten installieren:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Konfiguration anpassen:**

    - Benenne `config.example.yaml` in `config.yaml` um.
    - Trage die IP-Adresse deiner Hue Bridge ein.
    - Drücke den Link-Button auf deiner Bridge.
    - Führe das Skript einmal aus, um die `phue`-Bibliothek zu autorisieren.

3.  **Anwendung starten:**

    ```bash
    python main.py
    ```

4.  **Web-Oberfläche öffnen:**
    - Öffne einen Browser und gehe zu `http://<IP-deines-Servers>:5000`.

---

## Die Web-Oberfläche im Detail

Die Oberfläche ist in mehrere Reiter (Tabs) unterteilt:

### Routinen

Hier ist das Herzstück der Konfiguration. Eine Routine verknüpft einen Raum mit einem Zeitplan und optional einem Sensor.

- **Neue Routine erstellen:** Definiert eine neue Routine für einen Raum und einen Bewegungssensor.
- **Bearbeiten:** Öffnet den Detail-Editor für eine bestehende Routine.
- **Ablauf (Ansichtsmodus):** Zeigt eine Zusammenfassung der Einstellungen für die vier Zeitabschnitte:
  - **Morning (Morgen):** Sonnenaufgang bis 12:00 Uhr
  - **Day (Tag):** 12:00 Uhr bis Sonnenuntergang
  - **Evening (Abend):** Sonnenuntergang bis 23:00 Uhr
  - **Night (Nacht):** 23:00 Uhr bis Sonnenaufgang

### Szenen

Hier definierst du die eigentlichen Lichtstimmungen. Eine Szene ist eine Sammlung von Einstellungen (Helligkeit, Farbe, Farbtemperatur), die auf eine Lampengruppe angewendet werden kann.

### Status

Dieser Reiter gibt dir einen Live-Einblick in das, was das System gerade tut.

- **Live-Zustand:** Zeigt für jede Routine den aktuellen Zeitraum (period), die zuletzt geschaltete Szene und den Status des Bewegungsmelders an.
- **Log-Datei:** Zeigt die letzten Einträge aus der `info.log`-Datei an. Ideal zur Fehlersuche.

### Analyse (Blau)

Hier werden die von den Sensoren gesammelten Daten visualisiert.

- **Sensorauswahl:** Wähle einen deiner verfügbaren Bewegungssensoren aus.
- **Datumsauswahl:** Wähle den Tag, Monat oder das Jahr, das du analysieren möchtest.
- **Diagramm:** Zeigt den Verlauf von Helligkeit (lightlevel) und Temperatur (°C) über den gewählten Zeitraum an.

### Einstellungen (Grün)

Dieser Bereich ist für zukünftige globale Einstellungen reserviert, z.B. für die Konfiguration der Datenbank oder des Log-Levels.

### Hilfe (Gelb)

Zeigt diese `README.md`-Datei an, damit du die Dokumentation immer zur Hand hast.

---

## Die Steuerungslogik im Detail

Die Logik der Routine folgt einer klaren Hierarchie von Prioritäten, um zu entscheiden, welche Aktion ausgeführt wird. Bei jedem Durchlauf der Hauptschleife (ca. jede Sekunde) wird für jede Routine folgende Kette abgearbeitet:

### Priorität 1: Bewegungserkennung

- **Bedingung:** Ist die Bewegungs-Erkennung für den aktuellen Zeitraum (`motion_check`) aktiviert und wird gerade eine Bewegung erkannt (`get_motion() == True`)?
- **Aktion:** Ja? Dann wird sofort die für diesen Fall definierte Bewegungs-Szene (`x_scene_name`) aktiviert. Der interne Zustand wechselt zu `MOTION`. Alle nachfolgenden Logik-Schritte werden für diesen Durchlauf übersprungen.

### Priorität 2: Timeout nach Bewegung

- **Bedingung:** Befindet sich die Routine im Zustand `MOTION` und ist die eingestellte Wartezeit (`wait_time`) seit der letzten Bewegung abgelaufen?
- **Aktion:** Ja? Der Zustand wird auf `RESET` gesetzt. Dies zwingt die Logik im nächsten Durchlauf, die Situation neu zu bewerten und entweder die Helligkeitsregelung zu starten oder die Standard-Szene zu setzen.

### Priorität 3: Adaptive Helligkeitsregelung (Fading)

- **Bedingung:** Ist die Helligkeitsprüfung (`bri_check`) für den aktuellen Zeitraum aktiviert?
- **Aktion:** Die `_handle_brightness_control`-Methode wird ausgeführt. Diese implementiert eine inverse lineare Regelung mit Hysterese (Schmitt-Trigger).
  - **Hysterese:**
    - **Einschalt-Schwelle (`threshold_low`):** Dein konfigurierter Wert `max_light_level`. Fällt die Umgebungshelligkeit unter diesen Wert, wird die Regelung aktiv.
    - **Ausschalt-Schwelle (`threshold_high`):** `threshold_low * 1.25`. Steigt die Helligkeit über diesen höheren Wert, wird das Licht garantiert ausgeschaltet. Der Bereich dazwischen ist eine "tote Zone", in der keine Änderung erfolgt, um ein Flackern zu verhindern.
  - **Inverse Regelung (Fading):**
    - Wenn die Regelung aktiv ist, wird die Helligkeit der Lampe (`bri`) nach folgender Formel berechnet:
      $$bri = 1 + \left( 253 \cdot \frac{\text{threshold\_low} - \text{lightlevel}}{\text{threshold\_low}} \right)$$
    - Je dunkler die Umgebung (kleiner `lightlevel`), desto heller wird die Lampe (größer `bri`).
    - Um einen Farbwechsel zu vermeiden, wird beim ersten Aktivieren die komplette Szene gesetzt und bei nachfolgenden Anpassungen nur noch der `bri`-Wert an die Lampe gesendet.

### Priorität 4: Standard-Szene

- **Bedingung:** Wenn keine der obigen Bedingungen zutrifft (keine Bewegung, kein Timeout, keine aktive Helligkeitsregelung).
- **Aktion:** Die Routine setzt die Normal-Szene (`scene_name`), die für den aktuellen Zeitraum (day, night, etc.) konfiguriert ist. Dies geschieht nur einmal beim Wechsel in einen neuen Zustand, um unnötige Befehle zu vermeiden.

---

## Datenaufzeichnung

Ein separater `data_logger_thread` läuft im Hintergrund und ist für die Messwerterfassung zuständig.

- **Intervall:** Alle 15 Minuten.
- **Aktion:** Liest für jeden konfigurierten Sensor die aktuelle Helligkeit und Temperatur aus.
- **Speicherung:** Schreibt die Werte mit einem Zeitstempel in die lokale SQLite-Datenbank `sensor_data.db`.
- **Effizienz:** Dieser Prozess läuft unabhängig von der Haupt-Steuerungsschleife, um diese nicht zu blockieren.

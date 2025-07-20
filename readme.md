# Philips Hue Advanced Routine Controller

Ein Python-basiertes Steuerungssystem für Philips Hue, das zeit- und sensorbasierte Routinen über eine Web-UI ermöglicht. Das System nutzt eine modulare Architektur zur einfachen Erweiterung und Wartung.

## Core Features

- **Modulare Routine-Engine:** Jede Routine operiert unabhängig und kombiniert Zeitpläne (Morgen, Tag, Abend, Nacht) mit Sensor-Triggern (Bewegung, Helligkeit).
- **Zustandsbasierte Logik:** Eine robuste State-Machine (Normal, Bewegung, Inaktiv) handhabt Übergänge und sorgt für Systemstabilität und vorhersagbares Verhalten.
- **Adaptive Helligkeitsregelung:** Implementiert eine inverse lineare Regelung mit einstellbarer Hysterese, um die Beleuchtung an das Umgebungslicht anzupassen und Flackern bei Grenzwerten zu vermeiden.
- **Dynamische Zeitsteuerung:** Die Zeitabschnitte können an feste Uhrzeiten oder dynamisch an den Sonnenauf- und -untergang gekoppelt werden, basierend auf dem Standort des Nutzers.
- **Datenpersistenz & Analyse:** Sensorwerte (Helligkeit, Temperatur) werden in einer SQLite-Datenbank gespeichert und über eine `Flask`-basierte API für die Visualisierung mit Chart.js bereitgestellt.
- **Web-Interface:** Eine auf Vanilla JS und Tailwind CSS basierende Single-Page-Application dient der vollständigen Konfiguration von Routinen, Szenen und globalen Systemeinstellungen.

## Systemarchitektur

Das Projekt ist in mehrere Kernkomponenten unterteilt:

- `main.py`: Der Einstiegspunkt der Anwendung. Initialisiert die Bridge-Verbindung, startet den Webserver in einem separaten Prozess und die Hauptsteuerungslogik in einer robusten Schleife.
- `src/`: Enthält die Kernlogik als Python-Paket.
  - `routine.py`: Implementiert die Logik für einzelne Routinen, inklusive Zustandsmanagement.
  - `room.py` / `scene.py` / `sensor.py`: Abstraktionsklassen für die Interaktion mit der Hue Bridge API.
  - `daily_time_span.py`: Verwaltet die zeitliche Logik und die Einteilung der Tagesperioden, inklusive der Berechnung von Sonnenauf- und -untergang.
- `web/`: Beinhaltet die Flask-Webanwendung.
  - `server.py`: Stellt die API-Endpunkte (`/api/*`) für die Kommunikation zwischen Frontend und Backend bereit (Konfigurationsmanagement, Statusabfragen, Bridge-Interaktionen).
  - `templates/index.html`: Die Single-Page-Application, die die gesamte UI rendert.
- `config.yaml`: Zentrale Konfigurationsdatei für Bridge-IP, Routinen, Szenen und Standorteinstellungen.

## Setup & Installation

Voraussetzungen: Python >= 3.8

1.  **Repository klonen:**

    ```bash
    git clone [https://github.com/dein-repo/philipshue-day_routine.git](https://github.com/dein-repo/philipshue-day_routine.git)
    cd philipshue-day_routine
    ```

2.  **Abhängigkeiten installieren:**
    Es wird empfohlen, eine virtuelle Umgebung zu verwenden.

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # unter Linux/macOS
    # .\.venv\Scripts\activate  # unter Windows
    pip install -r requirements.txt
    ```

3.  **Hue Bridge verbinden:**
    a. `config.example.yaml` zu `config.yaml` kopieren.
    b. Die `bridge_ip` in `config.yaml` eintragen.
    c. `main.py` einmalig ausführen und den Anweisungen folgen, um die App durch Drücken des Link-Buttons auf der Bridge zu autorisieren. Der generierte App-Key wird automatisch in die `config.yaml` geschrieben.

4.  **Anwendung starten:**
    ```bash
    python main.py
    ```
    Die Weboberfläche ist unter `http://<deine-ip>:5000` erreichbar.

## API Endpunkte

Die `web/server.py` stellt folgende Haupt-Endpunkte bereit:

- `GET /api/config`: Lädt die aktuelle `config.yaml`.
- `POST /api/config`: Speichert die übermittelte Konfiguration in die `config.yaml`.
- `GET /api/status`: Gibt den Live-Zustand aller Routinen und die berechneten Sonnenzeiten zurück.
- `GET /api/bridge/groups`: Listet alle Räume/Zonen von der Hue Bridge.
- `GET /api/bridge/sensors`: Listet alle Bewegungssensoren von der Hue Bridge.
- `POST /api/system/restart`: Startet die Anwendung neu.

## Contribution

Contributions sind willkommen. Bitte erstelle einen Fork des Repositories und reiche einen Pull Request ein. Halte dich dabei an den bestehenden Code-Stil und stelle sicher, dass alle Tests erfolgreich durchlaufen.

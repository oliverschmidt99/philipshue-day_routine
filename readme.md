# Philips Hue Advanced Routine Controller

Ein fortschrittliches Steuerungssystem für Philips Hue, das komplexe, zeit- und sensorbasierte Routinen über eine benutzerfreundliche Weboberfläche ermöglicht. Die Anwendung ist modular aufgebaut und lässt sich dadurch leicht warten und erweitern.

---

## ⭐ Kernfunktionen

- **Modulare Routine-Engine:** Routinen arbeiten autonom und kombinieren frei definierbare Tageszeiten (Morgen, Tag, Abend, Nacht) mit Sensorereignissen wie Bewegung oder Helligkeit.
- **Zustandsbasierte Logik:** Eine robuste State-Machine verwaltet Systemzustände (z. B. Normal, Bewegung erkannt, Inaktiv) für ein vorhersehbares und stabiles Verhalten.
- **Adaptive Helligkeitsregelung:** Eine dynamische, inverse Steuerung mit Hysterese passt die Lichtintensität automatisch an das Umgebungslicht an – ohne störendes Flackern bei Schwellenwerten.
- **Dynamische Zeitsteuerung:** Tagesabschnitte können entweder an feste Uhrzeiten oder an Sonnenauf- und -untergang (standortbasiert) gekoppelt werden.
- **Datenpersistenz & Analyse:** Sensorwerte (z. B. Helligkeit, Temperatur) werden in einer SQLite-Datenbank gespeichert und per API für Visualisierungen im Frontend verfügbar gemacht.
- **Moderne Web-UI:** Die Benutzeroberfläche basiert auf Vanilla JS und Tailwind CSS und erlaubt die vollständige Konfiguration aller Routinen und Systemeinstellungen in einer Single-Page-Application.

---

## 🏗️ Systemarchitektur

Das System ist in klar abgegrenzte Komponenten strukturiert:

- **`main.py`**: Einstiegspunkt der Anwendung. Initialisiert die Verbindung zur Hue Bridge, startet den Webserver als Subprozess und führt die Hauptlogik in einer Endlosschleife aus.
- **`src/`**: Enthält die Kernlogik als Python-Modul.

  - `routine.py`: Implementiert die Logik einzelner Routinen inkl. Zustandsübergänge und Sensorverarbeitung.
  - `room.py`, `scene.py`, `sensor.py`: Abstraktionsklassen zur Interaktion mit der Hue-Bridge-API.
  - `daily_time_span.py`: Implementiert die Zeitlogik für Tagesabschnitte unter Berücksichtigung von Sonnenauf-/untergang.

- **`web/`**: Flask-basierte Webanwendung mit API und Frontend.

  - `server.py`: Definiert die REST-Endpunkte unter `/api/*`.
  - `templates/` & `static/`: HTML-, CSS- und JavaScript-Dateien für das Webinterface.

- **`config.yaml`**: Zentrale Konfigurationsdatei für Bridge, Routinen, Szenen und globale Parameter.

---

## 🚀 Installation & Inbetriebnahme

Die Installation erfolgt über ein automatisiertes Skript.

**Voraussetzungen:**

- Ein Arch-basiertes Linux-System (z. B. Arch Linux, EndeavourOS)
- `git` zur Versionsverwaltung

**Schritte:**

1. **Repository klonen:**

   ```bash
   git clone https://github.com/oliverschmidt99/philipshue-day_routine.git
   cd philipshue-day_routine
   ```

2. **Installationsskript ausführen:**

   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   Das Skript übernimmt:

   - Installation aller benötigten Pakete via `pacman`
   - Einrichtung einer virtuellen Python-Umgebung (`.venv`)
   - Installation von Abhängigkeiten aus `requirements.txt`
   - Erstellung und Aktivierung eines `systemd`-Dienstes zur Automatisierung

3. **Erstkonfiguration:**

   Nach der Installation läuft der Dienst im Hintergrund. Die Benutzeroberfläche ist über `http://<IP-ADRESSE>:5000` erreichbar. Ein Setup-Assistent führt durch die Verbindung mit der Hue Bridge.

---

## 🛠️ systemd-Service-Verwaltung

- **Status prüfen:**

  ```bash
  systemctl status hue_controller.service
  ```

- **Starten:**

  ```bash
  systemctl start hue_controller.service
  ```

- **Stoppen:**

  ```bash
  systemctl stop hue_controller.service
  ```

- **Neustarten:**

  ```bash
  systemctl restart hue_controller.service
  ```

- **Logs anzeigen:**

  ```bash
  journalctl -u hue_controller.service -f
  ```

---

## 🤝 Mitwirken

Beiträge sind willkommen! Bitte Pull-Requests für neue Features oder Bugfixes einreichen. Für größere Änderungen empfiehlt sich ein Issue zur Diskussion im Vorfeld.

---

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Eine freie Nutzung, Veränderung und Weiterverbreitung ist unter Beibehaltung der ursprünglichen Urheberrechtsinformationen erlaubt.

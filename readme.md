# Philips Hue Advanced Routine Controller

Ein fortschrittliches Steuerungssystem für Philips Hue, das komplexe, zeit- und sensorbasierte Routinen über eine benutzerfreundliche Weboberfläche ermöglicht. Die Anwendung ist modular aufgebaut und lässt sich dadurch leicht warten und erweitern.

---

## ⭐ Kernfunktionen

- **Intuitive Web-UI:** Eine moderne Single-Page-Application, mit der alle Routinen, Szenen und Systemeinstellungen bequem im Browser verwaltet werden können.
- **Modulare Routine-Engine:** Routinen kombinieren frei definierbare Tageszeiten (Morgen, Tag, Abend, Nacht) mit Sensorereignissen. Die Logik ist zustandsbasiert, um ein stabiles und vorhersehbares Verhalten zu gewährleisten.
- **Adaptive Helligkeitsregelung:** Eine intelligente, inverse Steuerung mit Hysterese passt die Lichtintensität automatisch an das Umgebungslicht an. Die gewünschte Lichtfarbe für die Regelung kann direkt in der Routine festgelegt werden.
- **Dynamische Zeitsteuerung:** Tagesabschnitte können an feste Uhrzeiten oder dynamisch an den Sonnenauf- und -untergang (standortbasiert) gekoppelt werden.
- **"Bitte nicht stören"-Funktion:** Erkennt manuelle Eingriffe (z.B. per App oder Schalter) und pausiert die Automatik temporär, um Nutzer nicht zu stören.
- **Datenanalyse & Visualisierung:** Sensorwerte (Helligkeit, Temperatur) werden in einer SQLite-Datenbank gespeichert und können direkt in der Web-UI als Tages- oder Wochenverlauf analysiert werden.
- **System-Management via UI:** Integrierte Funktionen zum Aktualisieren der Anwendung (via Git), Aktualisieren des Betriebssystems (für Arch & Debian-basierte Systeme), Sichern/Wiederherstellen der Konfiguration und Neustarten des Dienstes.

---

## 🏗️ Systemarchitektur

Das System ist in klar abgegrenzte Komponenten strukturiert:

- **`main.py`**: Startpunkt der Anwendung. Initialisiert die Bridge-Verbindung, startet den Webserver als Subprozess und führt die Hauptlogik-Schleife aus.
- **`src/`**: Enthält die Kernlogik als Python-Paket.
  - `routine.py`: Implementiert die State-Machine und Logik für einzelne Routinen.
  - `room.py`, `scene.py`, `sensor.py`: Abstraktionsklassen für die Hue-Bridge-API.
  - `daily_time_span.py`: Berechnet die Tagesperioden unter Berücksichtigung von Sonnenzeiten.
- **`web/`**: Flask-basierte Webanwendung.
  - `server.py`: Stellt die REST-API-Endpunkte (`/api/*`) für das Frontend bereit.
  - `templates/` & `static/`: HTML-, CSS- und JavaScript-Dateien für die Web-UI.
- **`config.yaml`**: Zentrale Konfigurationsdatei für alle Einstellungen.

---

## 🚀 Installation & Inbetriebnahme

Die Installation wird durch ein automatisiertes Skript vereinfacht.

**Voraussetzungen:**

- Ein Arch- oder Debian-basiertes Linux-System (z.B. Arch Linux, Raspberry Pi OS, Ubuntu).
- `git` muss installiert sein.

**Schritte:**

1.  **Repository klonen:**

    ```bash
    git clone [https://github.com/oliverschmidt99/philipshue-day-routine.git](https://github.com/oliverschmidt99/philipshue-day-routine.git)
    cd philipshue-day-routine
    ```

2.  **Installationsskript ausführen:**

    ```bash
    chmod +x install.sh
    ./install.sh
    ```

    Das Skript übernimmt automatisch:

    - Installation von Systemabhängigkeiten.
    - Einrichtung einer Python Virtual Environment (`.venv`).
    - Installation der Python-Pakete aus `requirements.txt`.
    - **Einrichtung von SSH & passwortfreiem `sudo`** für die Update-Funktionen in der UI.
    - Erstellung und Aktivierung eines `systemd`-Dienstes für den automatischen Start.

3.  **Erstkonfiguration:**
    Nach der Installation ist die Web-UI unter `http://<IP-DEINES-GERÄTS>:5000` erreichbar. Ein Assistent führt dich durch die erste Verbindung mit deiner Hue Bridge.

---

## 🛠️ Service-Verwaltung (systemd)

- **Status prüfen:** `systemctl status hue_controller.service`
- **Neustarten:** `systemctl restart hue_controller.service`
- **Logs live ansehen:** `journalctl -u hue_controller.service -f`

---

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz.

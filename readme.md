# Philips Hue Advanced Routine Controller

Ein fortschrittliches Steuerungssystem für Philips Hue, das komplexe, zeit- und sensorbasierte Routinen über eine benutzerfreundliche Weboberfläche ermöglicht.

---

## ⭐ Kernfunktionen

- **Intuitive Web-UI:** Eine moderne Single-Page-Application zur Verwaltung aller Routinen, Szenen und Systemeinstellungen.
- **Adaptive Helligkeitsregelung:** Passt die Lichtintensität intelligent an das Umgebungslicht an.
- **Dynamische Zeitsteuerung:** Koppelt Tagesabschnitte an feste Uhrzeiten oder dynamisch an Sonnenauf- und -untergang.
- **"Bitte nicht stören"-Funktion:** Erkennt manuelle Eingriffe und pausiert die Automatik temporär.
- **Datenanalyse & Visualisierung:** Speichert und visualisiert Sensorwerte (Helligkeit, Temperatur).
- **System-Management via UI:** Integrierte Funktionen für Updates, Backups und Neustarts.

---

## 🏗️ Systemarchitektur

- **`main.py`**: Startpunkt der Anwendung, startet Webserver und Kernlogik.
- **`src/`**: Enthält die Kernlogik als Python-Paket.
  - `core_logic.py`: Die Hauptschleife, die Routinen ausführt.
  - `config_manager.py`: Verwaltet die Konfigurationsdatei `config.yaml`.
  - `routine.py`, `room.py`, etc.: Abstraktionsklassen für die Hue-Logik.
- **`data/`**: Speichert alle veränderlichen Daten:
  - `config.yaml`: Die zentrale Konfigurationsdatei für alles.
  - `app.log`: Die Log-Datei.
  - `status.json`: Live-Status für die Web-UI.
  - `sensor_data.db`: SQLite-Datenbank für Analyse-Daten.
- **`web/`**: Flask-basierte Webanwendung.
  - `server.py`: Haupt-Serverdatei, die die API-Blueprints registriert.
  - `web/api/`: Aufgeteilte API-Endpunkte für bessere Übersicht.
  - `templates/` & `static/`: HTML-, CSS- und JavaScript-Dateien.

---

## 🚀 Installation & Inbetriebnahme

Die Installation wird durch ein Skript vereinfacht.

**Voraussetzungen:**

- Ein Arch- oder Debian-basiertes Linux-System.
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

    Das Skript übernimmt die komplette Einrichtung, inklusive eines `systemd`-Dienstes für den Autostart.

3.  **Erstkonfiguration:**
    Öffne `http://<IP-DEINES-GERÄTS>:5000` im Browser. Ein Assistent führt dich durch die Verbindung mit deiner Hue Bridge.

---

## 🛠️ Service-Verwaltung (systemd)

- **Status prüfen:** `systemctl status hue_controller.service`
- **Neustarten:** `sudo systemctl restart hue_controller.service`
- **Logs ansehen:** `journalctl -u hue_controller.service -f`

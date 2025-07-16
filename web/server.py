import os
import sys
import json
import sqlite3
import markdown
import yaml
import logging # NEU: Import für das Logging-Modul
from datetime import datetime, timedelta

# Füge das Hauptverzeichnis zum Python-Pfad hinzu, damit wir die src-Module importieren können
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, render_template, request
from src.logger import Logger
# Importiere die phue-Bibliothek, um mit der Bridge zu kommunizieren
from phue import Bridge

# Konfigurations- und Statusdateien
CONFIG_FILE = 'config.yaml'
STATUS_FILE = 'status.json'
LOG_FILE = 'info.log'
DB_FILE = 'sensor_data.db'
README_FILE = 'readme.md'

# Initialisiere Flask App und Logger
app = Flask(__name__)
log = Logger(LOG_FILE)

# NEU: Deaktiviere das Standard-Logging von Flask/Werkzeug, um die Konsole sauber zu halten
werkzeug_log = logging.getLogger('werkzeug')
werkzeug_log.setLevel(logging.ERROR)


def get_bridge():
    """Liest die Bridge-IP aus der config.yaml und stellt eine Verbindung her."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        bridge_ip = config.get('bridge_ip')
        if not bridge_ip:
            return None
        return Bridge(bridge_ip)
    except Exception as e:
        log.error(f"Fehler beim Verbinden mit der Bridge im Webserver: {e}")
        return None

@app.route('/')
def index():
    """Rendert die Hauptseite."""
    return render_template('index.html')

@app.route('/api/bridge/groups')
def get_bridge_groups():
    """Liefert eine Liste aller Gruppen (Räume/Zonen) von der Bridge."""
    b = get_bridge()
    if not b:
        return jsonify({"error": "Bridge nicht konfiguriert oder erreichbar"}), 500
    try:
        groups = b.get_group()
        # Formatiere die Daten in eine einfachere Liste von Objekten
        formatted_groups = [{"id": key, "name": value['name']} for key, value in groups.items()]
        return jsonify(formatted_groups)
    except Exception as e:
        log.error(f"Fehler beim Abrufen der Gruppen von der Bridge: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/bridge/sensors')
def get_bridge_sensors():
    """Liefert eine Liste aller Sensoren von der Bridge."""
    b = get_bridge()
    if not b:
        return jsonify({"error": "Bridge nicht konfiguriert oder erreichbar"}), 500
    try:
        sensors = b.get_sensor()
        # Formatiere die Daten und filtere nur nach Bewegungssensoren
        formatted_sensors = [
            {"id": key, "name": value['name']} 
            for key, value in sensors.items() 
            if value.get('type') == 'ZLLPresence'
        ]
        return jsonify(formatted_sensors)
    except Exception as e:
        log.error(f"Fehler beim Abrufen der Sensoren von der Bridge: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Liest oder schreibt die Hauptkonfigurationsdatei."""
    if request.method == 'POST':
        try:
            new_config = request.get_json()
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f, allow_unicode=True, sort_keys=False)
            log.info("Konfiguration wurde erfolgreich über die API aktualisiert.")
            return jsonify({"message": "Konfiguration erfolgreich gespeichert."})
        except Exception as e:
            log.error(f"Fehler beim Schreiben der Konfiguration: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    else: # GET
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return jsonify(config)
        except FileNotFoundError:
            return jsonify({"error": "Konfigurationsdatei nicht gefunden."}), 404
        except Exception as e:
            log.error(f"Fehler beim Lesen der Konfiguration: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

@app.route('/api/status')
def get_status():
    """Liest die Statusdatei und gibt ihren Inhalt zurück."""
    try:
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            status = json.load(f)
        return jsonify(status)
    except FileNotFoundError:
        return jsonify([]), 404
    except Exception as e:
        log.error(f"Fehler beim Lesen der Statusdatei: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/log')
def get_log():
    """Liest die letzten Zeilen der Log-Datei."""
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-500:]
            return "".join(lines)
    except FileNotFoundError:
        return "Log-Datei nicht gefunden.", 404

@app.route('/api/data/history')
def get_data_history():
    """Liefert historische Sensordaten für die Diagramme."""
    try:
        sensor_id = request.args.get('sensor_id', type=int)
        period = request.args.get('period', 'day') # day, month, year
        start_date_str = request.args.get('date')

        if not sensor_id or not start_date_str:
            return jsonify({"error": "sensor_id und date sind erforderlich"}), 400

        start_date = datetime.fromisoformat(start_date_str)

        if period == 'day':
            end_date = start_date + timedelta(days=1)
            date_format = "%H:%M"
        elif period == 'month':
            year = start_date.year + (start_date.month // 12)
            month = start_date.month % 12 + 1
            end_date = datetime(year, month, 1)
            date_format = "%d.%m"
        elif period == 'year':
            end_date = datetime(start_date.year + 1, 1, 1)
            date_format = "%B"
        else:
            return jsonify({"error": "Ungültiger Zeitraum"}), 400
        
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()

        cur.execute("""
            SELECT timestamp, value FROM measurements 
            WHERE sensor_id = ? AND measurement_type = 'brightness' AND timestamp >= ? AND timestamp < ?
            ORDER BY timestamp
        """, (sensor_id, start_date.isoformat(), end_date.isoformat()))
        brightness_data = cur.fetchall()

        cur.execute("""
            SELECT timestamp, value FROM measurements 
            WHERE sensor_id = ? AND measurement_type = 'temperature' AND timestamp >= ? AND timestamp < ?
            ORDER BY timestamp
        """, (sensor_id + 1, start_date.isoformat(), end_date.isoformat()))
        temperature_data = cur.fetchall()

        con.close()

        chart_data = {
            'labels': [datetime.fromisoformat(row[0]).strftime(date_format) for row in brightness_data],
            'brightness': [row[1] for row in brightness_data],
            'temperature': [row[1] for row in temperature_data]
        }
        
        return jsonify(chart_data)

    except Exception as e:
        log.error(f"Fehler beim Abrufen der Verlaufsdaten: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/readme')
def get_readme():
    """Liest die readme.md, konvertiert sie zu HTML und gibt sie zurück."""
    try:
        with open(README_FILE, 'r', encoding='utf-8') as f:
            text = f.read()
        html = markdown.markdown(text)
        return html
    except FileNotFoundError:
        return "<p>README.md nicht gefunden.</p>", 404
    except Exception as e:
        log.error(f"Fehler beim Lesen der README-Datei: {e}")
        return f"<p>Fehler: {e}</p>", 500


if __name__ == '__main__':
    # Starte den Flask-Server im Debug-Modus
    app.run(debug=False, port=5000, host='0.0.0.0')


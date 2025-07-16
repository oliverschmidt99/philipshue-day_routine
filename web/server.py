import os
import sys
import json
import sqlite3
import markdown
import yaml
import logging
import shutil
from datetime import datetime, timedelta

# Füge das Hauptverzeichnis zum Python-Pfad hinzu, damit wir die src-Module importieren können
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, render_template, request
from src.logger import Logger
from phue import Bridge

# Konfigurations- und Statusdateien
CONFIG_FILE = 'config.yaml'
CONFIG_BACKUP_FILE = 'config.backup.yaml'
STATUS_FILE = 'status.json'
LOG_FILE = 'info.log'
DB_FILE = 'sensor_data.db'
README_FILE = 'readme.md'

# Initialisiere Flask App und Logger
app = Flask(__name__)
log = Logger(LOG_FILE)

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
    b = get_bridge()
    if not b: return jsonify({"error": "Bridge nicht konfiguriert oder erreichbar"}), 500
    try:
        groups = b.get_group()
        return jsonify([{"id": key, "name": value['name']} for key, value in groups.items()])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bridge/sensors')
def get_bridge_sensors():
    b = get_bridge()
    if not b: return jsonify({"error": "Bridge nicht konfiguriert oder erreichbar"}), 500
    try:
        sensors = b.get_sensor()
        return jsonify([{"id": key, "name": value['name']} for key, value in sensors.items() if value.get('type') == 'ZLLPresence'])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'POST':
        try:
            new_config = request.get_json()
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f, allow_unicode=True, sort_keys=False)
            log.info("Konfiguration wurde erfolgreich über die API aktualisiert.")
            return jsonify({"message": "Konfiguration erfolgreich gespeichert."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else: # GET
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return jsonify(yaml.safe_load(f))
        except FileNotFoundError:
            return jsonify({"error": "Konfigurationsdatei nicht gefunden."}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/status')
def get_status():
    try:
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify([]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/log')
def get_log():
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return "".join(f.readlines()[-500:])
    except FileNotFoundError:
        return "Log-Datei nicht gefunden.", 404

@app.route('/api/data/history')
def get_data_history():
    try:
        sensor_id = request.args.get('sensor_id', type=int)
        period = request.args.get('period', 'day')
        start_date_str = request.args.get('date')

        if not sensor_id or not start_date_str:
            return jsonify({"error": "sensor_id und date sind erforderlich"}), 400

        start_date = datetime.fromisoformat(start_date_str)
        
        agg_format, date_format, end_date = "", "", None
        if period == 'day':
            end_date, date_format, agg_format = start_date + timedelta(days=1), "%H:%M", ""
        elif period == 'week':
            start_of_week = start_date - timedelta(days=start_date.weekday())
            end_date, date_format, agg_format = start_of_week + timedelta(days=7), "%a, %d.%m.", "%Y-%m-%d"
        elif period == 'month':
            year, month = (start_date.year, start_date.month % 12 + 1) if start_date.month < 12 else (start_date.year + 1, 1)
            end_date, date_format, agg_format = datetime(year, month, 1), "%d.%m.", "%Y-%m-%d"
        elif period == 'year':
            end_date, date_format, agg_format = datetime(start_date.year + 1, 1, 1), "%B", "%Y-%m"
        else:
            return jsonify({"error": "Ungültiger Zeitraum"}), 400
        
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()

        def fetch_aggregated_data(measurement_type, target_sensor_id):
            query = f"""
                SELECT strftime('{agg_format}', timestamp) as agg_time, AVG(value) 
                FROM measurements WHERE sensor_id = ? AND measurement_type = ? AND timestamp >= ? AND timestamp < ?
                GROUP BY agg_time ORDER BY agg_time
            """ if agg_format else """
                SELECT timestamp, value FROM measurements 
                WHERE sensor_id = ? AND measurement_type = ? AND timestamp >= ? AND timestamp < ? ORDER BY timestamp
            """
            cur.execute(query, (target_sensor_id, measurement_type, start_date.isoformat(), end_date.isoformat()))
            return cur.fetchall()

        brightness_data = fetch_aggregated_data('brightness', sensor_id)
        temperature_data = fetch_aggregated_data('temperature', sensor_id + 1)
        con.close()

        def format_label(ts_str, fmt, agg):
            dt_obj = datetime.strptime(ts_str, agg) if agg else datetime.fromisoformat(ts_str)
            return dt_obj.strftime(fmt)

        all_labels_raw = sorted(list(set([row[0] for row in brightness_data] + [row[0] for row in temperature_data])))
        brightness_dict, temperature_dict = dict(brightness_data), dict(temperature_data)
        
        return jsonify({
            'labels': [format_label(raw, date_format, agg_format) for raw in all_labels_raw],
            'brightness': [brightness_dict.get(raw) for raw in all_labels_raw],
            'temperature': [temperature_dict.get(raw) for raw in all_labels_raw]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/readme')
def get_readme():
    try:
        with open(README_FILE, 'r', encoding='utf-8') as f:
            return markdown.markdown(f.read())
    except FileNotFoundError:
        return "<p>README.md nicht gefunden.</p>", 404

# NEUE Endpunkte für die Einstellungen
@app.route('/api/system/restart', methods=['POST'])
def restart_app():
    log.info("Neustart der Anwendung über API ausgelöst.")
    # Dieser Befehl beendet den aktuellen Prozess und startet ihn neu.
    # Funktioniert gut in einfachen Szenarien, kann aber bei komplexen Setups unzuverlässig sein.
    try:
        # Gib dem Frontend Zeit, die Antwort zu empfangen, bevor der Server neu startet.
        def restart_later():
            time.sleep(1)
            os.execv(sys.executable, ['python'] + sys.argv)
        
        import threading
        threading.Thread(target=restart_later).start()
        
        return jsonify({"message": "Anwendung wird neu gestartet..."})
    except Exception as e:
        log.error(f"Fehler beim Neustart der Anwendung: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/database/clear', methods=['POST'])
def clear_database():
    log.info("Löschen der Datenbank über API ausgelöst.")
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("DELETE FROM measurements")
        con.commit()
        con.close()
        return jsonify({"message": "Messdaten-Historie wurde gelöscht."})
    except Exception as e:
        log.error(f"Fehler beim Löschen der Datenbank: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/config/backup', methods=['POST'])
def backup_config():
    log.info("Backup der Konfiguration über API ausgelöst.")
    try:
        shutil.copy(CONFIG_FILE, CONFIG_BACKUP_FILE)
        return jsonify({"message": f"Konfiguration wurde als '{CONFIG_BACKUP_FILE}' gesichert."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config/restore', methods=['POST'])
def restore_config():
    log.info("Wiederherstellung der Konfiguration über API ausgelöst.")
    try:
        if not os.path.exists(CONFIG_BACKUP_FILE):
            return jsonify({"error": "Keine Backup-Datei gefunden."}), 404
        shutil.copy(CONFIG_BACKUP_FILE, CONFIG_FILE)
        return jsonify({"message": "Konfiguration aus Backup wiederhergestellt. Bitte die Anwendung neu starten."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0')

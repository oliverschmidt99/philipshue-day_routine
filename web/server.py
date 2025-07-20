import os
import sys
import json
import sqlite3
import markdown
import yaml
import logging
import shutil
import time
import threading
import requests
from datetime import datetime, timedelta

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, render_template, request
from src.logger import Logger
from phue import Bridge

# Globale Dateipfade
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
CONFIG_FILE = os.path.join(PROJECT_ROOT, 'config.yaml')
CONFIG_LOCK_FILE = os.path.join(PROJECT_ROOT, 'config.yaml.lock')
CONFIG_BACKUP_FILE = os.path.join(PROJECT_ROOT, 'config.backup.yaml')
STATUS_FILE = os.path.join(PROJECT_ROOT, 'status.json')
LOG_FILE = os.path.join(PROJECT_ROOT, 'info.log')
DB_FILE = os.path.join(PROJECT_ROOT, 'sensor_data.db')
HELP_FILE = os.path.join(BASE_DIR, 'templates', 'hilfe.html')

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
        app_key = config.get('app_key')
        if not bridge_ip or not app_key:
            return None
        return Bridge(bridge_ip, username=app_key)
    except Exception as e:
        log.error(f"Fehler beim Verbinden mit der Bridge im Webserver: {e}")
        return None

# --- SETUP API ENDPOINTS ---

@app.route('/api/setup/status')
def get_setup_status():
    """Prüft, ob die Anwendung bereits konfiguriert ist."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        if config and config.get('bridge_ip') and config.get('app_key'):
            return jsonify({'setup_needed': False})
        return jsonify({'setup_needed': True})
    except Exception:
        return jsonify({'setup_needed': True})

@app.route('/api/setup/discover')
def discover_bridges():
    """Sucht nach Hue Bridges im Netzwerk."""
    try:
        response = requests.get('https://discovery.meethue.com/')
        response.raise_for_status()
        bridges = response.json()
        return jsonify([b['internalipaddress'] for b in bridges])
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/setup/connect', methods=['POST'])
def connect_to_bridge():
    """Versucht, sich mit der Bridge zu verbinden und einen App-Key zu erhalten."""
    data = request.get_json()
    ip_address = data.get('ip')
    if not ip_address:
        return jsonify({"error": "IP-Adresse fehlt."}), 400

    try:
        bridge = Bridge(ip_address)
        # Dieser Aufruf löst den Link-Button-Prozess aus
        bridge.connect()
        app_key = bridge.username
        return jsonify({"app_key": app_key})
    except Exception as e:
        # Extrahieren der relevanten Fehlermeldung
        error_message = str(e)
        if '101' in error_message:
            error_message = "Der Link-Button auf der Bridge wurde nicht gedrückt."
        return jsonify({"error": error_message}), 500

@app.route('/api/setup/save', methods=['POST'])
def save_setup_config():
    """Speichert die Erstkonfiguration."""
    try:
        data = request.get_json()
        
        # Erstelle eine vollständige Konfigurationsstruktur
        new_config = {
            'bridge_ip': data.get('bridge_ip'),
            'app_key': data.get('app_key'),
            'location': {
                'latitude': float(data.get('latitude')),
                'longitude': float(data.get('longitude'))
            },
            'global_settings': {
                'datalogger_interval_minutes': 15,
                'hysteresis_percent': 25,
                'log_level': 'INFO',
                'times': {'morning': '06:30', 'day': '', 'evening': '', 'night': '23:00'}
            },
            'rooms': [], 'routines': [],
            'scenes': {'off': {'status': False, 'bri': 0}, 'on': {'status': True, 'bri': 254}}
        }

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(new_config, f, allow_unicode=True, sort_keys=False)
        
        # KORREKTUR: Der Neustart wird jetzt von der main.py-Schleife gehandhabt.
        # Wir müssen hier nichts mehr tun, außer eine Erfolgsmeldung zurückzugeben.
        
        return jsonify({"message": "Konfiguration erfolgreich gespeichert. Die Anwendung lädt im Hintergrund neu."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- REGULAR API ENDPOINTS ---

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
            
            with open(CONFIG_LOCK_FILE, 'w') as f:
                pass
            log.debug("Config-Lock erstellt.")

            temp_file = CONFIG_FILE + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                yaml.dump(new_config, f, allow_unicode=True, sort_keys=False)

            os.replace(temp_file, CONFIG_FILE)
            
            log.info("Konfiguration wurde erfolgreich über die API aktualisiert.")
            return jsonify({"message": "Konfiguration erfolgreich gespeichert."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            if os.path.exists(CONFIG_LOCK_FILE):
                os.remove(CONFIG_LOCK_FILE)
                log.debug("Config-Lock entfernt.")

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
    """Gibt den aktuellen Status der Routinen und die Sonnenzeiten zurück."""
    try:
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            response_data = {
                'routines': data.get('routines', []),
                'sun_times': data.get('sun_times', None)
            }
            return jsonify(response_data)
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify({'routines': [], 'sun_times': None}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/log')
def get_log():
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return "".join(lines[-500:])
    except FileNotFoundError:
        return "Log-Datei nicht gefunden.", 404
    except Exception as e:
        return f"Fehler beim Lesen der Log-Datei: {e}", 500

@app.route('/api/data/history')
def get_data_history():
    """Gibt historische Sensordaten für die Diagramme zurück."""
    try:
        sensor_id = request.args.get('sensor_id', type=int)
        period = request.args.get('period', 'day')
        date_str = request.args.get('date')

        if sensor_id is None or not date_str:
            return jsonify({"error": "sensor_id und date sind erforderlich"}), 400

        start_date = datetime.fromisoformat(date_str)
        
        light_sensor_id = sensor_id + 1
        temp_sensor_id = sensor_id + 2
        
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()

        if period == 'day':
            end_date = start_date + timedelta(days=1)
            
            cur.execute("SELECT timestamp, value FROM measurements WHERE sensor_id = ? AND measurement_type = 'brightness' AND timestamp >= ? AND timestamp < ? ORDER BY timestamp",
                        (light_sensor_id, start_date.isoformat(), end_date.isoformat()))
            brightness_data = cur.fetchall()
            
            cur.execute("SELECT timestamp, value FROM measurements WHERE sensor_id = ? AND measurement_type = 'temperature' AND timestamp >= ? AND timestamp < ? ORDER BY timestamp",
                        (temp_sensor_id, start_date.isoformat(), end_date.isoformat()))
            temperature_data = cur.fetchall()

            labels = sorted(list(set([row[0] for row in brightness_data] + [row[0] for row in temperature_data])))
            brightness_dict = dict(brightness_data)
            temperature_dict = dict(temperature_data)

            return jsonify({
                'labels': labels,
                'brightness': [brightness_dict.get(ts) for ts in labels],
                'temperature': [temperature_dict.get(ts) for ts in labels]
            })

        elif period == 'week':
            start_of_week = start_date - timedelta(days=start_date.weekday())
            end_of_week = start_of_week + timedelta(days=7)
            
            def fetch_weekly_avg(target_sensor_id, m_type):
                query = """
                    SELECT strftime('%Y-%m-%d', timestamp) as day, AVG(value)
                    FROM measurements WHERE sensor_id = ? AND measurement_type = ? AND timestamp >= ? AND timestamp < ?
                    GROUP BY day ORDER BY day
                """
                cur.execute(query, (target_sensor_id, m_type, start_of_week.isoformat(), end_of_week.isoformat()))
                return dict(cur.fetchall())

            brightness_dict = fetch_weekly_avg(light_sensor_id, 'brightness')
            temperature_dict = fetch_weekly_avg(temp_sensor_id, 'temperature')
            
            week_days_iso = [(start_of_week + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
            day_names = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
            
            return jsonify({
                'labels': day_names,
                'brightness': [brightness_dict.get(day) for day in week_days_iso],
                'temperature': [temperature_dict.get(day) for day in week_days_iso]
            })

        else:
             return jsonify({"error": "Ungültiger Zeitraum"}), 400

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        if 'con' in locals() and con:
            con.close()

@app.route('/api/help')
def get_help():
    """Liest die hilfe.html und gibt ihren Inhalt als JSON zurück."""
    try:
        with open(HELP_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify(content=content)
    except FileNotFoundError:
        log.error(f"Hilfedatei nicht gefunden unter: {HELP_FILE}")
        return jsonify(error="hilfe.html nicht gefunden"), 404
    except Exception as e:
        log.error(f"Fehler beim Lesen der Hilfedatei: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/restart', methods=['POST'])
def restart_app():
    log.info("Neustart der Anwendung über API ausgelöst.")
    try:
        # Dieser Neustart ist für den normalen Betrieb gedacht, nicht für das Setup
        def restart_later():
            time.sleep(1)
            python_executable = sys.executable
            os.execv(python_executable, [python_executable] + sys.argv)
        
        threading.Thread(target=restart_later).start()
        
        return jsonify({"message": "Anwendung wird neu gestartet..."})
    except Exception as e:
        log.error(f"Fehler beim Neustart der Anwendung: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/config/backup', methods=['POST'])
def backup_config():
    log.info("Backup der Konfiguration über API ausgelöst.")
    try:
        shutil.copy(CONFIG_FILE, CONFIG_BACKUP_FILE)
        return jsonify({"message": f"Konfiguration wurde als '{os.path.basename(CONFIG_BACKUP_FILE)}' gesichert."})
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

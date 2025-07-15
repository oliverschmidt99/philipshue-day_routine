import os
import sys
from flask import Flask, request, jsonify, render_template, Response
import yaml
import json
import logging
from phue import Bridge
from unittest.mock import MagicMock # Import für den Test-Modus

# Pfade an neue Struktur anpassen
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
STATUS_FILE = os.path.join(os.path.dirname(__file__), '..', 'status.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'info.log')

app = Flask(__name__, template_folder='templates')

log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

bridge_connection = None

def get_bridge_connection():
    """
    Stellt eine Verbindung zur Bridge her.
    Im Test-Modus wird eine Schein-Bridge (Mock) zurückgegeben.
    """
    global bridge_connection

    # Prüfe, ob die App im Test-Modus läuft.
    if app.config.get("TESTING"):
        mock_bridge = MagicMock()
        mock_bridge.get_group.return_value = {'1': {'name': 'Test Raum', 'type': 'Room'}}
        mock_sensor = MagicMock(name='Test Sensor', type='ZLLPresence')
        mock_bridge.get_sensor_objects.return_value = {'2': mock_sensor}
        return mock_bridge

    # Normaler Betrieb
    if bridge_connection is None:
        try:
            # Im Testfall werden diese Pfade durch die Test-Fixtures überschrieben
            cfg_file = app.config.get('CONFIG_FILE', CONFIG_FILE)
            with open(cfg_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            b = Bridge(config['bridge_ip'])
            b.connect()
            bridge_connection = b
            app.logger.info("Bridge-Verbindung hergestellt.")
        except Exception as e:
            app.logger.error(f"API kann keine Bridge-Verbindung herstellen: {e}")
            return None
    return bridge_connection

# === API Endpunkte ===

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    # Im Test-Modus die temporären Pfade verwenden, sonst die Standardpfade
    cfg_file = app.config.get('TEST_CONFIG_FILE', CONFIG_FILE) if app.config.get("TESTING") else CONFIG_FILE
    
    if request.method == 'POST':
        try:
            data = request.json
            with open(cfg_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            return jsonify({"message": "Konfiguration gespeichert. Bitte starte die Anwendung neu, um die Änderungen zu übernehmen."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else: # GET
        try:
            with open(cfg_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return Response(json.dumps(config), mimetype='application/json')
        except Exception as e:
            return jsonify({"error": f"Fehler beim Laden von {cfg_file}: {e}"}), 500

@app.route('/api/bridge/<item>', methods=['GET'])
def get_bridge_data(item):
    bridge = get_bridge_connection()
    if not bridge:
        return jsonify({"error": "Keine Verbindung zur Bridge"}), 500
    try:
        if item == 'groups':
            data = bridge.get_group()
            return jsonify([{"id": key, "name": value['name']} for key, value in data.items() if value.get('type') in ['Room', 'Zone']])
        elif item == 'sensors':
            data = bridge.get_sensor_objects('id')
            return jsonify([{"id": key, "name": value.name} for key, value in data.items() if value.type == 'ZLLPresence'])
        return jsonify({"error": "Unbekannter Endpunkt"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    status_file = app.config.get('TEST_STATUS_FILE', STATUS_FILE) if app.config.get("TESTING") else STATUS_FILE
    try:
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
        return jsonify(status_data)
    except FileNotFoundError:
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/log', methods=['GET'])
def get_log():
    log_file = app.config.get('TEST_LOG_FILE', LOG_FILE) if app.config.get("TESTING") else LOG_FILE
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='text/plain')
    except FileNotFoundError:
        return Response("Log-Datei nicht gefunden.", mimetype='text/plain')
    except Exception as e:
        return Response(f"Fehler beim Lesen der Log-Datei: {e}", mimetype='text/plain')

if __name__ == '__main__':
    # Im normalen Betrieb wird die Umgebungsvariable nicht gesetzt sein.
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN'):
        get_bridge_connection()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

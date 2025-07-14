import logging
import os
import json
from flask import Flask, render_template, jsonify, request, send_from_directory
from hue_app.core.configuration import Configuration

# Initialisierung
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, '..', '..', 'config.yaml')
config = Configuration(config_path)
app = Flask(__name__, static_folder='static', template_folder='templates')

# Logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('hue.html')

# --- API Endpunkte ---
@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'POST':
        try:
            config.save_config(request.get_json())
            app.logger.info("Konfiguration gespeichert.")
            return jsonify({"success": True, "message": "Konfiguration erfolgreich gespeichert."})
        except Exception as e:
            app.logger.error(f"Fehler beim Speichern: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    return jsonify(config.get_config())

@app.route('/api/bridge/groups')
def get_bridge_groups():
    return jsonify(config.get_rooms_for_api())

@app.route('/api/bridge/sensors')
def get_bridge_sensors():
    """NEU: Stellt eine Liste der Sensoren von der Bridge bereit."""
    try:
        sensors = config.bridge.get_sensors() if config.bridge else []
        # Filtern und formatieren der Sensordaten für die UI
        sensor_list = [{'id': s.sensorid, 'name': s.name} for s in sensors if 'motion' in s.type.lower()]
        return jsonify(sensor_list)
    except Exception as e:
        app.logger.error(f"Fehler beim Abrufen der Sensoren: {e}")
        return jsonify([])

@app.route('/api/status')
def get_status_log():
    # Diese Funktion bleibt im Wesentlichen gleich und liest status.json und app.log
    status_data, log_data = {}, ""
    try:
        status_path = os.path.join(script_dir, '..', '..', 'status.json')
        if os.path.exists(status_path):
            with open(status_path, 'r') as f:
                content = f.read()
                if content.strip(): status_data = json.loads(content)
        
        log_path = os.path.join(script_dir, '..', '..', 'app.log')
        if os.path.exists(log_path):
            with open(log_path, 'r') as f: log_data = f.read()
    except Exception as e:
        app.logger.error(f"Fehler beim Lesen von Status/Log: {e}")
    return jsonify({"status": status_data, "log": log_data})

@app.route('/api/restart', methods=['POST'])
def restart_logic():
    app.logger.info("Neustart der Logik-Engine angefordert...")
    # Hier würde die Logik zum Neustarten des Hintergrund-Threads implementiert.
    return jsonify({"success": True, "message": "Neustart wird ausgeführt."})

def run_server(debug=True):
    app.run(host='0.0.0.0', port=5000, debug=debug)

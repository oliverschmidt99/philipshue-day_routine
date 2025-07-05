from flask import Flask, request, jsonify, render_template, Response
import yaml
import os
import subprocess
import json
from phue import Bridge

app = Flask(__name__)
CONFIG_FILE = 'config.yaml'
MAIN_SCRIPT = 'main.py'

# Globale Variablen
main_process = None
bridge_connection = None

def get_bridge_connection():
    """Stellt eine Singleton-Verbindung zur Bridge her und gibt sie zurück."""
    global bridge_connection
    if bridge_connection is None:
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            b = Bridge(config['bridge_ip'])
            b.connect()
            bridge_connection = b
            app.logger.info("Bridge-Verbindung für API-Aufrufe hergestellt.")
        except Exception as e:
            app.logger.error(f"Konnte keine Bridge-Verbindung für API herstellen: {e}")
            return None
    return bridge_connection

def restart_main_script():
    """Stoppt den laufenden main.py Prozess und startet ihn neu."""
    global main_process
    if main_process and main_process.poll() is None:
        print("Beende laufendes Hauptskript...")
        main_process.terminate()
        try:
            main_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("Warnung: Hauptskript konnte nicht rechtzeitig beendet werden. Erzwinge Beendigung (kill).")
            main_process.kill()
    
    print("Starte Hauptskript neu...")
    main_process = subprocess.Popen(['python', MAIN_SCRIPT])
    return "Hauptskript wurde neu gestartet."

# === API Endpunkte ===

@app.route('/')
def index():
    return render_template('hue.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Liest die lokale YAML-Konfiguration."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return Response(json.dumps(config), mimetype='application/json')
    except Exception as e:
        app.logger.error(f"Fehler beim Laden der config.yaml: {e}", exc_info=True)
        return jsonify({"error": "Server-Fehler beim Laden der Konfiguration."}), 500

@app.route('/api/config', methods=['POST'])
def set_config():
    """Speichert die komplette Konfiguration und startet die Haupt-Logik neu."""
    try:
        data = request.json
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        restart_message = restart_main_script()
        return jsonify({"message": f"Konfiguration erfolgreich gespeichert. {restart_message}"})
    except Exception as e:
        app.logger.error(f"Fehler beim Speichern der Konfiguration: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/bridge/groups', methods=['GET'])
def get_bridge_groups():
    """Holt alle Gruppen (Räume/Zonen) von der Bridge."""
    bridge = get_bridge_connection()
    if not bridge:
        return jsonify({"error": "Keine Verbindung zur Bridge"}), 500
    try:
        groups = bridge.get_group()
        # Filtere und formatiere die Ausgabe für die Webseite
        formatted_groups = [{"id": key, "name": value['name']} for key, value in groups.items()]
        return jsonify(formatted_groups)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bridge/sensors', methods=['GET'])
def get_bridge_sensors():
    """Holt alle Sensoren von der Bridge."""
    bridge = get_bridge_connection()
    if not bridge:
        return jsonify({"error": "Keine Verbindung zur Bridge"}), 500
    try:
        sensors = bridge.get_sensor_objects('id')
        # Gebe nur Bewegungsmelder zurück (Typ ZLLPresence)
        formatted_sensors = [{"id": key, "name": value.name} for key, value in sensors.items() if value.type == 'ZLLPresence']
        return jsonify(formatted_sensors)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Server Start ===

if __name__ == '__main__':
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN'):
        # Stelle sicher, dass die Bridge-Verbindung einmal initialisiert wird
        get_bridge_connection()
        restart_main_script()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

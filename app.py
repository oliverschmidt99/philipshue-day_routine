from flask import Flask, request, jsonify, render_template, Response
import yaml
import os
import subprocess
import json
import logging
from phue import Bridge

app = Flask(__name__)
CONFIG_FILE = 'config.yaml'
STATUS_FILE = 'status.json'
LOG_FILE = 'info.log'
MAIN_SCRIPT = 'main.py'

# Deaktiviere die standardmäßigen Flask-Zugriffslogs in der Konsole
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

main_process = None
bridge_connection = None

def get_bridge_connection():
    """Stellt eine Singleton-Verbindung zur Bridge her und gibt sie zurück."""
    global bridge_connection
    if bridge_connection is None:
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            # Lese die IP aus den neuen Einstellungen
            bridge_ip = config.get('settings', {}).get('bridge_ip', '127.0.0.1')
            b = Bridge(bridge_ip)
            b.connect()
            bridge_connection = b
            app.logger.info(f"Bridge-Verbindung für API zu {bridge_ip} hergestellt.")
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

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'POST':
        try:
            data = request.json
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            restart_message = restart_main_script()
            return jsonify({"message": f"Konfiguration erfolgreich gespeichert. {restart_message}"})
        except Exception as e:
            app.logger.error(f"Fehler beim Speichern der Konfiguration: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    else: # GET
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return Response(json.dumps(config), mimetype='application/json')
        except Exception as e:
            app.logger.error(f"Fehler beim Laden der config.yaml: {e}", exc_info=True)
            return jsonify({"error": "Server-Fehler beim Laden der Konfiguration."}), 500

@app.route('/api/bridge/<item>', methods=['GET'])
def get_bridge_data(item):
    bridge = get_bridge_connection()
    if not bridge:
        return jsonify({"error": "Keine Verbindung zur Bridge"}), 500
    try:
        if item == 'groups':
            data = bridge.get_group()
            return jsonify([{"id": key, "name": value['name']} for key, value in data.items()])
        elif item == 'sensors':
            data = bridge.get_sensor_objects('id')
            return jsonify([{"id": key, "name": value.name} for key, value in data.items() if value.type == 'ZLLPresence'])
        return jsonify({"error": "Unbekannter Endpunkt"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Liest die Status-Datei und gibt sie zurück."""
    try:
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
        return jsonify(status_data)
    except FileNotFoundError:
        return jsonify([]) # Leere Liste, wenn die Datei noch nicht existiert
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/log', methods=['GET'])
def get_log():
    """Liest die Log-Datei und gibt sie als Text zurück."""
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='text/plain')
    except FileNotFoundError:
        return Response("Log-Datei nicht gefunden.", mimetype='text/plain')
    except Exception as e:
        return Response(f"Fehler beim Lesen der Log-Datei: {e}", mimetype='text/plain')

# === Server Start ===

if __name__ == '__main__':
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN'):
        get_bridge_connection()
        restart_main_script()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

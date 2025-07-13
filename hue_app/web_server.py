import os
import subprocess
import json
import logging
from flask import Flask, request, jsonify, render_template, Response
from phue import Bridge

# Korrekter Import aus dem 'core'-Paket
from hue_app.core.configuration import Configuration

# --- Globale Konfiguration und Initialisierung ---

# Wichtig: Flask muss wissen, wo es die templates/ und static/ Ordner findet.
# Indem wir den Paketnamen angeben, funktioniert es automatisch.
app = Flask(__name__.split('.')[0])

# Pfade relativ zum Projekt-Root definieren
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_FILE = os.path.join(ROOT_DIR, 'config.yaml')
STATUS_FILE = os.path.join(ROOT_DIR, 'status.json')
LOG_FILE = os.path.join(ROOT_DIR, 'info.log')
ROUTINE_ENGINE_SCRIPT = os.path.join(os.path.dirname(__file__), 'routine_engine.py')

# Logging-Konfiguration
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) # Nur Fehler im Flask-Log anzeigen
app.logger.setLevel(logging.INFO)

main_process = None
bridge_connection = None

# --- Hilfsfunktionen ---

def get_bridge_connection():
    """Stellt eine Singleton-Verbindung zur Bridge her."""
    global bridge_connection
    if bridge_connection is None:
        try:
            config_manager = Configuration(config_file=CONFIG_FILE)
            if config_manager.bridge:
                bridge_connection = config_manager.bridge
                app.logger.info(f"Bridge-Verbindung für API hergestellt.")
            else:
                app.logger.error("Konnte keine Bridge-Verbindung für API herstellen.")
        except Exception as e:
            # DIESER BLOCK HAT GEFEHLT
            app.logger.error(f"Fehler bei der API-Bridge-Verbindung: {e}", exc_info=True)
            # Im Fehlerfall None zurückgeben
            bridge_connection = None
    return bridge_connection

def restart_routine_engine():
    """Stoppt den laufenden Routine-Engine Prozess und startet ihn neu."""
    global main_process
    if main_process and main_process.poll() is None:
        app.logger.info("Beende laufende Routine-Engine...")
        main_process.terminate()
        try:
            main_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            app.logger.warning("Routine-Engine konnte nicht rechtzeitig beendet werden.")
            main_process.kill()
    
    app.logger.info("Starte Routine-Engine neu...")
    main_process = subprocess.Popen(['python', ROUTINE_ENGINE_SCRIPT])
    return "Routine-Engine wurde neu gestartet."

# --- API Endpunkte ---

@app.route('/')
def index():
    return render_template('hue.html')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    config_manager = Configuration(config_file=CONFIG_FILE)
    if request.method == 'POST':
        try:
            data = request.json
            if config_manager.save_config(data):
                restart_message = restart_routine_engine()
                return jsonify({"message": f"Konfiguration gespeichert. {restart_message}"})
            else:
                return jsonify({"error": "Konfiguration konnte nicht gespeichert werden."}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        if config_manager.config:
            return Response(json.dumps(config_manager.config), mimetype='application/json')
        else:
            return jsonify({"error": "Konfiguration konnte nicht geladen werden."}), 500

@app.route('/api/bridge/<item>', methods=['GET'])
def get_bridge_data(item):
    bridge = get_bridge_connection()
    if not bridge:
        return jsonify({"error": "Keine Verbindung zur Bridge"}), 500
    try:
        if item == 'groups':
            data = bridge.get_group()
            return jsonify([{"id": k, "name": v['name']} for k, v in data.items()])
        elif item == 'sensors':
            data = bridge.get_sensor_objects('id')
            return jsonify([{"id": k, "name": v.name} for k, v in data.items() if v.type == 'ZLLPresence'])
        return jsonify({"error": "Unbekannter Endpunkt"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    try:
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    except FileNotFoundError:
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/log', methods=['GET'])
def get_log():
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='text/plain')
    except FileNotFoundError:
        return Response("Log-Datei nicht gefunden.", mimetype='text/plain')
    except Exception as e:
        return Response(f"Fehler beim Lesen der Log-Datei: {e}", mimetype='text/plain')

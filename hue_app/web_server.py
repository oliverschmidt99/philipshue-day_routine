import os
import json
import logging
import time
from threading import Thread
from datetime import datetime
from flask import Flask, request, jsonify, render_template, Response

# Importiere die Konfigurationsklasse
from hue_app.core.configuration import Configuration

# --- Globale Konfiguration und Initialisierung ---
app = Flask(__name__.split('.')[0])

# Definiere die Pfade einmalig und für alle gültig
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_FILE = os.path.join(ROOT_DIR, 'config.yaml')
STATUS_FILE = os.path.join(ROOT_DIR, 'status.json')
LOG_FILE = os.path.join(ROOT_DIR, 'info.log')

# Logging-Konfiguration
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app.logger.setLevel(logging.INFO)

# --- Globale Objekte für den gemeinsamen Zugriff ---
config_manager = Configuration(config_file=CONFIG_FILE)
bridge = config_manager.bridge

# --- Hintergrund-Engine als Thread ---
def run_background_engine():
    """Diese Funktion läuft in einem separaten Thread und führt die Hue-Logik aus."""
    app.logger.info("Hintergrund-Engine wird gestartet...")
    
    time.sleep(2) # Warte kurz, damit der Webserver vollständig initialisiert ist
    
    routines = config_manager.initialize_routines()
    if not routines:
        app.logger.warning("Keine Routinen gefunden. Engine läuft im Leerlauf.")

    app.logger.info("Engine läuft. Starte Hauptschleife.")
    while True:
        try:
            now = datetime.now().astimezone()
            for routine in routines:
                routine.run(now)

            # Status schreiben
            status_data = [r.get_status() for r in routines]
            with open(STATUS_FILE, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2)

            time.sleep(1)
        except Exception as e:
            app.logger.error(f"Fehler in der Hintergrund-Engine: {e}", exc_info=True)
            time.sleep(5) # Warte bei einem Fehler, um die Logs nicht zu fluten

# Starte den Hintergrund-Thread, wenn die App initialisiert wird.
# 'daemon=True' sorgt dafür, dass der Thread beendet wird, wenn die Haupt-App stoppt.
engine_thread = Thread(target=run_background_engine, daemon=True)
engine_thread.start()

# --- API Endpunkte ---

@app.route('/')
def index():
    return render_template('hue.html')

@app.route('/api/config', methods=['GET'])
def handle_config():
    # Fürs Erste nur GET, um die Stabilität zu gewährleisten.
    # POST zum Neuladen der Konfiguration ist ein späterer Schritt.
    if config_manager.config:
        return Response(json.dumps(config_manager.config), mimetype='application/json')
    else:
        return jsonify({"error": "Konfiguration konnte nicht geladen werden."}), 500

@app.route('/api/bridge/<item>', methods=['GET'])
def get_bridge_data(item):
    # Greift auf das globale, einmal initialisierte Bridge-Objekt zu
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
        # Es ist normal, dass die Datei beim ersten Start noch nicht existiert
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/log', methods=['GET'])
def get_log():
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='text/plain')
    except FileNotFoundError:
        return Response("Log-Datei noch nicht erstellt.", mimetype='text/plain')
    except Exception as e:
        return Response(f"Fehler beim Lesen der Log-Datei: {e}", mimetype='text/plain')

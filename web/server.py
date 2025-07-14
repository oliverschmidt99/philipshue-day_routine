import os
import sys
from flask import Flask, request, jsonify, render_template, Response
import yaml
import json
import logging
from phue import Bridge

# Pfade an neue Struktur anpassen
# Wir gehen eine Ebene vom 'web'-Ordner nach oben
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
STATUS_FILE = os.path.join(os.path.dirname(__file__), '..', 'status.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'info.log')


# Flask so konfigurieren, dass es den 'templates'-Ordner im selben Verzeichnis findet
app = Flask(__name__, template_folder='templates')

# Werkzeug-Logs reduzieren, um die Konsole sauber zu halten
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)

bridge_connection = None

def get_bridge_connection():
    """Stellt eine Singleton-Verbindung zur Bridge für die API her."""
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
            app.logger.error(f"API kann keine Bridge-Verbindung herstellen: {e}")
            return None
    return bridge_connection

# === API Endpunkte ===

@app.route('/')
def index():
    # Der Name der Template-Datei wurde angepasst
    return render_template('index.html')

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'POST':
        try:
            data = request.json
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            # Hinweis: Ein Neustart der Logik muss nun manuell erfolgen,
            # da der Server nicht mehr die Kontrolle darüber hat.
            return jsonify({"message": "Konfiguration gespeichert. Bitte starte die Anwendung neu, um die Änderungen zu übernehmen."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else: # GET
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return Response(json.dumps(config), mimetype='application/json')
        except Exception as e:
            return jsonify({"error": f"Fehler beim Laden von {CONFIG_FILE}: {e}"}), 500

@app.route('/api/bridge/<item>', methods=['GET'])
def get_bridge_data(item):
    """Gibt Bridge-Informationen wie Gruppen oder Sensoren zurück."""
    bridge = get_bridge_connection()
    if not bridge:
        return jsonify({"error": "Keine Verbindung zur Bridge"}), 500
    try:
        if item == 'groups':
            data = bridge.get_group()
            # Nur Gruppen mit Typ "Room" oder "Zone" zurückgeben
            return jsonify([{"id": key, "name": value['name']} for key, value in data.items() if value.get('type') in ['Room', 'Zone']])
        elif item == 'sensors':
            data = bridge.get_sensor_objects('id')
            # Nur Bewegungsmelder (ZLLPresence) zurückgeben
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
        return jsonify([])
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


if __name__ == '__main__':
    # Stellt sicher, dass die Bridge-Verbindung beim Start verfügbar ist
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN'):
        get_bridge_connection()
    
    app.run(debug=True, host='0.0.0.0', port=5000)

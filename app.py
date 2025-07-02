from flask import Flask, request, jsonify, render_template, Response
import yaml
import os
import subprocess
import json # Importiere die json-Bibliothek

app = Flask(__name__)
CONFIG_FILE = 'config.yaml'
MAIN_SCRIPT = 'main.py'

# Globale Variable, um den Prozess des Hauptskripts zu speichern
main_process = None

def restart_main_script():
    """Stoppt den laufenden main.py Prozess (falls er läuft) und startet ihn neu."""
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


@app.route('/')
def index():
    """Rendert die Hauptseite der Weboberfläche."""
    return render_template('hue.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Liest die YAML-Datei und sendet sie als JSON an das Frontend."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Manuelle Umwandlung zu JSON, um den TypeError zu umgehen.
        # Wir erstellen eine Response direkt mit dem JSON-String.
        json_output = json.dumps(config, indent=2) # indent für bessere Lesbarkeit beim Debuggen
        return Response(json_output, mimetype='application/json')
        
    except FileNotFoundError:
        app.logger.error(f"API-Fehler: Konfigurationsdatei {CONFIG_FILE} nicht gefunden.")
        return jsonify({"error": f"Konfigurationsdatei {CONFIG_FILE} nicht gefunden."}), 404
    except Exception as e:
        app.logger.error(f"Ein Fehler ist beim Laden der Konfiguration für die API aufgetreten:", exc_info=True)
        return jsonify({"error": "Server-Fehler beim Laden der Konfiguration."}), 500

@app.route('/api/config', methods=['POST'])
def set_config():
    """Empfängt JSON-Daten vom Frontend, speichert sie und startet das Hauptskript neu."""
    try:
        data = request.json
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        restart_message = restart_main_script()
        
        return jsonify({"message": f"Konfiguration erfolgreich gespeichert. {restart_message}"})
    except Exception as e:
        app.logger.error(f"Fehler beim Speichern der Konfiguration:", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/restart', methods=['POST'])
def restart_script_endpoint():
    """Ermöglicht einen manuellen Neustart des Hauptskripts über die API."""
    message = restart_main_script()
    return jsonify({"message": message})


if __name__ == '__main__':
    # Diese robustere Bedingung verhindert den Doppelstart des Hauptskripts im Debug-Modus.
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN'):
        restart_main_script()
    
    # Starte den Flask-Server.
    app.run(debug=True, host='0.0.0.0', port=5000)

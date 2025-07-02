from flask import Flask, request, jsonify, render_template
import yaml
import os
import subprocess

app = Flask(__name__)
CONFIG_FILE = 'config.yaml'
MAIN_SCRIPT = 'main.py'

# Globale Variable, um den Prozess des Hauptskripts zu speichern
main_process = None

def restart_main_script():
    """Stoppt den laufenden main.py Prozess und startet ihn neu."""
    global main_process
    if main_process:
        print("Beende laufendes Hauptskript...")
        main_process.terminate()
        main_process.wait() # Warten, bis der Prozess wirklich beendet ist
    
    print("Starte Hauptskript neu...")
    # 'subprocess.Popen' startet das Skript in einem neuen Prozess
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
        return jsonify(config)
    except FileNotFoundError:
        return jsonify({"error": f"Konfigurationsdatei {CONFIG_FILE} nicht gefunden."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['POST'])
def set_config():
    """Empfängt JSON-Daten vom Frontend und speichert sie in der YAML-Datei."""
    try:
        data = request.json
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        
        # Nachdem die Konfiguration gespeichert wurde, starte das Hauptskript neu
        restart_message = restart_main_script()
        
        return jsonify({"message": f"Konfiguration erfolgreich gespeichert. {restart_message}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/restart', methods=['POST'])
def restart_script():
    """Ermöglicht einen manuellen Neustart des Hauptskripts über die API."""
    message = restart_main_script()
    return jsonify({"message": message})


if __name__ == '__main__':
    # Starte das Hauptskript einmal beim Start des Webservers
    restart_main_script()
    # Starte den Flask-Server, erreichbar im gesamten Netzwerk
    app.run(debug=True, host='0.0.0.0', port=5000)

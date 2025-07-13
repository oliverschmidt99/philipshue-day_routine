import os
import sys

# Fügt das Projektverzeichnis zum Pfad hinzu.
# Das ist notwendig, damit Python das 'hue_app'-Paket als Modul finden kann.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importiert die App-Instanz und die Startfunktionen aus dem neuen Paket
from hue_app.web_server import app, get_bridge_connection, restart_routine_engine

if __name__ == '__main__':
    """
    Diese Logik stellt sicher, dass die Routine-Engine nur einmal
    gestartet wird, auch wenn der Flask-Debugger aktiv ist.
    """
    # Die 'WERKZEUG_RUN_MAIN' Umgebungsvariable wird von Flask gesetzt,
    # um einen Neustart des Debuggers zu signalisieren.
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN'):
        print("--- Initialisiere Bridge-Verbindung und starte Routine-Engine ---")
        get_bridge_connection()
        restart_routine_engine()
    
    print("--- Starte Flask Web-Server auf http://0.0.0.0:5000 ---")
    # Führe die Flask-App aus
    app.run(debug=True, host='0.0.0.0', port=5000)
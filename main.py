import os
import sys

# Fügt das Projektverzeichnis zum Pfad hinzu, damit das hue_app-Paket gefunden wird.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Importiert die fertige App-Instanz aus dem Webserver-Modul
from hue_app.web_server import app

if __name__ == '__main__':
    print("--- Starte Flask Web-Server auf http://0.0.0.0:5000 ---")
    print("Die Hue-Logik läuft jetzt im Hintergrund dieses Prozesses.")
    
    # Starte die Flask-App. Der 'use_reloader=False' ist wichtig, damit der
    # Hintergrund-Thread im Debug-Modus nicht zweimal gestartet wird.
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
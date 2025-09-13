"""
Hauptanwendung für die Philips Hue Routine-Steuerung.
Startet den Webserver und die Kernlogik in parallelen Threads.
"""
import os
import sys
import logging
import time
from threading import Thread

# Füge das Projekt-Root zum Python-Pfad hinzu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.logger import Logger
from src.config_manager import ConfigManager
from src.core_logic import CoreLogic
# Importiere die App Factory direkt aus dem 'web' Paket
from web import create_app

# --- Globale Pfade ---
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "app.log")
CONFIG_FILE = os.path.join(DATA_DIR, "config.yaml")

def run_web_server(app):
    """Führt den Flask-Server aus."""
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def run_core_logic_loop(log, config_manager):
    """Führt die Hauptschleife der Kernlogik aus."""
    last_modified_time = 0

    while True:
        try:
            current_modified_time = config_manager.get_last_modified_time()
            if current_modified_time > last_modified_time:
                log.info("Änderung in der Konfiguration erkannt. Initialisiere Kernlogik neu.")
                last_modified_time = current_modified_time

            core_logic = CoreLogic(log, config_manager)
            config_is_complete = core_logic.run_main_loop()

            if not config_is_complete:
                log.warning("Konfiguration unvollständig, warte 30 Sekunden...")
                time.sleep(30)
            else:
                log.info("Kernlogik-Schleife wurde unterbrochen. Warte 5 Sekunden vor Neustart.")
                time.sleep(5)
        except Exception as e:
            log.error(f"Schwerwiegender Fehler in der Kernlogik-Schleife: {e}", exc_info=True)
            time.sleep(15)

def main():
    """Hauptfunktion der Anwendung."""
    os.makedirs(DATA_DIR, exist_ok=True)
    log = Logger(LOG_FILE, level=logging.INFO)
    config_manager = ConfigManager(CONFIG_FILE, log)

    log.info("Erstelle Flask-App-Instanz...")
    flask_app = create_app()

    log.info("Starte Webserver in einem Hintergrund-Thread...")
    web_server_thread = Thread(target=run_web_server, args=(flask_app,), daemon=True)
    web_server_thread.start()
    log.info("Webserver gestartet.")

    log.info("Starte Kernlogik-Schleife im Haupt-Thread...")
    run_core_logic_loop(log, config_manager)

# HIER IST DIE KORREKTUR: Nur main() aufrufen.
if __name__ == "__main__":
    main()
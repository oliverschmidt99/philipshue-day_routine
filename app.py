"""
Hauptanwendung für die Philips Hue Routine-Steuerung.
Initialisiert und startet den Webserver und die Kernlogik.
"""
import os
import sys
import logging
from multiprocessing import Process
from src.logger import Logger
from src.config_manager import ConfigManager
from src.core_logic import CoreLogic
from web import create_app

# Fügt das Projekt-Root-Verzeichnis zum Python-Pfad hinzu
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def run_flask_app():
    """Startet die Flask-Webanwendung."""
    flask_app = create_app()
    flask_app.logger_instance.info("Starte Flask-Server auf http://0.0.0.0:9090...")
    # use_reloader=False, da die Hauptschleife den Neustart steuert
    flask_app.run(host="0.0.0.0", port=9090, debug=True, use_reloader=False)

if __name__ == "__main__":
    # Pfaddefinitionen
    DATA_DIR = os.path.join(project_root, "data")
    LOG_FILE = os.path.join(DATA_DIR, "app.log")
    SETTINGS_FILE = os.path.join(DATA_DIR, "settings.yaml")
    AUTOMATION_FILE = os.path.join(DATA_DIR, "automation.yaml")
    HOME_FILE = os.path.join(DATA_DIR, "home.yaml")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    log = Logger(LOG_FILE, level=logging.INFO)

    # Starte den Flask-Server in einem separaten Prozess
    log.info("Initialisiere Webserver-Prozess...")
    flask_process = Process(target=run_flask_app, daemon=True)
    flask_process.start()
    log.info(f"Webserver-Prozess gestartet mit PID: {flask_process.pid}")

    # Starte die Kernlogik im Hauptprozess
    try:
        log.info("Starte Kernlogik...")
        config_manager = ConfigManager(SETTINGS_FILE, AUTOMATION_FILE, HOME_FILE, log)
        core_logic = CoreLogic(log, config_manager)
        core_logic.run_main_loop()
    except KeyboardInterrupt:
        log.info("Programm wird durch Benutzer beendet.")
    finally:
        log.info("Beende Webserver-Prozess...")
        if flask_process.is_alive():
            flask_process.terminate()
            flask_process.join()
        log.info("Programm sauber beendet.")
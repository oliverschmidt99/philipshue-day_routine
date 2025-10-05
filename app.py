import sys
import os
import time
from multiprocessing import Process, Manager
from src.logger import AppLogger
from src.config_manager import ConfigManager
from src.core_logic import CoreLogic
from web import create_app

def run_flask_app(shared_data):
    """Startet die Flask-Webanwendung in einem eigenen Prozess."""
    # KORREKTUR: Erstelle eine eigene Instanz für diesen Prozess.
    logger = shared_data["logger"]
    config_manager = ConfigManager(logger)
    
    flask_app = create_app(
        config_manager=config_manager,
        logger_instance=logger,
        app_config=shared_data["app_config"]
    )

    logger.info(f"Starte Flask-Server auf http://0.0.0.0:9090...")
    
    try:
        # Host und Port anpassen, falls nötig
        flask_app.run(host='0.0.0.0', port=9090, debug=False, use_reloader=False)
    except Exception as e:
        logger.error(f"Flask-Server unerwartet beendet: {e}", exc_info=True)

def run_core_logic(shared_data):
    """Startet die Kernlogik in einem eigenen Prozess."""
    logger = shared_data["logger"]
    # KORREKTUR: Erstelle eine eigene Instanz für diesen Prozess.
    config_manager = ConfigManager(logger)
    
    logger.info("Starte Kernlogik...")
    core_logic = CoreLogic(
        log=logger,
        config_manager=config_manager
    )
    core_logic.run_main_loop()

if __name__ == '__main__':
    # Logger wird einmalig erstellt und kann geteilt werden
    logger = AppLogger(log_file="data/app.log").get_logger()
    logger.info("Initialisiere Anwendung...")

    # Der Manager wird nur noch für einfache Daten verwendet
    manager = Manager()
    shared_data = manager.dict()

    # Wir lesen die Konfig einmalig im Hauptprozess, um sie an die Subprozesse zu übergeben.
    # Die Subprozesse erstellen dann ihre eigenen Manager-Instanzen für das Neuladen.
    temp_config_manager = ConfigManager(logger)
    config = temp_config_manager.get_full_config()
    
    # KORREKTUR: Teile nur "picklable" Objekte.
    shared_data["logger"] = logger
    shared_data["app_config"] = {
        "bridge_ip": config.get("bridge_ip"),
        "app_key": config.get("app_key")
    }

    logger.info("Initialisiere Webserver-Prozess...")
    p_flask = Process(target=run_flask_app, args=(shared_data,))
    p_flask.start()
    logger.info(f"Webserver-Prozess gestartet mit PID: {p_flask.pid}")
    
    logger.info("Initialisiere Kernlogik-Prozess...")
    p_core = Process(target=run_core_logic, args=(shared_data,))
    p_core.start()
    logger.info(f"Kernlogik-Prozess gestartet mit PID: {p_core.pid}")

    try:
        p_flask.join()
        p_core.join()
    except KeyboardInterrupt:
        logger.info("Anwendung wird beendet.")
        p_flask.terminate()
        p_core.terminate()
        p_flask.join()
        p_core.join()
        logger.info("Prozesse erfolgreich beendet.")
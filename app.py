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
    flask_app = create_app(
        config_manager=shared_data["config_manager"],
        logger_instance=shared_data["logger"],
        app_config=shared_data["app_config"]  # Übergibt die Konfiguration
    )

    flask_app.logger_instance.info(f"Starte Flask-Server auf http://0.0.0.0:9090...")
    
    try:
        flask_app.run(host='0.0.0.0', port=9090, debug=False, use_reloader=False)
    except Exception as e:
        flask_app.logger_instance.error(f"Flask-Server unerwartet beendet: {e}", exc_info=True)

def run_core_logic(shared_data):
    """Startet die Kernlogik in einem eigenen Prozess."""
    logger = shared_data["logger"]
    logger.info("Starte Kernlogik...")
    core_logic = CoreLogic(
        log=logger,
        config_manager=shared_data["config_manager"]
    )
    core_logic.run_main_loop()

if __name__ == '__main__':
    logger = AppLogger().get_logger()
    logger.info("Initialisiere Anwendung...")

    manager = Manager()
    shared_data = manager.dict()

    config_manager = ConfigManager(logger)
    config = config_manager.get_full_config()
    
    # HIER DIE ÄNDERUNG: Keine Bridge-Instanz wird hier mehr erstellt.
    # Stattdessen teilen wir nur die notwendigen Konfigurationsdaten.
    shared_data["config_manager"] = config_manager
    shared_data["logger"] = logger
    shared_data["app_config"] = {
        "bridge_ip": config.get("bridge_ip"),
        "app_key": config.get("app_key")
    }

    logger.info("Initialisiere Webserver-Prozess...")
    p_flask = Process(target=run_flask_app, args=(shared_data,))
    p_flask.start()
    logger.info(f"Webserver-Prozess gestartet mit PID: {p_flask.pid}")
    
    # Die Kernlogik erstellt ihre eigene Bridge-Verbindung in der Schleife,
    # was bereits eine gute Praxis ist.
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
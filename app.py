import sys
import os
import time
from multiprocessing import Process, Manager
from src.logger import AppLogger
from src.config_manager import ConfigManager
from src.hue_wrapper import HueBridge
from src.core_logic import CoreLogic
from web import create_app

def run_flask_app(shared_data):
    """Startet die Flask-Webanwendung in einem eigenen Prozess."""
    
    # *** KORREKTUR: Übergebe die Instanzen direkt beim Erstellen der App ***
    flask_app = create_app(
        config_manager=shared_data["config_manager"],
        bridge_instance=shared_data["bridge_instance"],
        logger_instance=shared_data["logger"]
    )

    flask_app.logger_instance.info(f"Starte Flask-Server auf http://0.0.0.0:9090...")
    
    try:
        # deaktiviere den reloader, da wir den Neustart manuell über die restart.flag steuern
        flask_app.run(host='0.0.0.0', port=9090, debug=True, use_reloader=False)
    except Exception as e:
        flask_app.logger_instance.error(f"Flask-Server unerwartet beendet: {e}", exc_info=True)

def run_core_logic(shared_data):
    """Startet die Kernlogik in einem eigenen Prozess."""
    logger = shared_data["logger"]
    logger.info("Starte Kernlogik...")
    core_logic = CoreLogic(
        config_manager=shared_data["config_manager"],
        bridge=shared_data["bridge_instance"],
        logger=logger
    )
    core_logic.run()

if __name__ == '__main__':
    logger = AppLogger().get_logger()
    logger.info("Initialisiere Anwendung...")

    manager = Manager()
    shared_data = manager.dict()

    config_manager = ConfigManager(logger)
    config = config_manager.get_full_config()
    
    bridge = HueBridge(
        ip=config.get("bridge_ip"),
        app_key=config.get("app_key"),
        logger=logger
    )
    bridge.connect()

    shared_data["config_manager"] = config_manager
    shared_data["bridge_instance"] = bridge
    shared_data["logger"] = logger

    logger.info("Initialisiere Webserver-Prozess...")
    p_flask = Process(target=run_flask_app, args=(shared_data,))
    p_flask.start()
    logger.info(f"Webserver-Prozess gestartet mit PID: {p_flask.pid}")

    p_core = Process(target=run_core_logic, args=(shared_data,))
    p_core.start()
    logger.info(f"Kernlogik-Prozess gestartet mit PID: {p_core.pid}")

    try:
        while True:
            time.sleep(2)
            # Überprüfe auf Neustart-Signal
            restart_flag = os.path.join(os.path.dirname(__file__), "data", "restart.flag")
            if os.path.exists(restart_flag):
                logger.warning("Neustart-Signal erkannt. Starte Anwendung neu...")
                os.remove(restart_flag)
                
                # Beende alte Prozesse
                p_flask.terminate()
                p_core.terminate()
                p_flask.join()
                p_core.join()
                
                # Starte das Skript neu
                os.execv(sys.executable, ['python'] + sys.argv)

    except KeyboardInterrupt:
        logger.info("Anwendung wird beendet.")
        p_flask.terminate()
        p_core.terminate()
        p_flask.join()
        p_core.join()
        logger.info("Prozesse erfolgreich beendet.")
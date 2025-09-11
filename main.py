"""
Hauptanwendung für die Philips Hue Routine-Steuerung.
Initialisiert und startet den Webserver und die Kernlogik in einer
Schleife, um Neustarts nach Konfigurationsänderungen zu ermöglichen.
"""

import os
import sys
import subprocess
import atexit
import logging
import time

from src.logger import Logger
from src.config_manager import ConfigManager
from src.core_logic import CoreLogic

# --- Globale Pfade ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "app.log")
CONFIG_FILE = os.path.join(DATA_DIR, "config.yaml")
SERVER_SCRIPT = os.path.join(BASE_DIR, "web", "server.py")
RESTART_FLAG_FILE = os.path.join(DATA_DIR, "restart.flag")


def cleanup(log, server_process):
    """Wird bei Programmende ausgeführt, um den Webserver-Prozess sicher zu beenden."""
    if log:
        log.info("\nRäume auf und beende den Webserver-Prozess...")
    if server_process:
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
            if log:
                log.info("Webserver-Prozess erfolgreich beendet.")
        except subprocess.TimeoutExpired:
            if log:
                log.warning("Webserver-Prozess reagiert nicht, erzwinge Beendigung.")
            server_process.kill()
    if log:
        log.info("Programm beendet.")


def main():
    """Hauptfunktion der Anwendung."""
    os.makedirs(DATA_DIR, exist_ok=True)
    log = Logger(LOG_FILE, level=logging.INFO)

    log.info(f"Starte Webserver: {sys.executable} {SERVER_SCRIPT}")
    server_process = subprocess.Popen([sys.executable, SERVER_SCRIPT])
    log.info(f"Webserver-Prozess gestartet mit PID: {server_process.pid}")

    atexit.register(cleanup, log, server_process)

    while True:
        if os.path.exists(RESTART_FLAG_FILE):
            log.info("Neustart-Signal erkannt. Entferne Flag-Datei.")
            os.remove(RESTART_FLAG_FILE)

        log.info("Initialisiere Kernlogik...")
        config_manager = ConfigManager(CONFIG_FILE, log)
        core_logic = CoreLogic(log, config_manager)
        
        # Führe die Logik aus. Sie gibt `False` zurück, wenn gewartet werden soll.
        config_is_complete = core_logic.run_main_loop()

        if not config_is_complete:
            log.info("Konfiguration unvollständig, warte 15 Sekunden...")
            time.sleep(15)
        else:
            log.info("Kernlogik-Schleife wurde beendet. Warte 2 Sekunden vor Neustart.")
            time.sleep(2)


if __name__ == "__main__":
    main()
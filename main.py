"""
Hauptanwendung für die Philips Hue Routine-Steuerung.
Initialisiert und startet den Webserver und die Kernlogik.
"""

import os
import sys
import time
import subprocess
import atexit
import logging
from src.logger import Logger
from src.config_manager import ConfigManager
from src.core_logic import CoreLogic

# --- Globale Pfade ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "app.log")
CONFIG_FILE = os.path.join(DATA_DIR, "config.yaml")
SERVER_SCRIPT = os.path.join(BASE_DIR, "web", "server.py")

SERVER_PROCESS = None
LOG = None


def main():
    """Hauptfunktion der Anwendung."""
    global LOG
    os.makedirs(DATA_DIR, exist_ok=True)
    LOG = Logger(LOG_FILE, level=logging.INFO)

    # Setze den PYTHONPATH für den Unterprozess, damit er 'src' findet
    env = os.environ.copy()
    env["PYTHONPATH"] = BASE_DIR + os.pathsep + env.get("PYTHONPATH", "")

    # Startet den Webserver als separaten Prozess
    global SERVER_PROCESS
    LOG.info(f"Starte Webserver: {sys.executable} {SERVER_SCRIPT}")
    SERVER_PROCESS = subprocess.Popen([sys.executable, SERVER_SCRIPT], env=env)
    LOG.info(f"Webserver-Prozess gestartet mit PID: {SERVER_PROCESS.pid}")

    atexit.register(cleanup)

    config_manager = ConfigManager(CONFIG_FILE, LOG)

    # Startet die Hauptlogik-Schleife
    core_logic = CoreLogic(LOG, config_manager)
    core_logic.run_main_loop()


def cleanup():
    """Wird bei Programmende ausgeführt, um den Webserver zu beenden."""
    if LOG:
        LOG.info("\nRäume auf und beende den Webserver-Prozess...")
    if SERVER_PROCESS:
        SERVER_PROCESS.terminate()
        try:
            SERVER_PROCESS.wait(timeout=5)
            if LOG:
                LOG.info("Webserver-Prozess erfolgreich beendet.")
        except subprocess.TimeoutExpired:
            if LOG:
                LOG.warning("Webserver-Prozess reagiert nicht, erzwinge Beendigung.")
            SERVER_PROCESS.kill()
    if LOG:
        LOG.info("Programm beendet.")


if __name__ == "__main__":
    main()

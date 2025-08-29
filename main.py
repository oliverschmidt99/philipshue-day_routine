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
SERVER_SCRIPT = os.path.join(BASE_DIR, "web", "server.py")

SERVER_PROCESS = None


def main():
    """Hauptfunktion der Anwendung."""
    os.makedirs(DATA_DIR, exist_ok=True)
    log = Logger(LOG_FILE, level=logging.INFO)
    config_manager = ConfigManager(log)

    # Startet den Webserver als separaten Prozess
    global SERVER_PROCESS
    SERVER_PROCESS = subprocess.Popen([sys.executable, SERVER_SCRIPT])

    atexit.register(cleanup)

    # Startet die Hauptlogik-Schleife
    core_logic = CoreLogic(log, config_manager)
    core_logic.run_main_loop()


def cleanup():
    """Wird bei Programmende ausgeführt, um den Webserver zu beenden."""
    print("\nRäume auf und beende den Webserver-Prozess...")
    if SERVER_PROCESS:
        SERVER_PROCESS.terminate()
        SERVER_PROCESS.wait()
    print("Programm beendet.")


if __name__ == "__main__":
    main()

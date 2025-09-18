"""
Hauptanwendung für die Philips Hue Routine-Steuerung.
Initialisiert und startet den Webserver und die Kernlogik.
"""
import os
import sys
import subprocess
import atexit
import logging
from src.logger import Logger
from src.config_manager import ConfigManager
from src.core_logic import CoreLogic

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "app.log")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.yaml")
AUTOMATION_FILE = os.path.join(DATA_DIR, "automation.yaml")
HOME_FILE = os.path.join(DATA_DIR, "home.yaml")
SERVER_SCRIPT = os.path.join(BASE_DIR, "web", "server.py")

def cleanup(log, server_process):
    if server_process:
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
    log.info("Programm beendet.")

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    log = Logger(LOG_FILE, level=logging.INFO)

    log.info(f"Starte Webserver: {sys.executable} {SERVER_SCRIPT}")
    server_process = subprocess.Popen([sys.executable, SERVER_SCRIPT])
    log.info(f"Webserver-Prozess gestartet mit PID: {server_process.pid}")

    atexit.register(cleanup, log, server_process)
    
    config_manager = ConfigManager(SETTINGS_FILE, AUTOMATION_FILE, HOME_FILE, log)
    core_logic = CoreLogic(log, config_manager)
    core_logic.run_main_loop()

if __name__ == "__main__":
    main()
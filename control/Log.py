import logging
import os

# Define the path for the log file
aktueller_pfad = os.path.dirname(__file__)
datei_log = "info.log"
pfad_log = os.path.join(aktueller_pfad, datei_log)

# Customize the logging format to include columns: DATE | ROOM | ACTION | STATE
log_format = "%(asctime)s | %(room)-15s | %(action)-20s | %(state)-10s | %(message)s"

# Set up logging configuration
logging.basicConfig(
    filename=pfad_log,
    level=logging.INFO,
    format=log_format,
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Custom log function to add room, action, and state
def log_room_action(room, action, state):
    logging.info("Action performed", extra={"room": room, "action": action, "state": state})


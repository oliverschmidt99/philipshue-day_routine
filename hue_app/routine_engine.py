import sys
import os
import time
import json
from datetime import datetime

# Fügt das Projekt-Root-Verzeichnis zum Pfad hinzu, damit das hue_app-Paket gefunden wird.
# Notwendig, da dieses Skript als separater Prozess läuft.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Korrekte, explizite Imports aus dem hue_app-Paket
from hue_app.core.configuration import Configuration
from hue_app.core.routine import Routine
from hue_app.core.logger import Logger

# Pfade relativ zum Projekt-Root definieren
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
STATUS_FILE = os.path.join(ROOT_DIR, 'status.json')
CONFIG_FILE = os.path.join(ROOT_DIR, 'config.yaml')
LOG_FILE = os.path.join(ROOT_DIR, 'info.log')


def write_status(routines, log):
    """Sammelt den Status aller Routinen und schreibt ihn in eine JSON-Datei."""
    status_data = [r.get_status() for r in routines]
    try:
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        log.error(f"Fehler beim Schreiben der Status-Datei: {e}", exc_info=True)

def main():
    """
    Die Hauptfunktion, die die Hue-Routine initialisiert und ausführt.
    """
    log = Logger(LOG_FILE)
    log.info("--- Starte Philips Hue Routine-Engine ---")

    try:
        config_manager = Configuration(config_file=CONFIG_FILE, log=log)
        if not config_manager.config or not config_manager.bridge:
            log.error("Initialisierung fehlgeschlagen. Beende Engine.")
            return

        routines = config_manager.initialize_routines()

        if not routines:
            log.warning("Keine Routinen zum Ausführen gefunden. Engine läuft im Leerlauf.")
        
        log.info("Initialisierung der Engine abgeschlossen. Starte Hauptschleife.")
        last_status_write = time.time()
        
        while True:
            now = datetime.now().astimezone()
            for routine in routines:
                routine.run(now)
            
            if time.time() - last_status_write > 5:
                write_status(routines, log)
                last_status_write = time.time()

            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        log.info("Routine-Engine wird auf Anfrage beendet.")
    except Exception as e:
        log.error(f"Kritischer Fehler in der Routine-Engine: {e}", exc_info=True)
    finally:
        if os.path.exists(STATUS_FILE):
            try:
                os.remove(STATUS_FILE)
                log.info(f"Status-Datei '{STATUS_FILE}' wurde aufgeräumt.")
            except OSError as e:
                log.error(f"Fehler beim Löschen der Status-Datei: {e}")
        log.info("--- Philips Hue Routine-Engine beendet ---")


if __name__ == "__main__":
    main()

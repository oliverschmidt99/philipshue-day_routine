import time
import yaml
from datetime import datetime

from control.huebridge import HueBridge
from control.scene import Scene
from control.Room import Room
from control.Sensor import Sensor
from control.Routine import Routine
from control.Daily_time_span import Daily_time_span
from control.Log import Log

CONFIG_FILE = 'config.yaml'

def load_config():
    """Lädt die Konfiguration aus der YAML-Datei."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Fehler: Die Konfigurationsdatei '{CONFIG_FILE}' wurde nicht gefunden.")
        exit()
    except Exception as e:
        print(f"Fehler beim Laden der Konfiguration: {e}")
        exit()

def main():
    """Initialisiert und startet die Lichtsteuerung."""
    log = Log("info.log")
    log.info("Starte Philips Hue Routine...")

    config = load_config()
    if not config:
        return

    try:
        bridge = HueBridge(config['bridge_ip'], log)
        
        # 1. Szenen erstellen
        scenes = {name: Scene(**params) for name, params in config.get('scenes', {}).items()}

        # 2. Räume und Sensoren erstellen
        rooms = {room_conf['name']: Room(bridge, log, **room_conf) for room_conf in config.get('rooms', [])}
        sensors = {
            room_conf['name']: Sensor(bridge, room_conf['sensor_id']) 
            for room_conf in config.get('rooms', [])
        }

        # 3. Routinen erstellen
        routines = []
        for routine_conf in config.get('routines', []):
            room_name = routine_conf.get('room_name')
            room = rooms.get(room_name)
            sensor = sensors.get(room_name)
            
            if not room or not sensor:
                log.error(f"Raum oder Sensor für Routine '{routine_conf['name']}' nicht gefunden. Überspringe.")
                continue

            # Erstelle das Daily_time_span Objekt
            time_span_conf = routine_conf.get('daily_time', {})
            daily_time_span = Daily_time_span(
                time_span_conf.get('H1', 0), time_span_conf.get('M1', 0),
                time_span_conf.get('H2', 23), time_span_conf.get('M2', 59)
            )

            # Erstelle die Routine
            routine = Routine(
                name=routine_conf['name'],
                room=room,
                sensor=sensor,
                daily_time_span=daily_time_span,
                sections_config=routine_conf.get('sections', {}),
                scenes=scenes,
                log=log
            )
            routines.append(routine)
            log.info(f"Routine '{routine.name}' für Raum '{room.name}' erfolgreich geladen.")

        if not routines:
            log.warning("Keine Routinen zum Ausführen gefunden. Beende.")
            return

        # 4. Hauptschleife
        log.info("Initialisierung abgeschlossen. Starte Hauptschleife.")
        while True:
            now = datetime.now()
            for routine in routines:
                routine.run(now)
            time.sleep(1)

    except Exception as e:
        log.error(f"Ein kritischer Fehler ist aufgetreten: {e}", exc_info=True)
        print(f"Ein kritischer Fehler ist aufgetreten. Details siehe 'info.log'.")

if __name__ == "__main__":
    main()

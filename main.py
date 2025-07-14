import time
import yaml
import json
import os
from datetime import datetime, date
from phue import Bridge
from astral.sun import sun
from astral import LocationInfo

from control.scene import Scene
from control.Room import Room
from control.Sensor import Sensor
from control.Routine import Routine
from control.logger import Logger

CONFIG_FILE = 'config.yaml'
STATUS_FILE = 'status.json'

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

def connect_bridge(ip, log):
    """Stellt die Verbindung zur Hue Bridge her."""
    log.info(f"Versuche, eine Verbindung zur Bridge unter {ip} herzustellen...")
    try:
        b = Bridge(ip)
        b.connect()
        log.info("Verbindung zur Hue Bridge erfolgreich hergestellt.")
        return b
    except Exception as e:
        log.error(f"Konnte keine Verbindung zur Bridge herstellen: {e}", exc_info=True)
        exit()

def get_sun_times(location_config, log):
    """Berechnet die Sonnenauf- und -untergangszeiten für den aktuellen Tag."""
    if not location_config:
        log.warning("Keine Standort-Informationen in config.yaml gefunden. Sonnenzeiten können nicht berechnet werden.")
        return None
    try:
        loc = LocationInfo(
            "Home", "Germany", "Europe/Berlin",
            location_config['latitude'], location_config['longitude']
        )
        s = sun(loc.observer, date=date.today(), tzinfo=loc.timezone)
        log.info(f"Sonnenzeiten für heute berechnet: Aufgang={s['sunrise'].strftime('%H:%M')}, Untergang={s['sunset'].strftime('%H:%M')}")
        return {"sunrise": s['sunrise'], "sunset": s['sunset']}
    except Exception as e:
        log.error(f"Fehler bei der Berechnung der Sonnenzeiten: {e}", exc_info=True)
        return None

def write_status(routines):
    """Sammelt den Status aller Routinen und schreibt ihn in eine Datei."""
    status_data = [r.get_status() for r in routines]
    try:
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        print(f"Fehler beim Schreiben der Status-Datei: {e}")

def main():
    log = Logger("info.log")
    log.info("Starte Philips Hue Routine...")

    config = load_config()
    if not config:
        return

    try:
        bridge = connect_bridge(config['bridge_ip'], log)
        sun_times = get_sun_times(config.get('location'), log)
        
        scenes = {name: Scene(**params) for name, params in config.get('scenes', {}).items()}
        room_to_sensor_map = {room.get('name'): room.get('sensor_id') for room in config.get('rooms', [])}
        rooms = {room_conf['name']: Room(bridge, log, **room_conf) for room_conf in config.get('rooms', [])}
        sensors = {name: Sensor(bridge, sensor_id, log) for name, sensor_id in room_to_sensor_map.items() if sensor_id}

        routines = []
        for routine_conf in config.get('routines', []):
            room_name = routine_conf['room_name']
            room = rooms.get(room_name)
            sensor_id = room_to_sensor_map.get(room_name)
            sensor = sensors.get(room_name) if sensor_id else None

            if not room:
                log.error(f"Raum '{room_name}' für Routine '{routine_conf['name']}' nicht gefunden. Überspringe.")
                continue

            routines.append(Routine(
                name=routine_conf['name'], room=room, sensor=sensor,
                routine_config=routine_conf, scenes=scenes, sun_times=sun_times, log=log
            ))
            log.info(f"Routine '{routine_conf['name']}' für Raum '{room_name}' erfolgreich geladen.")

        if not routines:
            log.warning("Keine Routinen zum Ausführen gefunden. Beende.")
            return

        log.info("Initialisierung abgeschlossen. Starte Hauptschleife.")
        last_status_write = time.time()
        while True:
            now = datetime.now().astimezone()
            for routine in routines:
                routine.run(now)
            
            if time.time() - last_status_write > 5:
                write_status(routines)
                last_status_write = time.time()

            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        log.info("Programm wird beendet.")
        # KORRIGIERT: Prüft, ob die Datei existiert, bevor sie gelöscht wird.
        if os.path.exists(STATUS_FILE):
            try:
                os.remove(STATUS_FILE)
                log.info(f"Status-Datei '{STATUS_FILE}' wurde aufgeräumt.")
            except OSError as e:
                log.error(f"Fehler beim Löschen der Status-Datei: {e}")
    except Exception as e:
        log.error(f"Ein kritischer Fehler ist aufgetreten: {e}", exc_info=True)

if __name__ == "__main__":
    main()

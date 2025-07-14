import time
import yaml
import json
import os
import subprocess
import atexit
from datetime import datetime, date
from phue import Bridge
from astral.sun import sun
from astral import LocationInfo

# Angepasste Importe für die neue Struktur
from src.scene import Scene
from src.room import Room
from src.sensor import Sensor
from src.routine import Routine
from src.logger import Logger

CONFIG_FILE = 'config.yaml'
STATUS_FILE = 'status.json'
LOG_FILE = 'info.log'
SERVER_SCRIPT = os.path.join('web', 'server.py')

# Hält den Prozess für den Webserver
server_process = None

def load_config(log):
    """Lädt die Konfiguration aus der YAML-Datei."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        log.error(f"Fehler: Die Konfigurationsdatei '{CONFIG_FILE}' wurde nicht gefunden.")
        return None
    except Exception as e:
        log.error(f"Fehler beim Laden der Konfiguration: {e}")
        return None

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
        return None

def get_sun_times(location_config, log):
    """Berechnet die Sonnenauf- und -untergangszeiten."""
    if not location_config:
        log.warning("Keine Standort-Informationen in config.yaml gefunden.")
        return None
    try:
        loc = LocationInfo(
            "Home", "Germany", "Europe/Berlin",
            location_config['latitude'], location_config['longitude']
        )
        s = sun(loc.observer, date=date.today(), tzinfo=loc.timezone)
        log.info(f"Sonnenzeiten: Aufgang={s['sunrise']:%H:%M}, Untergang={s['sunset']:%H:%M}")
        return {"sunrise": s['sunrise'], "sunset": s['sunset']}
    except Exception as e:
        log.error(f"Fehler bei der Berechnung der Sonnenzeiten: {e}", exc_info=True)
        return None

def write_status(routines):
    """Schreibt den aktuellen Status aller Routinen in eine Datei."""
    status_data = [r.get_status() for r in routines]
    try:
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        print(f"Fehler beim Schreiben der Status-Datei: {e}")

def run_logic(log):
    """Die Hauptschleife, die die Routinen ausführt."""
    log.info("Starte Hue-Logik...")
    config = load_config(log)
    if not config:
        return

    bridge = connect_bridge(config['bridge_ip'], log)
    if not bridge:
        return

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
            log.error(f"Raum '{room_name}' für Routine '{routine_conf['name']}' nicht gefunden.")
            continue

        routines.append(Routine(
            name=routine_conf['name'], room=room, sensor=sensor,
            routine_config=routine_conf, scenes=scenes, sun_times=sun_times, log=log
        ))
        log.info(f"Routine '{routine_conf['name']}' für Raum '{room_name}' geladen.")

    if not routines:
        log.warning("Keine Routinen gefunden. Beende Logik-Thread.")
        return

    log.info("Initialisierung abgeschlossen. Starte Hauptschleife.")
    last_status_write = time.time()
    while True:
        try:
            now = datetime.now().astimezone()
            for routine in routines:
                routine.run(now)
            
            if time.time() - last_status_write > 5:
                write_status(routines)
                last_status_write = time.time()

            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            break
        except Exception as e:
            log.error(f"Ein kritischer Fehler in der Hauptschleife ist aufgetreten: {e}", exc_info=True)


def start_server(log):
    """Startet den Flask-Webserver als separaten Prozess."""
    global server_process
    log.info("Starte den Webserver...")
    # 'os.sys.executable' stellt sicher, dass dasselbe Python-Environment genutzt wird
    server_process = subprocess.Popen([os.sys.executable, SERVER_SCRIPT])


def cleanup():
    """Räumt auf, wenn das Programm beendet wird."""
    print("\nRäume auf und beende Prozesse...")
    if server_process and server_process.poll() is None:
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
    
    if os.path.exists(STATUS_FILE):
        try:
            os.remove(STATUS_FILE)
            print(f"Status-Datei '{STATUS_FILE}' wurde entfernt.")
        except OSError as e:
            print(f"Fehler beim Löschen der Status-Datei: {e}")
    print("Programm beendet.")


if __name__ == "__main__":
    log = Logger(LOG_FILE)
    start_server(log)
    
    atexit.register(cleanup)
    
    try:
        run_logic(log)
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        log.error(f"Ein unerwarteter Fehler hat das Hauptprogramm beendet: {e}", exc_info=True)

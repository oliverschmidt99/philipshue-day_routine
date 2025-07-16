import time
import yaml
import json
import os
import subprocess
import atexit
import sqlite3
import threading
import logging
import sys
from datetime import datetime, date, timedelta
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
DB_FILE = 'sensor_data.db'
SERVER_SCRIPT = os.path.join('web', 'server.py')

# Hält den Prozess für den Webserver
server_process = None
data_logger_thread = None
stop_event = threading.Event()

def init_database(log):
    """Initialisiert die SQLite-Datenbank und erstellt die Tabelle, falls sie nicht existiert."""
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS measurements (
                timestamp TEXT NOT NULL,
                sensor_id INTEGER NOT NULL,
                measurement_type TEXT NOT NULL,
                value REAL NOT NULL,
                PRIMARY KEY (timestamp, sensor_id, measurement_type)
            )
        ''')
        con.commit()
        con.close()
        log.info("Datenbank 'sensor_data.db' erfolgreich initialisiert.")
    except Exception as e:
        log.error(f"Fehler bei der Initialisierung der Datenbank: {e}", exc_info=True)

def data_logger_worker(sensors, interval_minutes, log):
    """Ein Worker-Thread, der periodisch Sensordaten in die DB schreibt."""
    log.info(f"Datenlogger-Thread gestartet. Intervall: {interval_minutes} Minuten.")
    while not stop_event.is_set():
        try:
            now = datetime.now()
            seconds_until_next_log = (interval_minutes * 60) - (now.timestamp() % (interval_minutes * 60))
            log.debug(f"Datenlogger: Warte {seconds_until_next_log:.0f} Sekunden bis zur nächsten Messung.")
            
            stopped = stop_event.wait(seconds_until_next_log)
            if stopped:
                break

            con = sqlite3.connect(DB_FILE)
            cur = con.cursor()
            timestamp = datetime.now().isoformat()
            
            for sensor in sensors:
                brightness = sensor.get_brightness()
                temperature = sensor.get_temperature()
                
                log.debug(f"Datenlogger: Sensor {sensor.motion_sensor_id} -> Helligkeit={brightness}, Temp={temperature}")

                cur.execute("INSERT OR IGNORE INTO measurements VALUES (?, ?, ?, ?)",
                            (timestamp, sensor.light_sensor_id, 'brightness', brightness))
                
                cur.execute("INSERT OR IGNORE INTO measurements VALUES (?, ?, ?, ?)",
                            (timestamp, sensor.temp_sensor_id, 'temperature', temperature))

            con.commit()
            con.close()
            log.debug("Sensordaten erfolgreich in die Datenbank geschrieben.")
        except Exception as e:
            log.error(f"Fehler im Datenlogger-Thread: {e}", exc_info=True)
            stop_event.wait(60)

    log.info("Datenlogger-Thread beendet.")


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
        loc = LocationInfo("Home", "Germany", "Europe/Berlin", location_config['latitude'], location_config['longitude'])
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
    """Die Hauptschleife, die die Routinen ausführt. Gibt True zurück, wenn sie neu gestartet werden soll."""
    global data_logger_thread
    log.info("Lade Konfiguration und starte Hue-Logik...")
    config = load_config(log)
    if not config:
        return False

    global_settings = config.get('global_settings', {})
    datalogger_interval = global_settings.get('datalogger_interval_minutes', 15)
    status_interval = global_settings.get('status_interval_s', 5)

    try:
        last_mod_time = os.path.getmtime(CONFIG_FILE)
    except OSError as e:
        log.error(f"Konnte Modifikationszeit von '{CONFIG_FILE}' nicht lesen: {e}")
        return False

    bridge = connect_bridge(config['bridge_ip'], log)
    if not bridge:
        return False

    sun_times = get_sun_times(config.get('location'), log)
    
    scenes = {name: Scene(**params) for name, params in config.get('scenes', {}).items()}
    
    # KORREKTUR: Lade ALLE Bewegungssensoren für den Datenlogger
    try:
        all_sensors_data = bridge.get_sensor()
        all_motion_sensor_ids = [int(sid) for sid, data in all_sensors_data.items() if data.get('type') == 'ZLLPresence']
        log.info(f"Gefundene Bewegungssensoren auf der Bridge: {all_motion_sensor_ids}")
        all_sensor_objects_for_logger = [Sensor(bridge, sensor_id, log) for sensor_id in all_motion_sensor_ids]
    except Exception as e:
        log.error(f"Fehler beim Abrufen aller Sensoren von der Bridge: {e}")
        all_sensor_objects_for_logger = []

    # Erstelle Sensor-Objekte nur für die in Routinen verwendeten Sensoren
    unique_sensor_ids_in_routines = {room.get('sensor_id') for room in config.get('rooms', []) if room.get('sensor_id')}
    sensors_for_routines = [Sensor(bridge, sensor_id, log) for sensor_id in unique_sensor_ids_in_routines]
    
    room_to_sensor_map = {}
    for room_conf in config.get('rooms', []):
        sensor_id = room_conf.get('sensor_id')
        if sensor_id:
            sensor_obj = next((s for s in sensors_for_routines if s.motion_sensor_id == sensor_id), None)
            room_to_sensor_map[room_conf['name']] = sensor_obj

    rooms = {room_conf['name']: Room(bridge, log, **room_conf) for room_conf in config.get('rooms', [])}

    routines = []
    for routine_conf in config.get('routines', []):
        room_name = routine_conf['room_name']
        room = rooms.get(room_name)
        sensor = room_to_sensor_map.get(room_name)

        if not room:
            log.error(f"Raum '{room_name}' für Routine '{routine_conf['name']}' nicht gefunden.")
            continue

        routines.append(Routine(
            name=routine_conf['name'], room=room, sensor=sensor,
            routine_config=routine_conf, scenes=scenes, sun_times=sun_times, log=log, global_settings=global_settings
        ))
    
    if routines:
        log.info(f"{len(routines)} Routine(n) erfolgreich geladen.")
    else:
        log.warning("Keine Routinen in der Konfiguration gefunden.")

    if data_logger_thread is None or not data_logger_thread.is_alive():
        stop_event.clear()
        # Übergebe ALLE Sensoren an den Logger
        data_logger_thread = threading.Thread(target=data_logger_worker, args=(all_sensor_objects_for_logger, datalogger_interval, log))
        data_logger_thread.daemon = True
        data_logger_thread.start()

    log.info("Initialisierung abgeschlossen. Starte Hauptschleife.")
    last_status_write = time.time()
    
    while True:
        try:
            try:
                current_mod_time = os.path.getmtime(CONFIG_FILE)
                if current_mod_time > last_mod_time:
                    log.info("Änderung in 'config.yaml' erkannt. Starte die Logik neu...")
                    return True
            except OSError:
                pass

            now = datetime.now().astimezone()
            for routine in routines:
                routine.run(now)
            
            if time.time() - last_status_write > status_interval:
                write_status(routines)
                last_status_write = time.time()

            time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            return False
        except Exception as e:
            log.error(f"Ein kritischer Fehler in der Hauptschleife ist aufgetreten: {e}", exc_info=True)
            time.sleep(5)

def start_server(log):
    global server_process
    log.info("Starte den Webserver...")
    server_process = subprocess.Popen([sys.executable, SERVER_SCRIPT])

def cleanup():
    print("\nRäume auf und beende Prozesse...")
    if server_process and server_process.poll() is None:
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
    
    if data_logger_thread and data_logger_thread.is_alive():
        stop_event.set()
        data_logger_thread.join()

    if os.path.exists(STATUS_FILE):
        try:
            os.remove(STATUS_FILE)
            print(f"Status-Datei '{STATUS_FILE}' wurde entfernt.")
        except OSError as e:
            print(f"Fehler beim Löschen der Status-Datei: {e}")
    print("Programm beendet.")

if __name__ == "__main__":
    config = load_config(Logger(LOG_FILE, level=logging.INFO))
    log_level_str = config.get('global_settings', {}).get('log_level', 'INFO').upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    log = Logger(LOG_FILE, level=log_level)
    init_database(log)
    start_server(log)
    
    atexit.register(cleanup)
    
    try:
        while run_logic(log):
            log.info("Warte 2 Sekunden, bevor die Konfiguration neu geladen wird...")
            config = load_config(log)
            log_level_str = config.get('global_settings', {}).get('log_level', 'INFO').upper()
            log.logger.setLevel(getattr(logging, log_level_str, logging.INFO))
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        pass
    except Exception as e:
        log.error(f"Ein unerwarteter Fehler hat das Hauptprogramm beendet: {e}", exc_info=True)

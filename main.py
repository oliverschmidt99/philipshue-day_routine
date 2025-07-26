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
from datetime import datetime, date
from phue import Bridge, PhueRequestTimeout
from astral.sun import sun
from astral import LocationInfo
from requests.exceptions import ConnectionError

# Angepasste Importe für die neue Struktur
from src.scene import Scene
from src.room import Room
from src.sensor import Sensor
from src.routine import Routine
from src.logger import Logger

# Globale Dateipfade
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.yaml")
CONFIG_LOCK_FILE = os.path.join(BASE_DIR, "config.yaml.lock")
STATUS_FILE = os.path.join(BASE_DIR, "status.json")
LOG_FILE = os.path.join(BASE_DIR, "info.log")
DB_FILE = os.path.join(BASE_DIR, "sensor_data.db")
SERVER_SCRIPT = os.path.join(BASE_DIR, "web", "server.py")


# Hält den Prozess für den Webserver
server_process = None
data_logger_thread = None
stop_event = threading.Event()


def manage_config_file(log):
    """
    Stellt sicher, dass eine config.yaml existiert. Wenn nicht, wird eine
    minimale Standardkonfiguration erstellt, damit der Webserver starten kann.
    """
    if os.path.exists(CONFIG_FILE):
        log.info("config.yaml gefunden.")
        return

    log.warning(
        "Keine config.yaml gefunden. Erstelle eine neue Datei mit Standardwerten."
    )
    try:
        default_config = {
            "bridge_ip": "",
            "app_key": "",
            "location": {},
            "global_settings": {},
            "rooms": [],
            "routines": [],
            "scenes": {},
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, allow_unicode=True, sort_keys=False)
        log.info(
            "Leere config.yaml wurde erstellt. Die Konfiguration erfolgt über die Web-UI."
        )
    except Exception as e:
        log.error(f"Kritischer Fehler: Konnte keine neue config.yaml erstellen: {e}")
        sys.exit(1)


def init_database(log):
    """Initialisiert die SQLite-Datenbank und erstellt die Tabelle, falls sie nicht existiert."""
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS measurements (
                timestamp TEXT NOT NULL,
                sensor_id INTEGER NOT NULL,
                measurement_type TEXT NOT NULL,
                value REAL NOT NULL,
                PRIMARY KEY (timestamp, sensor_id, measurement_type)
            )
        """
        )
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
            # **ÄNDERUNG: Intervall auf 1 Minute gesetzt**
            seconds_until_next_log = 60 - (now.second % 60)
            log.debug(
                f"Datenlogger: Warte {seconds_until_next_log:.0f} Sekunden bis zur nächsten Messung."
            )

            stopped = stop_event.wait(seconds_until_next_log)
            if stopped:
                break

            con = sqlite3.connect(DB_FILE)
            cur = con.cursor()
            timestamp = datetime.now().isoformat()

            for sensor in sensors:
                brightness = sensor.get_brightness()
                temperature = sensor.get_temperature()

                if brightness is None or temperature is None:
                    log.warning(
                        f"Konnte keine gültigen Daten von Sensor {sensor.motion_sensor_id} abrufen (Netzwerkproblem?), überspringe DB-Eintrag."
                    )
                    continue

                log.debug(
                    f"Datenlogger: Sensor {sensor.motion_sensor_id} -> Helligkeit={brightness}, Temp={temperature}"
                )

                cur.execute(
                    "INSERT OR IGNORE INTO measurements VALUES (?, ?, ?, ?)",
                    (timestamp, sensor.light_sensor_id, "brightness", brightness),
                )

                cur.execute(
                    "INSERT OR IGNORE INTO measurements VALUES (?, ?, ?, ?)",
                    (timestamp, sensor.temp_sensor_id, "temperature", temperature),
                )

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
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if config is None:
                log.warning(
                    f"Konfigurationsdatei '{CONFIG_FILE}' ist leer oder ungültig. Wird als leeres Dict behandelt."
                )
                return {}
            return config
    except FileNotFoundError:
        log.error(
            f"Fehler: Die Konfigurationsdatei '{CONFIG_FILE}' wurde nicht gefunden."
        )
        return None
    except Exception as e:
        log.error(f"Fehler beim Laden der Konfiguration: {e}")
        return None


def connect_bridge(ip, app_key, log):
    """Stellt die Verbindung zur Hue Bridge her."""
    log.info(f"Versuche, eine Verbindung zur Bridge unter {ip} herzustellen...")
    try:
        b = Bridge(ip, username=app_key)
        b.get_api()
        log.info("Verbindung zur Hue Bridge erfolgreich hergestellt.")
        return b
    except (PhueRequestTimeout, ConnectionError) as e:
        log.error(
            f"Konnte keine Verbindung zur Bridge herstellen (Netzwerkfehler): {e}"
        )
        return None
    except Exception as e:
        log.error(
            f"Ein unerwarteter Fehler ist beim Verbinden mit der Bridge aufgetreten: {e}",
            exc_info=True,
        )
        return None


def get_sun_times(location_config, log):
    """Berechnet die Sonnenauf- und -untergangszeiten."""
    if (
        not location_config
        or "latitude" not in location_config
        or "longitude" not in location_config
    ):
        log.warning(
            "Keine vollständigen Standort-Informationen in config.yaml gefunden."
        )
        return None
    try:
        loc = LocationInfo(
            "Home",
            "Germany",
            "Europe/Berlin",
            location_config["latitude"],
            location_config["longitude"],
        )
        s = sun(loc.observer, date=date.today(), tzinfo=loc.timezone)
        log.info(
            f"Sonnenzeiten: Aufgang={s['sunrise']:%H:%M}, Untergang={s['sunset']:%H:%M}"
        )
        return {"sunrise": s["sunrise"], "sunset": s["sunset"]}
    except Exception as e:
        log.error(f"Fehler bei der Berechnung der Sonnenzeiten: {e}", exc_info=True)
        return None


def write_status(routines, sun_times):
    """Schreibt den aktuellen Status aller Routinen und die Sonnenzeiten in eine Datei."""
    status_data = {
        "routines": [r.get_status() for r in routines],
        "sun_times": sun_times,
    }
    try:
        if status_data["sun_times"]:
            serializable_sun_times = status_data["sun_times"].copy()
            serializable_sun_times["sunrise"] = serializable_sun_times[
                "sunrise"
            ].isoformat()
            serializable_sun_times["sunset"] = serializable_sun_times[
                "sunset"
            ].isoformat()
            status_data["sun_times"] = serializable_sun_times

        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status_data, f, indent=2)
    except Exception as e:
        print(f"Fehler beim Schreiben der Status-Datei: {e}")


def run_logic(log):
    """Die Hauptschleife, die die Routinen ausführt. Gibt True zurück, wenn sie neu gestartet werden soll."""
    global data_logger_thread
    log.info("Lade Konfiguration und starte Hue-Logik...")
    config = load_config(log)
    if config is None:
        log.error("Laden der Konfiguration fehlgeschlagen. Breche ab.")
        return False

    bridge_ip = config.get("bridge_ip")
    app_key = config.get("app_key")
    bridge = None

    if not bridge_ip or not app_key:
        log.warning(
            "Keine 'bridge_ip' oder 'app_key' in der Konfiguration gefunden. Die Lichtsteuerung ist pausiert."
        )
    else:
        bridge = connect_bridge(bridge_ip, app_key, log)
        if not bridge:
            log.warning(
                "Verbindung zur Bridge fehlgeschlagen. Versuche es in 30 Sekunden erneut..."
            )
            time.sleep(30)
            return True

    try:
        global_settings = config.get("global_settings", {})
        loop_interval = global_settings.get("loop_interval_s", 1)
        status_interval = global_settings.get("status_interval_s", 5)
        datalogger_interval = global_settings.get("datalogger_interval_minutes", 1)
        last_mod_time = os.path.getmtime(CONFIG_FILE)
        sun_times = get_sun_times(config.get("location"), log)

        scenes = {
            name: Scene(**params) for name, params in config.get("scenes", {}).items()
        }
        routines = []

        if bridge:
            all_sensors_data = bridge.get_sensor()
            all_motion_sensor_ids = [
                int(sid)
                for sid, data in all_sensors_data.items()
                if data.get("type") == "ZLLPresence"
            ]
            all_sensor_objects_for_logger = [
                Sensor(bridge, sensor_id, log) for sensor_id in all_motion_sensor_ids
            ]

            unique_sensor_ids_in_routines = {
                room.get("sensor_id")
                for room in config.get("rooms", [])
                if room.get("sensor_id")
            }
            sensors_for_routines = {
                sensor_id: Sensor(bridge, sensor_id, log)
                for sensor_id in unique_sensor_ids_in_routines
            }

            room_to_sensor_map = {
                room_conf["name"]: sensors_for_routines.get(room_conf.get("sensor_id"))
                for room_conf in config.get("rooms", [])
            }

            rooms = {
                room_conf["name"]: Room(bridge, log, **room_conf)
                for room_conf in config.get("rooms", [])
            }

            routines = [
                Routine(
                    name=r_conf["name"],
                    room=rooms.get(r_conf["room_name"]),
                    sensor=room_to_sensor_map.get(r_conf["room_name"]),
                    routine_config=r_conf,
                    scenes=scenes,
                    sun_times=sun_times,
                    log=log,
                    global_settings=global_settings,
                )
                for r_conf in config.get("routines", [])
                if rooms.get(r_conf["room_name"])
            ]

            log.info(f"{len(routines)} Routine(n) erfolgreich geladen.")

            if all_sensor_objects_for_logger and (
                data_logger_thread is None or not data_logger_thread.is_alive()
            ):
                stop_event.clear()
                data_logger_thread = threading.Thread(
                    target=data_logger_worker,
                    args=(all_sensor_objects_for_logger, datalogger_interval, log),
                )
                data_logger_thread.daemon = True
                data_logger_thread.start()
        else:
            log.info(
                "Keine Bridge-Verbindung, Routinen und Datenlogger werden nicht initialisiert."
            )

        log.info("Initialisierung abgeschlossen. Starte Hauptschleife.")
        last_status_write = time.time()

        while True:
            current_mod_time = os.path.getmtime(CONFIG_FILE)
            if current_mod_time > last_mod_time:
                log.info(
                    "Änderung in 'config.yaml' erkannt. Warte auf Freigabe (Lock-Datei)..."
                )

                lock_wait_start = time.time()
                while os.path.exists(CONFIG_LOCK_FILE):
                    time.sleep(0.1)
                    if time.time() - lock_wait_start > 10:
                        log.error(
                            "Lock-Datei wurde nach 10s nicht entfernt. Breche Neustart ab."
                        )
                        last_mod_time = current_mod_time
                        break
                else:
                    log.info("Konfiguration freigegeben. Starte die Logik neu...")
                    return True

            if bridge:
                now = datetime.now().astimezone()
                for routine in routines:
                    routine.run(now)

            if time.time() - last_status_write > status_interval:
                write_status(routines, sun_times)
                last_status_write = time.time()

            time.sleep(loop_interval)

    except (PhueRequestTimeout, ConnectionError, OSError) as e:
        log.error(f"Netzwerkverbindung zur Bridge verloren: {e}. Starte Logik neu...")
        time.sleep(10)
        return True
    except (KeyboardInterrupt, SystemExit):
        return False
    except Exception as e:
        log.error(
            f"Ein kritischer Fehler in der Hauptschleife ist aufgetreten: {e}",
            exc_info=True,
        )
        time.sleep(5)
        return True


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
    log = Logger(LOG_FILE, level=logging.INFO)

    manage_config_file(log)
    init_database(log)

    atexit.register(cleanup)
    start_server(log)

    while True:
        if not run_logic(log):
            break

        log.info("Warte 5 Sekunden, bevor die Logik neu gestartet wird...")
        time.sleep(5)

        config = load_config(log)
        if config:
            new_log_level_str = (
                config.get("global_settings", {}).get("log_level", "INFO").upper()
            )
            log.logger.setLevel(getattr(logging, new_log_level_str, logging.INFO))
            log.info(f"Log-Level wurde auf {new_log_level_str} gesetzt.")

    log.info("Hauptprogramm wird beendet.")

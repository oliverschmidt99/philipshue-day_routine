"""
Kapselt die gesamte Kernlogik der Hue-Steuerung, inklusive der Hauptschleife.
"""

import os
import json
import time
import sqlite3
import threading
from datetime import datetime, date

from phue import Bridge, PhueRequestTimeout
from requests.exceptions import ConnectionError as RequestsConnectionError
from astral import LocationInfo
from astral.sun import sun

from src.scene import Scene
from src.room import Room
from src.sensor import Sensor
from src.routine import Routine
from src.logger import Logger
from src.config_manager import ConfigManager

# --- Globale Pfade ---
BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(BASE_DIR, "sensor_data.db")
STATUS_FILE = os.path.join(DATA_DIR, "status.json")


class CoreLogic:
    """Führt die Hauptschleife aus, verbindet sich mit der Bridge und steuert die Routinen."""

    def __init__(self, log: Logger, config_manager: ConfigManager):
        self.log = log
        self.config_manager = config_manager
        self.data_logger_thread = None
        self.stop_event = threading.Event()
        self._init_database()

    def _init_database(self):
        """Stellt sicher, dass die Datenbank und die Tabelle existieren."""
        try:
            with sqlite3.connect(DB_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS measurements (
                        timestamp TEXT NOT NULL, sensor_id INTEGER NOT NULL,
                        measurement_type TEXT NOT NULL, value REAL NOT NULL,
                        PRIMARY KEY (timestamp, sensor_id, measurement_type)
                    )
                    """
                )
            self.log.info("Datenbank initialisiert.")
        except sqlite3.Error as e:
            self.log.error(f"Datenbankfehler bei Initialisierung: {e}", exc_info=True)

    def run_main_loop(self):
        """
        Die Endlosschleife, die die Logik am Laufen hält und bei
        Fehlern oder Konfigurationsänderungen neu startet.
        """
        while not self.stop_event.is_set():
            config = self.config_manager.get_full_config()
            if not config or not config.get("bridge_ip"):
                self.log.warning(
                    "Konfiguration unvollständig oder Bridge nicht eingerichtet. Warte 15s."
                )
                time.sleep(15)
                continue

            bridge = self._connect_to_bridge(config)
            if not bridge:
                time.sleep(30)
                continue

            # Diese Methode läuft, bis die Konfiguration geändert wird oder ein Fehler auftritt
            self._execute_routine_session(bridge)

    def _connect_to_bridge(self, config: dict) -> Bridge | None:
        """Versucht, eine Verbindung zur Hue Bridge herzustellen."""
        bridge_ip = config.get("bridge_ip")
        app_key = config.get("app_key")
        if not bridge_ip or not app_key:
            self.log.warning(
                "Bridge-IP oder App-Key fehlen in config.yaml. Steuerung pausiert."
            )
            return None
        try:
            bridge = Bridge(bridge_ip, username=app_key)
            bridge.get_api()  # Testet die Verbindung
            self.log.info(f"Erfolgreich mit Bridge unter {bridge_ip} verbunden.")
            return bridge
        except (RequestsConnectionError, PhueRequestTimeout, OSError) as e:
            self.log.error(f"Netzwerkfehler zur Bridge: {e}.")
            return None

    def _execute_routine_session(self, bridge: Bridge):
        """
        Initialisiert und führt alle Routinen aus, bis eine Änderung der
        Konfigurationsdatei erkannt wird.
        """
        config = self.config_manager.get_full_config()
        global_settings = config.get("global_settings", {})
        sun_times = self._get_sun_times(config.get("location"))
        scenes = {
            name: Scene(**params) for name, params in config.get("scenes", {}).items()
        }

        rooms = {
            rc["name"]: Room(bridge, self.log, **rc) for rc in config.get("rooms", [])
        }

        sensors = {}
        for room_config in config.get("rooms", []):
            if sensor_id := room_config.get("sensor_id"):
                if sensor_id not in sensors:
                    sensors[sensor_id] = Sensor(bridge, sensor_id, self.log)

        routines = [
            Routine(
                r_conf["name"],
                rooms.get(r_conf["room_name"]),
                sensors.get(
                    next(
                        (
                            r.get("sensor_id")
                            for r in config.get("rooms", [])
                            if r.get("name") == r_conf["room_name"]
                        ),
                        None,
                    )
                ),
                r_conf,
                scenes,
                sun_times,
                self.log,
                global_settings,
            )
            for r_conf in config.get("routines", [])
            if rooms.get(r_conf["room_name"])
        ]

        last_mod_time = self.config_manager.get_last_modified_time()
        last_status_write = 0

        self.log.info(f"{len(routines)} Routinen werden jetzt ausgeführt...")
        while not self.stop_event.is_set():
            try:
                if self.config_manager.get_last_modified_time() > last_mod_time:
                    self.log.info("Änderung in config.yaml erkannt. Lade Logik neu.")
                    return

                now = datetime.now().astimezone()
                for routine in routines:
                    routine.run(now)

                if time.time() - last_status_write > global_settings.get(
                    "status_interval_s", 5
                ):
                    self._write_status(routines, sun_times)
                    last_status_write = time.time()

                time.sleep(global_settings.get("loop_interval_s", 1))

            except (RequestsConnectionError, PhueRequestTimeout, OSError) as e:
                self.log.error(
                    f"Verbindung zur Bridge verloren: {e}. Starte Logik neu..."
                )
                return
            except (TypeError, KeyError) as e:
                self.log.error(
                    f"Konfigurationsfehler: {e}. Bitte config.yaml prüfen.",
                    exc_info=True,
                )
                time.sleep(15)
                return

    def _get_sun_times(self, location_config):
        """Berechnet Sonnenauf- und -untergang."""
        if not (
            location_config
            and location_config.get("latitude")
            and location_config.get("longitude")
        ):
            return None
        try:
            loc = LocationInfo(
                "Home",
                "Germany",
                "Europe/Berlin",
                float(location_config["latitude"]),
                float(location_config["longitude"]),
            )
            sun_info = sun(loc.observer, date=date.today(), tzinfo=loc.timezone)
            return {"sunrise": sun_info["sunrise"], "sunset": sun_info["sunset"]}
        except (ValueError, TypeError) as e:
            self.log.error(f"Fehler bei der Berechnung der Sonnenzeiten: {e}")
            return None

    def _write_status(self, routines, sun_times):
        """Schreibt den aktuellen Status in die status.json."""
        status_data = {
            "routines": [r.get_status() for r in routines],
            "sun_times": sun_times,
        }
        try:
            if status_data.get("sun_times"):
                status_data["sun_times"] = {
                    "sunrise": status_data["sun_times"]["sunrise"].isoformat(),
                    "sunset": status_data["sun_times"]["sunset"].isoformat(),
                }
            with open(STATUS_FILE + ".tmp", "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2)
            os.replace(STATUS_FILE + ".tmp", STATUS_FILE)
        except (IOError, TypeError) as e:
            self.log.error(f"Fehler beim Schreiben der Status-Datei: {e}")

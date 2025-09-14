"""
Kapselt die gesamte Kernlogik der Hue-Steuerung, inklusive der Hauptschleife.
"""
import os
import json
import time
import sqlite3
from datetime import datetime, date
from astral import LocationInfo
from astral.sun import sun

from src.hue_wrapper import HueBridge
from src.scene import Scene
from src.room import Room
from src.sensor import Sensor
from src.routine import Routine
from src.logger import Logger
from src.config_manager import ConfigManager

BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(BASE_DIR, "sensor_data.db")
STATUS_FILE = os.path.join(DATA_DIR, "status.json")

class CoreLogic:
    def __init__(self, log: Logger, config_manager: ConfigManager):
        self.log = log
        self.config_manager = config_manager
        self._init_database()

    def _init_database(self):
        try:
            with sqlite3.connect(DB_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS measurements (
                        timestamp TEXT NOT NULL, sensor_id TEXT NOT NULL,
                        measurement_type TEXT NOT NULL, value REAL NOT NULL,
                        PRIMARY KEY (timestamp, sensor_id, measurement_type)
                    )
                    """
                )
            self.log.info("Datenbank initialisiert.")
        except sqlite3.Error as e:
            self.log.error(f"Datenbankfehler bei Initialisierung: {e}", exc_info=True)

    def run_main_loop(self):
        while True:
            config = self.config_manager.get_full_config()
            if not config or not config.get("bridge_ip"):
                self.log.warning("Konfiguration unvollständig. Warte 15s.")
                time.sleep(15)
                continue

            bridge = self._connect_to_bridge(config)
            if not bridge:
                time.sleep(30)
                continue

            self._execute_routine_session(bridge)

    def _connect_to_bridge(self, config: dict) -> HueBridge | None:
        bridge_ip = config.get("bridge_ip")
        app_key = config.get("app_key")
        if not bridge_ip or not app_key:
            return None
        
        bridge = HueBridge(ip=bridge_ip, app_key=app_key, logger=self.log)
        if bridge.is_connected():
            return bridge
        else:
            self.log.error("Netzwerkfehler zur Bridge: Verbindung konnte nicht hergestellt werden.")
            return None

    def _execute_routine_session(self, bridge: HueBridge):
        config = self.config_manager.get_full_config()
        global_settings = config.get("global_settings", {})
        sun_times = self._get_sun_times(config.get("location"))
        scenes = {name: Scene(**params) for name, params in config.get("scenes", {}).items()}
        
        bridge_data = bridge.get_api_data()
        all_rooms_and_zones = bridge_data.get("rooms", []) + bridge_data.get("zones", [])

        rooms = {}
        for room_conf in config.get("rooms", []):
            bridge_group = next((g for g in all_rooms_and_zones if g['metadata']['name'] == room_conf["name"]), None)
            if bridge_group:
                rooms[room_conf["name"]] = Room(bridge, self.log, name=room_conf["name"], group_id=bridge_group["id"])

        sensors = {}
        for room_conf in config.get("rooms", []):
            if room_conf.get("sensor_id"):
                sensors[room_conf["sensor_id"]] = Sensor(bridge, room_conf["sensor_id"], self.log)

        routines = [
            Routine(r_conf["name"], rooms.get(r_conf["room_name"]), sensors.get(next((r.get("sensor_id") for r in config.get("rooms", []) if r.get("name") == r_conf["room_name"]), None)), r_conf, scenes, sun_times, self.log, global_settings) 
            for r_conf in config.get("routines", []) if rooms.get(r_conf["room_name"])
        ]

        last_mod_time = self.config_manager.get_last_modified_time()
        last_status_write = 0

        self.log.info(f"{len(routines)} Routinen werden jetzt ausgeführt...")
        while True:
            try:
                if self.config_manager.get_last_modified_time() > last_mod_time:
                    self.log.info("Änderung in config.yaml erkannt. Lade Logik neu.")
                    return

                now = datetime.now().astimezone()
                for routine in routines:
                    routine.run(now)

                if time.time() - last_status_write > global_settings.get("status_interval_s", 5):
                    self._write_status(routines, sun_times)
                    last_status_write = time.time()

                time.sleep(global_settings.get("loop_interval_s", 1))

            except Exception as e:
                self.log.error(f"Unerwarteter Fehler in der Hauptschleife: {e}. Starte Logik neu...", exc_info=True)
                time.sleep(5)
                return

    def _get_sun_times(self, location_config):
        if not (location_config and location_config.get("latitude") and location_config.get("longitude")):
            return None
        try:
            loc = LocationInfo("Home", "Germany", "Europe/Berlin", float(location_config["latitude"]), float(location_config["longitude"]))
            sun_info = sun(loc.observer, date=date.today(), tzinfo=loc.timezone)
            return {"sunrise": sun_info["sunrise"], "sunset": sun_info["sunset"]}
        except (ValueError, TypeError) as e:
            self.log.error(f"Fehler bei der Berechnung der Sonnenzeiten: {e}")
            return None

    def _write_status(self, routines, sun_times):
        status_data = {"routines": [r.get_status() for r in routines], "sun_times": sun_times}
        try:
            if status_data.get("sun_times"):
                status_data["sun_times"] = {"sunrise": status_data["sun_times"]["sunrise"].isoformat(), "sunset": status_data["sun_times"]["sunset"].isoformat()}
            with open(STATUS_FILE + ".tmp", "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2)
            os.replace(STATUS_FILE + ".tmp", STATUS_FILE)
        except (IOError, TypeError) as e:
            self.log.error(f"Fehler beim Schreiben der Status-Datei: {e}")
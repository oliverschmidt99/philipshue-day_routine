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
from src.timer import Timer
from src.state_machine import StateMachine
from src.logger import AppLogger
from src.config_manager import ConfigManager

BASE_DIR = os.path.dirname(os.path.abspath(os.path.join(__file__, "..")))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_FILE = os.path.join(BASE_DIR, "sensor_data.db")
STATUS_FILE = os.path.join(DATA_DIR, "status.json")

class CoreLogic:
    def __init__(self, log: AppLogger, config_manager: ConfigManager):
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

            self._execute_automation_session(bridge)

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

    def _execute_automation_session(self, bridge: HueBridge):
        config = self.config_manager.get_full_config()
        global_settings = config.get("global_settings", {})
        sun_times = self._get_sun_times(config.get("location"))
        scenes = {name: Scene(**params) for name, params in config.get("scenes", {}).items()}
        
        bridge_data = bridge.get_full_api_data()
        
        all_rooms_and_zones = bridge_data.get("rooms", []) + bridge_data.get("zones", [])

        rooms = {}
        for group in all_rooms_and_zones:
            if 'metadata' in group and 'name' in group['metadata']:
                rooms[group['metadata']['name']] = Room(bridge, self.log, name=group['metadata']['name'], group_id=group["id"])

        sensors = {s['id']: Sensor(bridge, s['id'], self.log) for s in bridge_data.get("devices", []) if s.get('product_data', {}).get('product_name') == 'Hue motion sensor'}
        
        automations = []
        automation_configs = config.get("automations", [])

        for aut_conf in automation_configs:
            aut_type = aut_conf.get("type", "routine")
            name = aut_conf.get("name")
            room_name = aut_conf.get("room_name") if aut_type == "routine" else aut_conf.get("target_room")
            room = rooms.get(room_name)
            
            sensor = None
            if 'sensor_id' in aut_conf and aut_conf['sensor_id']:
                sensor = sensors.get(aut_conf['sensor_id'])
            
            common_args = {
                "name": name, "config": aut_conf, "log": self.log,
                "bridge": bridge, "scenes": scenes, "rooms": rooms,
                "sensors": sensors, "sun_times": sun_times,
                "global_settings": global_settings
            }

            if aut_type == "routine":
                if room:
                    automations.append(Routine(room=room, sensor=sensor, **common_args))
            elif aut_type == "timer":
                 automations.append(Timer(**common_args))
            elif aut_type == "state_machine":
                 automations.append(StateMachine(**common_args))

        last_mod_time = self.config_manager.get_last_modified_time()
        last_status_write = 0

        self.log.info(f"{len(automations)} Automationen werden jetzt ausgeführt...")
        while True:
            try:
                if self.config_manager.get_last_modified_time() > last_mod_time:
                    self.log.info("Änderung in der Konfiguration erkannt. Lade Logik neu.")
                    return

                now = datetime.now().astimezone()
                for automation in automations:
                    automation.run(now)

                if time.time() - last_status_write > global_settings.get("status_interval_s", 5):
                    self._write_status(automations, sun_times)
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

    def _write_status(self, automations, sun_times):
        status_data = {"automations": [aut.get_status() for aut in automations], "sun_times": {}}
        if sun_times:
            status_data["sun_times"] = {"sunrise": sun_times["sunrise"].isoformat(), "sunset": sun_times["sunset"].isoformat()}
        try:
            with open(STATUS_FILE + ".tmp", "w", encoding="utf-8") as f:
                json.dump(status_data, f, indent=2)
            os.replace(STATUS_FILE + ".tmp", STATUS_FILE)
        except (IOError, TypeError) as e:
            self.log.error(f"Fehler beim Schreiben der Status-Datei: {e}")
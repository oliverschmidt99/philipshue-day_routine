import yaml
from phue import Bridge
from astral import LocationInfo
from astral.sun import sun
from datetime import date

# Relative Imports, da wir uns innerhalb des 'core'-Pakets befinden
from .logger import Logger
from .scene import Scene
from .room import Room
from .sensor import Sensor
from .routine import Routine

class Configuration:
    """
    Eine zentrale Klasse zur Verwaltung der Konfiguration, der Bridge-Verbindung
    und zur Initialisierung der Kernkomponenten der Anwendung.
    """
    def __init__(self, config_file='config.yaml', log: Logger = None):
        self.log = log or Logger("config_loader.log")
        self.config_file = config_file
        self.config = self._load_config()
        self.bridge = self._connect_bridge()
        self.sun_times = self._get_sun_times()

    def _load_config(self):
        """Lädt die Konfiguration aus der angegebenen YAML-Datei."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.log.info(f"Lade Konfiguration aus '{self.config_file}'.")
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.log.error(f"Konfigurationsdatei '{self.config_file}' nicht gefunden.")
            return None
        except Exception as e:
            self.log.error(f"Fehler beim Laden der Konfiguration: {e}", exc_info=True)
            return None

    def _connect_bridge(self):
        """Stellt die Verbindung zur Philips Hue Bridge her."""
        ip = self.config.get('settings', {}).get('bridge_ip')
        if not ip:
            self.log.error("Bridge-IP nicht in der Konfiguration gefunden.")
            return None
        
        self.log.info(f"Versuche Verbindung zur Bridge unter {ip}...")
        try:
            b = Bridge(ip)
            b.connect()
            self.log.info("Verbindung zur Hue Bridge erfolgreich hergestellt.")
            return b
        except Exception as e:
            self.log.error(f"Verbindung zur Bridge fehlgeschlagen: {e}", exc_info=True)
            return None

    def _get_sun_times(self):
        """Berechnet die Zeiten für Sonnenauf- und -untergang."""
        location_config = self.config.get('location')
        if not location_config:
            self.log.warning("Keine Standort-Infos gefunden. Sonnenzeiten werden nicht berechnet.")
            return None
        try:
            loc = LocationInfo("Home", "Germany", "Europe/Berlin", 
                             location_config['latitude'], location_config['longitude'])
            s = sun(loc.observer, date=date.today(), tzinfo=loc.timezone)
            self.log.info(f"Sonnenzeiten: Aufgang={s['sunrise']:%H:%M}, Untergang={s['sunset']:%H:%M}")
            return {"sunrise": s['sunrise'], "sunset": s['sunset']}
        except Exception as e:
            self.log.error(f"Fehler bei der Berechnung der Sonnenzeiten: {e}", exc_info=True)
            return None

    def initialize_routines(self):
        """Initialisiert und gibt eine Liste aller konfigurierten Routinen zurück."""
        if not self.config or not self.bridge:
            self.log.error("Initialisierung der Routinen nicht möglich, da Config oder Bridge fehlen.")
            return []

        scenes = {name: Scene(**params) for name, params in self.config.get('scenes', {}).items()}
        rooms = {conf['name']: Room(self.bridge, self.log, **conf) for conf in self.config.get('rooms', [])}
        sensors = {
            room_conf['name']: Sensor(self.bridge, room_conf['sensor_id'], self.log)
            for room_conf in self.config.get('rooms', []) if 'sensor_id' in room_conf
        }

        routines = []
        for conf in self.config.get('routines', []):
            room_name = conf.get('room_name')
            room = rooms.get(room_name)
            sensor = sensors.get(room_name)

            if not room:
                self.log.error(f"Raum '{room_name}' für Routine '{conf['name']}' nicht gefunden. Überspringe.")
                continue

            routines.append(Routine(
                name=conf['name'], room=room, sensor=sensor,
                routine_config=conf, scenes=scenes, sun_times=self.sun_times, log=self.log
            ))
            self.log.info(f"Routine '{conf['name']}' für Raum '{room_name}' geladen.")
        
        return routines

    def save_config(self, new_config_data):
        """Speichert die übergebenen Konfigurationsdaten in die YAML-Datei."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(new_config_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            self.log.info(f"Konfiguration wurde in '{self.config_file}' gespeichert.")
            self.config = new_config_data
            return True
        except Exception as e:
            self.log.error(f"Fehler beim Speichern der Konfiguration: {e}", exc_info=True)
            return False

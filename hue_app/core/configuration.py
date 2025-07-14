import yaml
from .huebridge import HueBridge
from .room import Room
from .scene import Scene
from .routine import Routine
from .logger import setup_logger

class Configuration:
    """
    Verwaltet das Laden, Speichern und den Zugriff auf die Konfiguration der App.
    """
    def __init__(self, config_file):
        self.config_file = config_file
        log_level = self._get_initial_log_level()
        self.logger = setup_logger('HueFlowLogger', log_level)
        
        self.data = self._load_config()

        if not self.data:
            self.bridge = None
            self.rooms = []
            self.scenes = []
            self.routines = []
            self.logger.warning("Initialisierung mit leeren Werten, da keine Konfiguration gefunden wurde.")
        else:
            self.bridge = self._connect_bridge()
            self.rooms = self._load_rooms()
            self.scenes = self._load_scenes()
            self.routines = self._load_routines()

    def _get_initial_log_level(self):
        """Liest nur das Log-Level aus der YAML, bevor der volle Logger initialisiert wird."""
        try:
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f)
                return config_data.get('general', {}).get('log_level', 'INFO')
        except (FileNotFoundError, yaml.YAMLError):
            return 'INFO'

    def _load_config(self):
        """Lädt die Konfiguration aus der YAML-Datei."""
        try:
            with open(self.config_file, 'r') as f:
                config_data = yaml.safe_load(f)
                return config_data if isinstance(config_data, dict) else self._create_default_config()
        except FileNotFoundError:
            return self._create_default_config()
        except yaml.YAMLError as e:
            self.logger.error(f"Fehler beim Parsen der Konfigurationsdatei: {e}")
            return self._create_default_config()

    def _create_default_config(self):
        """Erstellt eine leere, aber gültige Konfigurationsstruktur."""
        self.logger.warning(f"Konfigurationsdatei nicht gefunden oder fehlerhaft. Erstelle eine leere Konfiguration.")
        return {
            'general': {'language': 'de', 'log_level': 'INFO'},
            'hue_bridge': {'ip_address': None, 'api_key': None, 'refresh_rate': 5},
            'routines': [],
            'scenes': []
        }

    def get_config(self):
        """Gibt die gesamte Konfiguration als Dictionary zurück."""
        return self.data

    def save_config(self, config_data):
        """Speichert die übergebenen Konfigurationsdaten in der YAML-Datei."""
        self.data = config_data
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)
            self.logger.info(f"Konfiguration erfolgreich in '{self.config_file}' gespeichert.")
            new_log_level = self.data.get('general', {}).get('log_level', 'INFO')
            self.logger.setLevel(new_log_level.upper())
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Konfiguration: {e}")

    def _connect_bridge(self):
        """Stellt die Verbindung zur Hue Bridge her."""
        if not self.data:
            return None
        
        bridge_config = self.data.get('hue_bridge', {})
        ip = bridge_config.get('ip_address')
        # Der 'username' in phue entspricht dem 'api_key'
        api_key = bridge_config.get('api_key')

        if not ip:
            self.logger.error("Bridge-IP wurde nicht in der Konfiguration gefunden.")
            return None
        
        return HueBridge(ip, username=api_key)

    def _load_rooms(self):
        """Lädt die Raum-Objekte von der Bridge."""
        if not self.bridge or not self.bridge.is_configured():
            return []
        # Gibt die Liste der phue Group-Objekte zurück
        return self.bridge.get_groups() or []

    def get_rooms_for_api(self):
        """
        NEU: Konvertiert die Raum-Objekte in eine einfache Liste von Dictionaries
        für die JSON-API, damit das Frontend sie verarbeiten kann.
        """
        if not self.rooms:
            return []
        
        room_list = []
        for room in self.rooms:
            # Erstellt ein einfaches Dictionary für jeden Raum
            room_list.append({'id': room.group_id, 'name': room.name})
        return room_list

    def _load_scenes(self):
        """Lädt die Szenen-Konfigurationen."""
        return self.data.get('scenes', [])

    def _load_routines(self):
        """Lädt die Routinen-Konfigurationen."""
        return self.data.get('routines', [])

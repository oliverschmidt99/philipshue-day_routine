"""
Ein Wrapper für die python-hue-v2 Bibliothek, um die neue v2 API zu kapseln
und die Umstellung des restlichen Codes zu minimieren.
"""
from typing import Optional, Dict, List, Union
from python_hue_v2.hue import Hue
from python_hue_v2.room import Room as HueRoom
from python_hue_v2.zone import Zone as HueZone

class HueBridge:
    """
    Eine Klasse, die eine Verbindung zur Philips Hue Bridge über die v2 API verwaltet.
    """

    def __init__(self, ip: str = None, app_key: str = None, logger=None):
        self.ip = ip
        self.app_key = app_key
        self.log = logger
        self._hue: Optional[Hue] = None
        self.connect()

    def _log_error(self, message: str, exc_info=False):
        if self.log:
            self.log.error(message, exc_info=exc_info)
        else:
            print(f"ERROR: {message}")

    def connect(self):
        """Stellt die Verbindung zur Bridge her."""
        if not self.ip or not self.app_key:
            return
        try:
            self._hue = Hue(self.ip, self.app_key)
            self._hue.bridge.get_bridge()
            self.log.info(f"Erfolgreich mit Bridge unter {self.ip} (v2 API) verbunden.")
        except Exception as e:
            self._log_error(f"Fehler bei der Initialisierung der v2 Bridge: {e}")
            self._hue = None
    
    @staticmethod
    def create_app_key(ip: str, logger=None) -> Optional[str]:
        """
        Führt den Prozess zum Erstellen eines neuen App-Keys durch.
        Der physische Knopf auf der Bridge muss gedrückt werden.
        """
        try:
            hue = Hue(ip)
            app_key = hue.bridge.connect()
            if logger: logger.info(f"Neuer App-Key für Bridge {ip} erfolgreich erstellt.")
            return app_key
        except Exception as e:
            if logger: logger.error(f"Fehler beim Erstellen des App-Keys: {e}")
            return None

    def is_connected(self) -> bool:
        return self._hue is not None

    def get_api_data(self) -> Dict:
        """Holt alle relevanten Daten von der Bridge als Dictionaries."""
        if not self.is_connected(): return {}
        return {
            "devices": self._hue.bridge.get_devices(),
            "rooms": self._hue.bridge.get_rooms(),
            "zones": self._hue.bridge.get_zones(),
        }

    def get_device_by_id(self, device_id: str) -> Optional[Dict]:
        """Holt die Daten eines einzelnen Geräts als Dictionary."""
        if not self.is_connected(): return None
        try:
            return self._hue.bridge.get_device(device_id)
        except ConnectionError:
            self.log.warning(f"Gerät mit ID {device_id} konnte nicht gefunden werden.")
            return None

    def get_resource(self, resource_type: str, resource_id: str) -> Optional[Dict]:
        """Holt die rohen Daten einer spezifischen Ressource (Service)."""
        if not self.is_connected(): return None
        try:
            # Dies ist die korrekte Methode, die wir im Test verifiziert haben.
            return self._hue.bridge._get_by_id(resource_type, resource_id)
        except Exception as e:
            self._log_error(f"Fehler beim Abrufen der Ressource {resource_type}/{resource_id}: {e}")
            return None
            
    def get_lights(self) -> List[Dict]:
        if not self.is_connected(): return []
        return self._hue.bridge.get_lights()

    def get_scenes(self) -> List[Dict]:
        if not self.is_connected(): return []
        return self._hue.bridge.get_scenes()
        
    def get_grouped_lights(self) -> List[Dict]:
        if not self.is_connected(): return []
        return self._hue.bridge.get_grouped_lights()

    def get_group_object_by_id(self, group_id: str) -> Optional[Union[HueRoom, HueZone]]:
        """Holt das Bibliotheks-Objekt für einen Raum oder eine Zone."""
        if not self.is_connected(): return None
        return next((g for g in self._hue.rooms + self._hue.zones if g.id == group_id), None)

    def set_group_state(self, group_id: str, state: dict):
        """Setzt den Zustand für eine Gruppe (Raum oder Zone)."""
        if not self.is_connected(): return

        try:
            # Finde die grouped_light ID, die zu unserem Raum/Zone gehört
            owner_rid = None
            all_groups = self._hue.bridge.get_rooms() + self._hue.bridge.get_zones()
            group_to_control = next((g for g in all_groups if g['id'] == group_id), None)

            if group_to_control and group_to_control.get('services'):
                grouped_light_service = next((s for s in group_to_control['services'] if s.get('rtype') == 'grouped_light'), None)
                if grouped_light_service:
                    owner_rid = grouped_light_service['rid']

            if not owner_rid:
                 self.log.error(f"Kein grouped_light Service für Gruppe {group_id} gefunden.")
                 return

            self._hue.bridge.set_grouped_light_service(owner_rid, state)

        except Exception as e:
            self._log_error(f"Fehler beim Setzen des Zustands für Gruppe {group_id}: {e}", exc_info=True)

    def set_light_state(self, light_id: str, state: dict):
        """Setzt den Zustand für eine einzelne Lampe."""
        if not self.is_connected(): return
        try:
            # Die ID einer 'light'-Ressource ist die Service-ID, die wir zum Steuern benötigen.
            self._hue.bridge.set_light_service(light_id, state)
        except Exception as e:
            self._log_error(f"Fehler beim Setzen des Zustands für Lampe {light_id}: {e}", exc_info=True)
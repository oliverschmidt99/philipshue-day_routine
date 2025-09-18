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
        if not self.is_connected():
            return None
        try:
            # Korrekte Zuordnung der Ressourcentypen zu den Attributen des Hue-Objekts
            resource_map = {
                "motion": self._hue.motion_sensors,
                "light_level": self._hue.light_level_sensors,
                "temperature": self._hue.temperature_sensors,
                "grouped_light": self._hue.grouped_lights
            }
            
            resource_list = resource_map.get(resource_type)
            
            if resource_list:
                for item in resource_list:
                    if item.id == resource_id:
                        return item.raw  # Gibt die Rohdaten als Dictionary zurück
                self.log.warning(f"Ressource mit ID {resource_id} im Typ '{resource_type}' nicht gefunden.")
                return None
            else:
                self.log.warning(f"Unbekannter Ressourcen-Typ '{resource_type}' angefragt.")
                return None
                
        except Exception as e:
            self._log_error(f"Fehler beim Abrufen der Ressource {resource_type}/{resource_id}: {e}", exc_info=True)
            return None

    def get_group_object_by_id(self, group_id: str) -> Optional[Union[HueRoom, HueZone]]:
        """Holt das Bibliotheks-Objekt für einen Raum oder eine Zone."""
        if not self.is_connected(): return None
        return next((g for g in self._hue.rooms + self._hue.zones if g.id == group_id), None)

    def set_group_state(self, group_id: str, state: dict):
        """Setzt den Zustand für eine Gruppe (Raum oder Zone)."""
        if not self.is_connected(): return

        try:
            target_grouped_light = next((gl for gl in self._hue.grouped_lights if gl.owner.rid == group_id), None)
            
            if not target_grouped_light:
                self._log_error(f"Kein steuerbarer Licht-Service für Gruppe {group_id} gefunden.")
                return

            on = state.get("on")
            brightness = (state.get("bri") / 254) * 100 if "bri" in state and state.get("bri") is not None else None
            mirek = state.get("ct")
            
            target_grouped_light.set_state(on=on, brightness=brightness, mirek=mirek)

        except Exception as e:
            self._log_error(f"Fehler beim Setzen des Zustands für Gruppe {group_id}: {e}", exc_info=True)
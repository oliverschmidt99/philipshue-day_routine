"""
Ein Wrapper für die python-hue-v2 Bibliothek, der die Komplexität der v2 API kapselt
und einen Workaround für fehlende Gruppen-Funktionen (Farbtemperatur) implementiert.
"""
from typing import Optional, Dict, List
from python_hue_v2.hue import Hue
import time

class HueBridge:
    """
    Eine Klasse, die eine Verbindung zur Philips Hue Bridge über die v2 API verwaltet.
    """

    def __init__(self, ip: str = None, app_key: str = None, logger=None):
        self.ip = ip
        self.app_key = app_key
        self.log = logger
        self._hue: Optional[Hue] = None
        self._group_light_mapping: Dict[str, List[str]] = {}
        self._group_name_mapping: Dict[str, str] = {} # NEU: Speichert Gruppennamen
        self._light_capabilities: Dict[str, Dict] = {} # NEU: Speichert Fähigkeiten der Lampen
        self.connect()

    def _log_error(self, message: str, exc_info=False):
        if self.log:
            self.log.error(message, exc_info=exc_info)
        else:
            print(f"ERROR: {message}")

    def connect(self):
        """Stellt die Verbindung zur Bridge her und lädt die Gruppen-Struktur."""
        if not self.ip or not self.app_key:
            return
        try:
            self._hue = Hue(self.ip, self.app_key)
            self._hue.bridge.get_bridge()
            self._cache_device_and_group_info() # Umbenannt für mehr Klarheit
            self.log.info(f"Erfolgreich mit Bridge unter {self.ip} (v2 API) verbunden.")
        except Exception as e:
            self._log_error(f"Fehler bei der Initialisierung der v2 Bridge: {e}")
            self._hue = None
    
    @staticmethod
    def create_app_key(ip: str, logger=None) -> Optional[str]:
        """Führt den Prozess zum Erstellen eines neuen App-Keys durch."""
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

    def _cache_device_and_group_info(self):
        """
        KORRIGIERT & ERWEITERT: Speichert alle relevanten Infos über Geräte,
        Gruppen und deren Beziehungen in einem Rutsch.
        """
        if not self.is_connected(): return
        
        all_lights = self._hue.bridge.get_lights()
        all_devices_by_id = {device['id']: device for device in self._hue.bridge.get_devices()}
        groups = self._hue.bridge.get_rooms() + self._hue.bridge.get_zones()

        # NEU: Fähigkeiten der Lampen speichern (z.B. ob sie Farbtemperatur unterstützen)
        self._light_capabilities = {light['id']: light for light in all_lights}

        # Gruppenzuordnungen und Namen speichern
        self._group_light_mapping = {}
        self._group_name_mapping = {}
        for group in groups:
            group_id = group.get('id')
            if not group_id: continue
            
            self._group_name_mapping[group_id] = group.get('metadata', {}).get('name', 'Unbekannte Gruppe')
            self._group_light_mapping[group_id] = []
            
            for child in group.get('children', []):
                if child.get('rtype') == 'device':
                    device = all_devices_by_id.get(child.get('rid'))
                    if device:
                        for service in device.get('services', []):
                            if service.get('rtype') == 'light':
                                self._group_light_mapping[group_id].append(service['rid'])

    def get_api_data(self) -> Dict:
        """Holt alle relevanten Daten von der Bridge als Dictionaries."""
        if not self.is_connected(): return {}
        self._cache_device_and_group_info() # Immer aktuelle Daten sicherstellen
        return {
            "devices": self._hue.bridge.get_devices(),
            "rooms": self._hue.bridge.get_rooms(),
            "zones": self._hue.bridge.get_zones(),
            "lights": self._hue.bridge.get_lights(),
            "scenes": self._hue.bridge.get_scenes()
        }

    def get_device_by_id(self, device_id: str) -> Optional[Dict]:
        """Holt die Daten eines einzelnen Geräts als Dictionary."""
        if not self.is_connected(): return None
        try:
            return self._hue.bridge.get_device(device_id)
        except Exception:
            return None

    def set_light_state(self, light_id: str, state: dict):
        """Setzt den Zustand einer EINZELNEN Lampe."""
        if not self.is_connected(): return

        api_state = {}
        if "on" in state:
            api_state["on"] = {"on": state["on"]}
        if "bri" in state and state["bri"] is not None:
            api_state["dimming"] = {"brightness": (state["bri"] / 254) * 100}
        
        # NEU: Prüfen, ob die Lampe Farbtemperatur unterstützt
        if "ct" in state and state["ct"] is not None:
            light_info = self._light_capabilities.get(light_id, {})
            if "color_temperature" in light_info:
                api_state["color_temperature"] = {"mirek": state["ct"]}
            else:
                self.log.debug(f"Lampe {light_id} unterstützt keine Farbtemperatur. Befehl wird ignoriert.")

        if api_state:
            try:
                self._hue.bridge._put_by_id('light', light_id, api_state)
            except Exception as e:
                self._log_error(f"Fehler beim Setzen des Zustands für Lampe {light_id}: {e}", exc_info=True)

    def set_group_state(self, group_id: str, state: dict):
        """Setzt den Zustand für eine Gruppe (Raum oder Zone)."""
        if not self.is_connected(): return

        try:
            target_grouped_light = next((gl for gl in self._hue.grouped_lights if gl.owner.rid == group_id), None)
            
            if not target_grouped_light:
                group_name = self._group_name_mapping.get(group_id, group_id)
                self._log_error(f"Kein steuerbarer Licht-Service für Gruppe '{group_name}' gefunden.")
                return

            group_kwargs = {}
            if "on" in state:
                group_kwargs["on"] = state["on"]
            if "bri" in state and state["bri"] is not None:
                group_kwargs["brightness"] = (state["bri"] / 254) * 100
            
            if group_kwargs:
                target_grouped_light.set_state(**group_kwargs)

            if "ct" in state and state.get("on", True):
                light_ids_in_group = self._group_light_mapping.get(group_id)
                
                if light_ids_in_group is None:
                    self.log.warning(f"Gruppe '{self._group_name_mapping.get(group_id, group_id)}' (ID: {group_id}) nicht im Cache. Versuche Neuladen...")
                    self._cache_device_and_group_info()
                    light_ids_in_group = self._group_light_mapping.get(group_id, [])

                if not light_ids_in_group:
                    group_name = self._group_name_mapping.get(group_id, group_id)
                    self.log.warning(f"Keine Lampen für Gruppe '{group_name}' (ID: {group_id}) gefunden. Farbtemperatur kann nicht gesetzt werden.")
                    return

                ct_state = {"ct": state["ct"]}
                time.sleep(0.1) 
                
                for light_id in light_ids_in_group:
                    self.set_light_state(light_id, ct_state)

        except Exception as e:
            group_name = self._group_name_mapping.get(group_id, group_id)
            self._log_error(f"Fehler beim Setzen des Zustands für Gruppe '{group_name}': {e}", exc_info=True)
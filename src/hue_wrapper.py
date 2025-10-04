from typing import Optional, Dict, List, Union, Literal
import logging
from python_hue_v2.hue import Hue
from python_hue_v2.scene import ScenePost, ActionPost

class HueBridge:
    """
    Eine Wrapper-Klasse, die eine stabile Verbindung zur Philips Hue
    Bridge über die v2 API verwaltet und high-level Methoden zur Steuerung bietet.
    """

    def __init__(self, ip: str, app_key: str, logger: Optional[logging.Logger] = None):
        self.ip = ip
        self.app_key = app_key
        self.logger = logger or logging.getLogger(__name__)
        self._hue: Optional[Hue] = None

    def connect(self):
        """Stellt die Verbindung zur Bridge her und verifiziert sie."""
        if not self.ip or not self.app_key:
            self.logger.warning("IP-Adresse oder App-Key fehlen. Verbindung nicht möglich.")
            return
        try:
            self._hue = Hue(self.ip, self.app_key)
            self._hue.bridge.get_bridge()
            self.logger.info(f"Erfolgreich mit Bridge unter {self.ip} (v2 API) verbunden.")
        except Exception as e:
            self.logger.error(f"Fehler bei der Initialisierung der v2 Bridge: {e}", exc_info=True)
            self._hue = None

    def is_connected(self) -> bool:
        return self._hue is not None

    @staticmethod
    def create_app_key(ip: str, logger: Optional[logging.Logger] = None) -> Optional[str]:
        log = logger or logging.getLogger(__name__)
        try:
            temp_hue = Hue(ip)
            log.info("Bitte den Knopf auf der Hue Bridge drücken...")
            app_key = temp_hue.bridge.connect()
            log.info(f"Neuer App-Key für Bridge {ip} erfolgreich erstellt.")
            return app_key
        except Exception as e:
            log.error(f"Fehler beim Erstellen des App-Keys: {e}", exc_info=True)
            return None

    def get_full_api_data(self) -> Dict:
        if not self.is_connected(): return {}
        try:
            # KORREKTUR: Die Controller-Objekte sind iterierbar. Wir konvertieren sie in Listen von Dictionaries.
            data = {
                "lights": [light.data_dict for light in self._hue.lights],
                "scenes": [scene.data_dict for scene in self._hue.scenes],
                "devices": [device.data_dict for device in self._hue.devices],
                "rooms": [room.data_dict for room in self._hue.rooms],
                "zones": [zone.data_dict for zone in self._hue.zones],
            }
            return data
        except Exception as e:
            self.logger.error(f"Unerwarteter Fehler beim Abrufen der gesamten Bridge-Daten: {e}", exc_info=True)
            return {}
        
    def get_grouped_lights(self) -> List:
        if not self.is_connected() or not hasattr(self._hue, 'grouped_light'): 
            return []
        try:
            return [gl.data_dict for gl in self._hue.grouped_light]
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Gruppenlichter: {e}", exc_info=True)
            return []
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
            self._hue.bridge.get_bridge() # Testaufruf zur Verifizierung
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
        return self._hue.bridge.get_all()

    def get_device_by_id(self, device_id: str) -> Optional[Dict]:
        if not self.is_connected(): return None
        try:
            return self._hue.bridge._get_by_id('device', device_id)
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen von Gerät {device_id}: {e}")
            return None
            
    def get_light_level_by_device_id(self, device_id: str) -> Optional[Dict]:
        device = self.get_device_by_id(device_id)
        if device:
            for service in device.get('services', []):
                if service.get('rtype') == 'light_level':
                    return self._hue.bridge._get_by_id('light_level', service['rid'])
        return None

    def get_temperature_by_device_id(self, device_id: str) -> Optional[Dict]:
        device = self.get_device_by_id(device_id)
        if device:
            for service in device.get('services', []):
                if service.get('rtype') == 'temperature':
                    return self._hue.bridge._get_by_id('temperature', service['rid'])
        return None

    def set_group_state(self, group_id: str, state: dict):
        if not self.is_connected(): return
        
        group = self._hue.bridge._get_by_id('room', group_id) or self._hue.bridge._get_by_id('zone', group_id)
        if not group:
            self.logger.error(f"Gruppe {group_id} nicht gefunden.")
            return

        grouped_light_service = next((s for s in group['services'] if s['rtype'] == 'grouped_light'), None)
        if not grouped_light_service:
            self.logger.error(f"Kein 'grouped_light' Service für Gruppe {group_id} gefunden.")
            return
        
        grouped_light_id = grouped_light_service['rid']

        v2_state = {}
        if 'on' in state:
            v2_state['on'] = {'on': state.get('status', False)}
        if 'bri' in state:
            v2_state['dimming'] = {'brightness': (state['bri'] / 254) * 100}
        if 'ct' in state:
            v2_state['color_temperature'] = {'mirek': state['ct']}
        
        try:
            self._hue.bridge.set_grouped_light_service(grouped_light_id, v2_state)
        except Exception as e:
            self.logger.error(f"Fehler beim Setzen des Zustands für Gruppe {group_id}: {e}", exc_info=True)
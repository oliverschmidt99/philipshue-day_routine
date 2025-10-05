"""
Ein erweiterter Wrapper für die python-hue-v2 Bibliothek, um die v2 API
umfassend zu kapseln und eine einfache, high-level Steuerung zu ermöglichen.
"""
from typing import Optional, Dict, List, Literal
import logging
from python_hue_v2.hue import Hue
from python_hue_v2.scene import Scene as HueScene

class HueBridge:
    """
    Eine umfassende Wrapper-Klasse, die eine stabile Verbindung zur Philips Hue
    Bridge über die v2 API verwaltet und high-level Methoden zur Steuerung bietet.
    """

    def __init__(self, ip: str, app_key: str, logger: Optional[logging.Logger] = None):
        self.ip = ip
        self.app_key = app_key
        self.logger = logger or logging.getLogger(__name__)
        self._hue: Optional[Hue] = None
        self.connect()

    def connect(self):
        """Stellt die Verbindung zur Bridge her und verifiziert sie."""
        if not self.ip or not self.app_key:
            self.logger.warning("IP-Adresse oder App-Key fehlen. Verbindung nicht möglich.")
            self._hue = None
            return
        try:
            self._hue = Hue(self.ip, self.app_key)
            self.logger.info(f"Verbindung zur Bridge unter {self.ip} (v2 API) wird versucht...")
            self._hue.bridge.get_bridge()
            self.logger.info("Verbindung zur Bridge erfolgreich hergestellt.")
        except Exception as e:
            self.logger.error(f"Fehler bei der Initialisierung der v2 Bridge: {e}", exc_info=True)
            self._hue = None

    def is_connected(self) -> bool:
        """Prüft, ob eine aktive und funktionierende Verbindung zur Bridge besteht."""
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
            return {
                "lights": self._hue.bridge.get_lights() or [],
                "scenes": self._hue.bridge.get_scenes() or [],
                "devices": self._hue.bridge.get_devices() or [],
                "rooms": self._hue.bridge.get_rooms() or [],
                "zones": self._hue.bridge.get_zones() or [],
                "grouped_lights": self._hue.bridge.get_grouped_lights() or [],
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der gesamten Bridge-Daten: {e}", exc_info=True)
            return {}

    def get_grouped_lights(self) -> List[Dict]:
        if not self.is_connected(): return []
        return self._hue.bridge.get_grouped_lights() or []
            
    def get_resource_by_id(self, resource_type: str, resource_id: str) -> Optional[Dict]:
        if not self.is_connected(): return None
        try:
            return self._hue.bridge._get_by_id(resource_type, resource_id)
        except Exception:
            return None

    def set_light_state(self, light_id: str, state: dict):
        if not self.is_connected(): return
        try:
            self._hue.bridge.set_light(light_id_v2=light_id, data=state)
        except Exception as e:
            self.logger.error(f"Fehler beim Setzen des Zustands für Lampe {light_id}: {e}", exc_info=True)

    def set_group_state(self, group_id: str, state: dict):
        if not self.is_connected(): return
        try:
            grouped_light_id = self._find_grouped_light_id_for_group(group_id)
            if grouped_light_id:
                self._hue.bridge.set_grouped_light_service(grouped_light_id, state)
            else:
                self.logger.warning(f"Kein 'grouped_light' Service für Gruppe {group_id} gefunden.")
        except Exception as e:
            self.logger.error(f"Fehler beim Setzen des Zustands für Gruppe {group_id}: {e}", exc_info=True)

    def recall_scene(self, scene_id: str):
        if not self.is_connected(): return
        try:
            # KORREKTUR: Die ID wird als positional argument übergeben, nicht als keyword.
            scene = HueScene(self._hue.bridge, scene_id)
            scene.recall(action='active')
        except Exception as e:
            self.logger.error(f"Fehler beim Aktivieren der Szene {scene_id}: {e}", exc_info=True)

    def create_scene(self, name: str, group_id: str, group_type: Literal['room', 'zone'], actions: List[Dict]) -> Optional[Dict]:
        if not self.is_connected(): return None
        try:
            scene_data = {
                "metadata": {"name": name},
                "group": {"rid": group_id, "rtype": group_type},
                "actions": actions,
                "type": "scene"
            }
            return self._hue.bridge.create_scene(scene_data)
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Szene '{name}': {e}", exc_info=True)
            return None

    def delete_scene(self, scene_id: str):
        if not self.is_connected(): return
        try:
            # KORREKTUR: Die ID wird als positional argument übergeben.
            scene = HueScene(self._hue.bridge, scene_id)
            scene.delete()
        except Exception as e:
            self.logger.error(f"Fehler beim Löschen der Szene {scene_id}: {e}", exc_info=True)

    def _find_grouped_light_id_for_group(self, group_id: str) -> Optional[str]:
        """Findet die ID des 'grouped_light'-Services für einen gegebenen Raum oder eine Zone."""
        all_groups = (self._hue.bridge.get_rooms() or []) + (self._hue.bridge.get_zones() or [])
        for group in all_groups:
            if group.get('id') == group_id:
                for service in group.get('services', []):
                    if service.get('rtype') == 'grouped_light':
                        return service.get('rid')
        return None
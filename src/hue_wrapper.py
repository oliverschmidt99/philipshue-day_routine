"""
Ein erweiterter Wrapper für die python-hue-v2 Bibliothek, um die v2 API
umfassend zu kapseln und eine einfache, high-level Steuerung zu ermöglichen.
"""
from typing import Optional, Dict, List, Literal
import logging
from python_hue_v2.hue import Hue
from python_hue_v2.scene import Scene as HueScene

class HueBridge:
    def __init__(self, ip: str, app_key: str, logger: Optional[logging.Logger] = None):
        self.ip = ip
        self.app_key = app_key
        self.logger = logger or logging.getLogger(__name__)
        self._hue: Optional[Hue] = None
        self.connect()

    def connect(self):
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
            scene = HueScene(self._hue.bridge, scene_id)
            scene.recall(action='active')
        except Exception as e:
            self.logger.error(f"Fehler beim Aktivieren der Szene {scene_id}: {e}", exc_info=True)

    def create_scene(self, name: str, group_id: str, group_type: Literal['room', 'zone'], actions: List[Dict]) -> Optional[Dict]:
        # ... (Methode bleibt unverändert)
        pass

    def delete_scene(self, scene_id: str):
        # ... (Methode bleibt unverändert)
        pass

    def _find_grouped_light_id_for_group(self, group_id: str) -> Optional[str]:
        # ... (Methode bleibt unverändert)
        pass
        
    def update_resource_metadata(self, resource_type: str, resource_id: str, new_name: str):
        """Ändert den Namen einer Ressource (z.B. room, zone, light, device)."""
        if not self.is_connected(): return
        try:
            payload = {"metadata": {"name": new_name}}
            self._hue.bridge.put(f"/{resource_type}/{resource_id}", payload)
            self.logger.info(f"Ressource '{resource_type}/{resource_id}' umbenannt in '{new_name}'.")
        except Exception as e:
            self.logger.error(f"Fehler beim Umbenennen von '{resource_type}/{resource_id}': {e}", exc_info=True)
            
    def move_device_to_group(self, device_id: str, new_group_id: str):
        """Verschiebt ein Gerät (und damit dessen Lichter) in einen neuen Raum oder eine neue Zone."""
        if not self.is_connected(): return

        all_groups = self.get_full_api_data().get('rooms', []) + self.get_full_api_data().get('zones', [])
        old_group = None
        
        # 1. Finde die alte Gruppe, um das Gerät daraus zu entfernen
        for group in all_groups:
            if any(child.get('rid') == device_id for child in group.get('children', [])):
                old_group = group
                break

        # 2. Entferne Gerät aus alter Gruppe (falls es in einer war)
        if old_group:
            old_children = [child for child in old_group.get('children', []) if child.get('rid') != device_id]
            group_type = 'room' if 'archetype' in old_group.get('metadata', {}) else 'zone'
            payload = {"children": old_children}
            try:
                self._hue.bridge.put(f"/{group_type}/{old_group['id']}", payload)
                self.logger.info(f"Gerät {device_id} aus Gruppe {old_group['id']} entfernt.")
            except Exception as e:
                 self.logger.error(f"Fehler beim Entfernen von Gerät aus Gruppe {old_group['id']}: {e}", exc_info=True)


        # 3. Füge Gerät zur neuen Gruppe hinzu
        new_group = next((g for g in all_groups if g['id'] == new_group_id), None)
        if new_group:
            new_children = new_group.get('children', [])
            if not any(child.get('rid') == device_id for child in new_children):
                new_children.append({"rid": device_id, "rtype": "device"})
            
            payload = {"children": new_children}
            group_type = 'room' if 'archetype' in new_group.get('metadata', {}) else 'zone'
            try:
                self._hue.bridge.put(f"/{group_type}/{new_group_id}", payload)
                self.logger.info(f"Gerät {device_id} zu Gruppe {new_group_id} hinzugefügt.")
            except Exception as e:
                 self.logger.error(f"Fehler beim Hinzufügen von Gerät zu Gruppe {new_group_id}: {e}", exc_info=True)
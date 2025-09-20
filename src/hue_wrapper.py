"""
Ein erweiterter Wrapper für die python-hue-v2 Bibliothek, um die v2 API
umfassend zu kapseln und eine einfache, high-level Steuerung zu ermöglichen.

Version: 2.0
"""
from typing import Optional, Dict, List, Union, Literal
import logging

# Direkte Importe aus der python-hue-v2 Bibliothek
from python_hue_v2.hue import Hue
from python_hue_v2.light import Light as HueLight
from python_hue_v2.room import Room as HueRoom
from python_hue_v2.zone import Zone as HueZone
from python_hue_v2.scene import Scene as HueScene
from python_hue_v2.scene import ScenePost, ActionPost
from python_hue_v2.grouped_light import GroupedLight as HueGroupedLight


class HueBridge:
    """
    Eine umfassende Wrapper-Klasse, die eine stabile Verbindung zur Philips Hue
    Bridge über die v2 API verwaltet und high-level Methoden zur Steuerung bietet.
    """

    def __init__(self, ip: str, app_key: str, logger: Optional[logging.Logger] = None):
        self.ip = ip
        self.app_key = app_key
        self.log = logger or logging.getLogger(__name__)
        self._hue: Optional[Hue] = None
        self.connect()

    def _log(self, level: str, message: str, exc_info: bool = False):
        """Zentrale Logging-Funktion."""
        log_func = getattr(self.log, level.lower(), self.log.info)
        # KORREKTUR 1: Übergebe exc_info nur, wenn es sich um einen Fehler handelt
        if level.lower() == 'error' and exc_info:
            log_func(message, exc_info=exc_info)
        else:
            log_func(message)

    # /////////////////////////////////////////////////////////////////////////
    # ///   Connection & Status
    # /////////////////////////////////////////////////////////////////////////

    def connect(self):
        """Stellt die Verbindung zur Bridge her und verifiziert sie."""
        if not self.ip or not self.app_key:
            self._log("warning", "IP-Adresse oder App-Key fehlen. Verbindung nicht möglich.")
            return
        try:
            self._hue = Hue(self.ip, self.app_key)
            self._hue.bridge.get_bridge()
            self._log("info", f"Erfolgreich mit Bridge unter {self.ip} (v2 API) verbunden.")
        except Exception as e:
            self._log("error", f"Fehler bei der Initialisierung der v2 Bridge: {e}", exc_info=True)
            self._hue = None

    def is_connected(self) -> bool:
        """Prüft, ob eine aktive und funktionierende Verbindung zur Bridge besteht."""
        return self._hue is not None

    @staticmethod
    def create_app_key(ip: str, logger: Optional[logging.Logger] = None) -> Optional[str]:
        log = logger or logging.getLogger(__name__)
        try:
            temp_hue = Hue(ip)
            log.info("Bitte den Knopf auf der Hue Bridge drücken, um einen neuen App-Key zu erstellen...")
            app_key = temp_hue.bridge.connect()
            log.info(f"Neuer App-Key für Bridge {ip} erfolgreich erstellt.")
            return app_key
        except Exception as e:
            log.error(f"Fehler beim Erstellen des App-Keys: {e}", exc_info=True)
            return None

    # /////////////////////////////////////////////////////////////////////////
    # ///   Getter (Informationen abrufen)
    # /////////////////////////////////////////////////////////////////////////

    def get_bridge_info(self) -> Dict:
        if not self.is_connected(): return {}
        return self._hue.bridge.get_bridge()

    def get_full_api_data(self) -> Dict:
        if not self.is_connected(): return {}
        return {
            "lights": self.get_lights(),
            "scenes": self.get_scenes(),
            "rooms": self.get_rooms(),
            "zones": self.get_zones(),
            "devices": self.get_devices(),
            "grouped_lights": self.get_grouped_lights(),
        }

    def get_resource_by_id(self, resource_type: str, resource_id: str) -> Optional[Dict]:
        if not self.is_connected(): return None
        try:
            return self._hue.bridge._get_by_id(resource_type, resource_id)
        except Exception as e:
            self._log("error", f"Fehler beim Abrufen der Ressource {resource_type}/{resource_id}: {e}")
            return None

    def get_lights(self) -> List[Dict]:
        if not self.is_connected(): return []
        return self._hue.bridge.get_lights()

    def get_light_by_id(self, light_id: str) -> Optional[Dict]:
        return self.get_resource_by_id('light', light_id)

    def get_light_by_name(self, name: str) -> Optional[Dict]:
        if not self.is_connected(): return None
        for light in self.get_lights():
            if light.get('metadata', {}).get('name', '').lower() == name.lower():
                return light
        return None

    def get_devices(self) -> List[Dict]:
        if not self.is_connected(): return []
        return self._hue.bridge.get_devices()

    def get_device_by_id(self, device_id: str) -> Optional[Dict]:
        return self.get_resource_by_id('device', device_id)

    def get_rooms(self) -> List[Dict]:
        if not self.is_connected(): return []
        return self._hue.bridge.get_rooms()

    def get_zones(self) -> List[Dict]:
        if not self.is_connected(): return []
        return self._hue.bridge.get_zones()
        
    def get_grouped_lights(self) -> List[Dict]:
        if not self.is_connected(): return []
        return self._hue.bridge.get_grouped_lights()

    def get_group_by_id(self, group_id: str) -> Optional[Dict]:
        all_groups = self.get_rooms() + self.get_zones()
        return next((g for g in all_groups if g.get('id') == group_id), None)
        
    def get_group_by_name(self, name: str) -> Optional[Dict]:
        all_groups = self.get_rooms() + self.get_zones()
        for group in all_groups:
            if 'services' in group:
                    light_service_id = self._find_grouped_light_id_for_group(group['id'])
                    if light_service_id:
                        light_service = self.get_resource_by_id('grouped_light', light_service_id)
                        if light_service and light_service.get('metadata', {}).get('name', '').lower() == name.lower():
                            return group
        return None

    def get_lights_in_group(self, group_id: str) -> List[Dict]:
        group = self.get_group_by_id(group_id)
        if not group or 'children' not in group:
            return []
        
        light_ids = [child['rid'] for child in group['children']]
        return [self.get_light_by_id(lid) for lid in light_ids if self.get_light_by_id(lid)]

    def get_scenes(self) -> List[Dict]:
        if not self.is_connected(): return []
        return self._hue.bridge.get_scenes()

    def get_scene_by_id(self, scene_id: str) -> Optional[Dict]:
        return self.get_resource_by_id('scene', scene_id)

    def get_scene_by_name(self, name: str) -> Optional[Dict]:
        if not self.is_connected(): return None
        for scene in self.get_scenes():
            if scene.get('metadata', {}).get('name', '').lower() == name.lower():
                return scene
        return None

    # /////////////////////////////////////////////////////////////////////////
    # ///   Setter (Zustände ändern & Aktionen ausführen)
    # /////////////////////////////////////////////////////////////////////////
    
    def set_light_state(self, light_id: str, state: dict):
        if not self.is_connected(): return
        try:
            for property_name, property_value in state.items():
                # KORREKTUR 2: Der Parameter heißt 'light_id_v2'
                self._hue.bridge.set_light(
                    light_id_v2=light_id, 
                    light_property_name=property_name, 
                    property_value=property_value
                )
        except Exception as e:
            self._log("error", f"Fehler beim Setzen des Zustands für Lampe {light_id}: {e}", exc_info=True)

    def turn_on_light(self, light_id: str, brightness: Optional[int] = None, transition_ms: Optional[int] = None):
        state = {'on': {'on': True}}
        if brightness is not None:
            state['dimming'] = {'brightness': max(0, min(100, brightness))}
        if transition_ms is not None:
              state['dynamics'] = {'duration': transition_ms}
        self.set_light_state(light_id, state)

    def turn_off_light(self, light_id: str, transition_ms: Optional[int] = None):
        state = {'on': {'on': False}}
        if transition_ms is not None:
              state['dynamics'] = {'duration': transition_ms}
        self.set_light_state(light_id, state)
        
    def set_light_color_xy(self, light_id: str, x: float, y: float):
        state = {'color': {'xy': {'x': x, 'y': y}}}
        self.set_light_state(light_id, state)

    def set_light_color_temp(self, light_id: str, mirek: int):
        state = {'color_temperature': {'mirek': mirek}}
        self.set_light_state(light_id, state)

    def set_group_state(self, group_id: str, state: dict):
        if not self.is_connected(): return
        try:
            grouped_light_id = self._find_grouped_light_id_for_group(group_id)
            if not grouped_light_id:
                self._log("error", f"Kein 'grouped_light' Service für Gruppe {group_id} gefunden.")
                return
            self._hue.bridge.set_grouped_light_service(grouped_light_id, state)
        except Exception as e:
            self._log("error", f"Fehler beim Setzen des Zustands für Gruppe {group_id}: {e}", exc_info=True)

    def turn_on_group(self, group_id: str, brightness: Optional[int] = None, transition_ms: Optional[int] = None):
        state = {'on': {'on': True}}
        if brightness is not None:
            state['dimming'] = {'brightness': max(0, min(100, brightness))}
        if transition_ms is not None:
              state['dynamics'] = {'duration': transition_ms}
        self.set_group_state(group_id, state)

    def turn_off_group(self, group_id: str, transition_ms: Optional[int] = None):
        state = {'on': {'on': False}}
        if transition_ms is not None:
              state['dynamics'] = {'duration': transition_ms}
        self.set_group_state(group_id, state)

    def recall_scene(self, scene_id: str):
        if not self.is_connected(): return
        try:
            scene = HueScene(self._hue.bridge, scene_id)
            scene.recall(action='active')
            self._log("info", f"Szene {scene_id} erfolgreich aktiviert.")
        except Exception as e:
            self._log("error", f"Fehler beim Aktivieren der Szene {scene_id}: {e}", exc_info=True)

    def create_scene(self, name: str, group_id: str, group_type: Literal['room', 'zone'], actions: List[Dict]) -> Optional[List[Dict]]:
        if not self.is_connected(): return None
        try:
            scene_data = ScenePost.create_by_parameters(
                name=name,
                group_rid=group_id,
                group_rtype=group_type,
                actions=[ActionPost(a) for a in actions]
            )
            response = self._hue.bridge.create_scene(scene_data.data_dict)
            self._log("info", f"Szene '{name}' erfolgreich erstellt.")
            return response
        except Exception as e:
            self._log("error", f"Fehler beim Erstellen der Szene '{name}': {e}", exc_info=True)
            return None

    def delete_scene(self, scene_id: str):
        if not self.is_connected(): return
        try:
            self._hue.bridge.delete_scene(scene_id)
            self._log("info", f"Szene {scene_id} erfolgreich gelöscht.")
        except Exception as e:
            self._log("error", f"Fehler beim Löschen der Szene {scene_id}: {e}", exc_info=True)

    # /////////////////////////////////////////////////////////////////////////
    # ///   Private Hilfsfunktionen
    # /////////////////////////////////////////////////////////////////////////

    def _find_grouped_light_id_for_group(self, group_id: str) -> Optional[str]:
        group = self.get_group_by_id(group_id)
        if group and 'services' in group:
            service = next((s for s in group['services'] if s.get('rtype') == 'grouped_light'), None)
            if service:
                return service.get('rid')
        return None
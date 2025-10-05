"""
Ein erweiterter Wrapper für die python-hue-v2 Bibliothek, um die v2 API
umfassend zu kapseln und eine einfache, high-level Steuerung zu ermöglichen.

Version: 2.0
"""
from typing import Optional, Dict, List, Literal
import logging
from python_hue_v2.hue import Hue
from python_hue_v2.scene import ScenePost, ActionPost

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
            return
        try:
            self._hue = Hue(self.ip, self.app_key)
            self._hue.bridge.get_bridge()
            self.logger.info(f"Erfolgreich mit Bridge unter {self.ip} (v2 API) verbunden.")
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
            log.info("Bitte den Knopf auf der Hue Bridge drücken, um einen neuen App-Key zu erstellen...")
            app_key = temp_hue.bridge.connect()
            log.info(f"Neuer App-Key für Bridge {ip} erfolgreich erstellt.")
            return app_key
        except Exception as e:
            log.error(f"Fehler beim Erstellen des App-Keys: {e}", exc_info=True)
            return None

    def get_full_api_data(self) -> Dict:
        if not self.is_connected(): return {}
        try:
            data = {
                "lights": [light.data_dict for light in self._hue.lights],
                "scenes": [scene.data_dict for scene in self._hue.scenes],
                "devices": [device.data_dict for device in self._hue.devices],
                "rooms": [room.data_dict for room in self._hue.rooms],
                "zones": [zone.data_dict for zone in self._hue.zones],
                "grouped_lights": [gl.data_dict for gl in self._hue.grouped_light],
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

    def get_device_by_id(self, device_id: str) -> Optional[Dict]:
        """Holt ein Gerät anhand seiner ID."""
        if not self.is_connected(): return None
        try:
            for device in self._hue.devices:
                if device.id == device_id:
                    return device.data_dict
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen von Gerät {device_id}: {e}", exc_info=True)
        return None

    def get_resource_by_id(self, resource_type: str, resource_id: str) -> Optional[Dict]:
        """Holt eine beliebige Ressource anhand ihres Typs und ihrer ID."""
        if not self.is_connected(): return None
        try:
            # Annahme: _get_by_id ist eine hypothetische, effiziente Methode.
            # Wenn nicht vorhanden, muss dies anders implementiert werden.
            if hasattr(self._hue.bridge, '_get_by_id'):
                 return self._hue.bridge._get_by_id(resource_type, resource_id)
            # Fallback, falls die Methode nicht existiert
            else:
                resources = getattr(self._hue, resource_type + "s", [])
                for resource in resources:
                    if resource.id == resource_id:
                        return resource.data_dict
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen von {resource_type}/{resource_id}: {e}", exc_info=True)
        return None

    def set_group_state(self, group_id: str, state: dict):
        """Setzt den Zustand für eine Lichtgruppe (Raum oder Zone)."""
        if not self.is_connected(): return
        
        # Finde den grouped_light Service, der zu diesem Raum/dieser Zone gehört
        target_grouped_light = None
        for gl in self._hue.grouped_light:
            if gl.owner and gl.owner.rid == group_id:
                target_grouped_light = gl
                break
        
        if target_grouped_light:
            try:
                target_grouped_light.set_state(state)
            except Exception as e:
                self.logger.error(f"Fehler beim Setzen des Gruppenstatus für {group_id}: {e}", exc_info=True)
        else:
            self.logger.warning(f"Kein grouped_light Service für Gruppe {group_id} gefunden.")
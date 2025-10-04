"""
Liest und interpretiert Daten von einem Hue Bewegungssensor,
inklusive der zugehörigen Unter-Sensoren für Helligkeit und Temperatur.
"""
from src.hue_wrapper import HueBridge
from .logger import AppLogger

class Sensor:
    """Liest Daten von einem Hue-Bewegungssensor und stellt sie bereit."""
    def __init__(self, bridge: HueBridge, device_id: str, log: AppLogger):
        self.bridge = bridge
        self.log = log
        self.device_id = device_id
        self._device_data = None

    def _get_device_data(self):
        """Holt die Daten für das spezifische Gerät, falls noch nicht vorhanden."""
        if not self._device_data:
            if not self.bridge.is_connected():
                return None
            # Nutzt die neue Funktion aus dem Wrapper
            self._device_data = self.bridge.get_device_by_id(self.device_id)
            if not self._device_data:
                self.log.warning(f"Kein Gerät mit ID {self.device_id} gefunden.")
        return self._device_data

    def _get_service_data(self, service_type: str):
        """Holt die vollen Daten eines spezifischen Services (z.B. motion) des Geräts."""
        device = self._get_device_data()
        if not device or 'services' not in device:
            return None
        
        service_ref = next((s for s in device['services'] if s.get('rtype') == service_type), None)
        if not service_ref:
            return None
        
        return self.bridge.get_resource_by_id(service_type, service_ref['rid'])

    def get_motion(self) -> bool:
        """Gibt True zurück, wenn eine Bewegung erkannt wird, sonst False."""
        motion_data = self._get_service_data('motion')
        return motion_data.get('motion', {}).get('motion', False) if motion_data else False

    def get_brightness(self) -> int | None:
        """Gibt den Helligkeitswert (light_level) vom Lichtsensor zurück."""
        light_data = self._get_service_data('light_level')
        return light_data.get('light', {}).get('light_level') if light_data else None

    def get_temperature(self) -> float | None:
        """Gibt die Temperatur in Grad Celsius vom Temperatursensor zurück."""
        temp_data = self._get_service_data('temperature')
        return temp_data.get('temperature', {}).get('temperature') if temp_data else None
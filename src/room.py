"""
Repräsentiert einen Raum oder eine Zone der Hue Bridge
und kapselt die Steuerungsbefehle für die zugehörige Lichtgruppe.
"""
import time
from src.hue_wrapper import HueBridge
from src.logger import AppLogger

class Room:
    """Repräsentiert einen Raum oder eine Zone und steuert die zugehörigen Lichter."""
    def __init__(self, bridge: HueBridge, log: AppLogger, name: str, group_id: str, **kwargs):
        self.bridge = bridge
        self.log = log
        self.name = name
        self.group_id = group_id
        self.last_command_time = 0

    def apply_state(self, state: dict, command_throttle_s: int = 1):
        """Setzt den Zustand für die Lichtgruppe im Raum, mit einem Throttle."""
        if not self.group_id or time.time() - self.last_command_time < command_throttle_s:
            return
        self.bridge.set_group_state(self.group_id, state)
        self.last_command_time = time.time()
        self.log.debug(f"Raum '{self.name}' (Gruppe {self.group_id}) gesetzt auf: {state}")

    def _get_grouped_light_data(self) -> dict | None:
        """Holt die rohen Daten des zugehörigen GroupedLight-Services."""
        if not self.group_id: return None
        all_gl = self.bridge.get_grouped_lights()
        return next((gl for gl in all_gl if gl.get('owner', {}).get('rid') == self.group_id), None)

    def is_any_light_on(self) -> bool | None:
        """Prüft, ob irgendein Licht in der Gruppe des Raumes an ist."""
        group_data = self._get_grouped_light_data()
        return group_data.get('on', {}).get('on') if group_data else None

    def get_current_state(self) -> dict | None:
        """Holt den aktuellen Lichtzustand der Gruppe des Raumes."""
        group_data = self._get_grouped_light_data()
        if group_data:
            brightness = group_data.get('dimming', {}).get('brightness', 0)
            return {
                "on": group_data.get('on', {}).get('on'),
                "bri": int((brightness / 100) * 254) if brightness is not None else None,
                "ct": group_data.get('color_temperature', {}).get('mirek')
            }
        return None
"""
Repräsentiert einen Raum oder eine Zone der Hue Bridge
und kapselt die Steuerungsbefehle für die zugehörige Lichtgruppe.
"""
import time
from src.hue_wrapper import HueBridge
from .logger import Logger

class Room:
    """Repräsentiert einen Raum oder eine Zone und steuert die zugehörigen Lichter."""
    def __init__(self, bridge: HueBridge, log: Logger, name: str, group_id: int):
        self.bridge = bridge
        self.log = log
        self.name = name
        self.group_id = int(group_id)
        self.last_command_time = 0

    def apply_state(self, state: dict, command_throttle_s: int = 1):
        """Setzt den Zustand für die Lichtgruppe im Raum, mit einem Throttle."""
        if time.time() - self.last_command_time < command_throttle_s:
            return
        self.bridge.set_group(self.group_id, state)
        self.last_command_time = time.time()
        self.log.debug(f"Raum '{self.name}' (Gruppe {self.group_id}) gesetzt auf: {state}")

    def is_any_light_on(self) -> bool | None:
        """Prüft, ob irgendein Licht in der Gruppe des Raumes an ist."""
        group_state = self.bridge.get_group(self.group_id)
        return group_state.get("state", {}).get("any_on") if group_state else None

    def get_current_state(self) -> dict | None:
        """Holt den aktuellen Lichtzustand der Gruppe des Raumes."""
        group_data = self.bridge.get_group(self.group_id)
        return group_data.get("action") if group_data else None
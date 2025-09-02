"""
Repräsentiert einen Raum oder eine Zone der Hue Bridge
und kapselt die Steuerungsbefehle für die zugehörige Lichtgruppe.
"""

import time
from phue import Bridge, PhueException
from .logger import Logger


class Room:
    """Repräsentiert einen Raum oder eine Zone und steuert die zugehörigen Lichter."""

    def __init__(self, bridge: Bridge, log: Logger, name: str, group_id: int):
        self.bridge = bridge
        self.log = log
        self.name = name
        self.group_id = int(group_id)
        self.last_command_time = 0

    def apply_state(self, state: dict, command_throttle_s: float = 1.0):
        """Setzt den Zustand für die Lichtgruppe im Raum, mit einem Throttle."""
        if time.time() - self.last_command_time < command_throttle_s:
            return
        try:
            self.bridge.set_group(self.group_id, state)
            self.last_command_time = time.time()
            self.log.debug(
                f"Raum '{self.name}' (Gruppe {self.group_id}) gesetzt auf: {state}"
            )
        except PhueException as e:
            self.log.error(
                f"Fehler beim Setzen des Zustands für Raum '{self.name}': {e}"
            )

    def is_any_light_on(self) -> bool | None:
        """Prüft, ob irgendein Licht in der Gruppe des Raumes an ist."""
        try:
            group_state = self.bridge.get_group(self.group_id)
            return group_state.get("state", {}).get("any_on")
        except (PhueException, TypeError) as e:
            self.log.error(
                f"Konnte Status für Gruppe {self.group_id} nicht abrufen: {e}"
            )
            return None

    def get_current_state(self) -> dict | None:
        """Holt den aktuellen Lichtzustand der Gruppe des Raumes."""
        try:
            group_data = self.bridge.get_group(self.group_id)
            return group_data.get("action")
        except (PhueException, TypeError) as e:
            self.log.error(
                f"Konnte Zustand für Gruppe {self.group_id} nicht abrufen: {e}"
            )
            return None

# src/room.py
import time
from phue import Bridge, PhueException
from .logger import Logger


class Room:
    """Repräsentiert einen Raum oder eine Zone und steuert die zugehörigen Lichter."""

    def __init__(
        self, bridge: Bridge, log: Logger, name: str, group_ids: list[int], **kwargs
    ):
        self.bridge = bridge
        self.log = log
        self.name = name
        self.group_ids = [int(gid) for gid in group_ids]
        self.last_command_time = 0

    def apply_state(self, state: dict, command_throttle_s: int = 1):
        """Setzt den Zustand für alle Lichtgruppen im Raum, mit einem Throttle."""
        if time.time() - self.last_command_time < command_throttle_s:
            return
        try:
            self.bridge.set_group(self.group_ids, state)
            self.last_command_time = time.time()
        except PhueException as e:
            self.log.error(
                f"Fehler beim Setzen des Zustands für Raum '{self.name}': {e}"
            )

    def is_any_light_on(self) -> bool | None:
        """Prüft, ob irgendein Licht in der ersten Gruppe des Raumes an ist."""
        if not self.group_ids:
            return False
        try:
            state = self.bridge.get_group(self.group_ids[0], "on")
            return state if isinstance(state, bool) else None
        except PhueException as e:
            self.log.error(
                f"Konnte Status für Gruppe {self.group_ids[0]} nicht abrufen: {e}"
            )
            return None

    def get_current_state(self) -> dict | None:
        """Holt den aktuellen Lichtzustand der ersten Gruppe des Raumes."""
        if not self.group_ids:
            return None
        try:
            group_data = self.bridge.get_group(self.group_ids[0])
            return group_data.get("action")
        except PhueException as e:
            self.log.error(
                f"Konnte Zustand für Gruppe {self.group_ids[0]} nicht abrufen: {e}"
            )
            return None

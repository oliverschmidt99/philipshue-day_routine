"""
Repräsentiert einen Raum oder eine Zone der Hue Bridge
und kapselt die Steuerungsbefehle für die zugehörigen Lichtgruppen.
"""

import time
from phue import Bridge, PhueException
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .logger import Logger


class Room:
    """Repräsentiert einen Raum oder eine Zone und steuert die zugehörigen Lichter."""

    # **kwargs fängt alle unerwarteten Argumente wie 'sensor_id' ab
    def __init__(
        self, bridge: Bridge, log: "Logger", name: str, group_ids: list, **kwargs
    ):
        """Initialisiert das Room-Objekt."""
        self.bridge = bridge
        self.log = log
        self.name = name
        self.group_ids = [int(gid) for gid in group_ids]
        self.last_command_time = 0
        self.log.info(
            f"Raum '{self.name}' initialisiert mit Gruppen-IDs: {self.group_ids}"
        )

    def apply_state(self, state: dict, command_throttle_s: int = 1):
        """Setzt den Zustand für alle Lichtgruppen im Raum, mit einem Throttle."""
        if time.time() - self.last_command_time < command_throttle_s:
            return
        try:
            self.bridge.set_group(self.group_ids, state)
            self.last_command_time = time.time()
            self.log.debug(
                f"Raum '{self.name}' (Gruppen {self.group_ids}) gesetzt auf: {state}"
            )
        except PhueException as e:
            self.log.error(
                f"Fehler beim Setzen des Zustands für Raum '{self.name}': {e}"
            )

    def is_any_light_on(self) -> bool | None:
        """Prüft, ob irgendein Licht in der ERSTEN Gruppe des Raumes an ist."""
        if not self.group_ids:
            return None
        try:
            group_state = self.bridge.get_group(self.group_ids[0])
            return group_state.get("state", {}).get("any_on")
        except (PhueException, TypeError) as e:
            self.log.error(
                f"Konnte Status für Gruppe {self.group_ids[0]} nicht abrufen: {e}"
            )
            return None

    def get_current_state(self) -> dict | None:
        """Holt den aktuellen Lichtzustand der ERSTEN Gruppe des Raumes."""
        if not self.group_ids:
            return None
        try:
            group_data = self.bridge.get_group(self.group_ids[0])
            return group_data.get("action")
        except (PhueException, TypeError) as e:
            self.log.error(
                f"Konnte Zustand für Gruppe {self.group_ids[0]} nicht abrufen: {e}"
            )
            return None

"""
Repräsentiert einen Raum oder eine Zone der Hue Bridge
und kapselt die Steuerungsbefehle für die zugehörige Lichtgruppe.
"""

import time
# Importiere den Wrapper anstelle der Bridge-Klasse
from .hue_wrapper import HueBridge
from .logger import Logger


class Room:
    """Repräsentiert einen Raum oder eine Zone und steuert die zugehörigen Lichter."""

    # Passe den Konstruktor an, um eine HueBridge-Instanz zu erhalten
    def __init__(self, bridge: HueBridge, log: Logger, name: str, group_id: int):
        self.bridge = bridge
        self.log = log
        self.name = name
        self.group_id = int(group_id)
        self.last_command_time = 0

    def apply_state(self, state: dict, command_throttle_s: float = 1.0):
        """Setzt den Zustand für die Lichtgruppe im Raum, mit einem Throttle."""
        if time.time() - self.last_command_time < command_throttle_s:
            return
        
        # Nutze die Wrapper-Methode
        self.bridge.set_group_state(self.group_id, state)
        self.last_command_time = time.time()
        self.log.debug(
            f"Raum '{self.name}' (Gruppe {self.group_id}) gesetzt auf: {state}"
        )

    def is_any_light_on(self) -> bool | None:
        """Prüft, ob irgendein Licht in der Gruppe des Raumes an ist."""
        # Nutze die Wrapper-Methode
        group_state = self.bridge.get_group(self.group_id)
        if group_state:
            return group_state.get("state", {}).get("any_on")
        # Fehler werden bereits im Wrapper geloggt
        return None

    def get_current_state(self) -> dict | None:
        """Holt den aktuellen Lichtzustand der Gruppe des Raumes."""
        # Nutze die Wrapper-Methode
        group_data = self.bridge.get_group(self.group_id)
        if group_data:
            return group_data.get("action")
        # Fehler werden bereits im Wrapper geloggt
        return None
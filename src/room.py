import time


class Room:
    """Represents a room or a zone in the Hue system."""

    def __init__(self, bridge, log, name, group_ids, **kwargs):
        """Initializes the Room object."""
        self.bridge = bridge
        self.log = log
        self.name = name
        self.group_ids = [int(gid) for gid in group_ids]
        self.last_command_time = 0

    def apply_state(self, state, command_throttle_s=1):
        """
        Sets the state for all light groups in the room.
        """
        current_time = time.time()
        if current_time - self.last_command_time < command_throttle_s:
            self.log.debug(f"Room '{self.name}': Command throttled. Skipping.")
            return

        self.log.debug(
            f"Room '{self.name}': Setting groups {self.group_ids} to state: {state}"
        )
        try:
            self.bridge.set_group(self.group_ids, state)
            self.last_command_time = current_time
        except Exception as e:
            self.log.error(f"Failed to set state for room '{self.name}': {e}")

    def is_any_light_on(self):
        """
        Prüft, ob irgendein Licht in dieser Gruppe aktuell eingeschaltet ist.
        """
        if not self.group_ids:
            return False
        try:
            group_state = self.bridge.get_group(self.group_ids[0])
            if group_state and "state" in group_state:
                return group_state["state"].get("any_on", False)
        except Exception as e:
            self.log.error(
                f"Konnte den Status für Gruppe {self.group_ids[0]} nicht abrufen: {e}"
            )
            return None
        return False

    def get_current_state(self):
        """
        Holt den aktuellen, detaillierten Lichtzustand der Gruppe von der Bridge.
        """
        if not self.group_ids:
            return None
        try:
            group_action = self.bridge.get_group(self.group_ids[0], "action")
            if group_action:
                # Wir geben nur die relevanten Schlüssel zurück, um den Vergleich zu vereinfachen
                relevant_keys = ["on", "bri", "ct", "hue", "sat"]
                return {
                    key: group_action.get(key)
                    for key in relevant_keys
                    if key in group_action
                }
        except Exception as e:
            self.log.error(
                f"Konnte den 'action'-Zustand für Gruppe {self.group_ids[0]} nicht abrufen: {e}"
            )
            return None
        return None
